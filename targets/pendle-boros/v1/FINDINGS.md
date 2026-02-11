# Pendle Boros Security Findings

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 3 |
| Medium | 5 |
| Low | 4 |
| Informational | 3 |

## Critical Findings

### C-01: Deposit Box External Call Can Drain Approved Tokens

**Location:** `contracts/deposit/DepositBox.sol:39-50`

**Description:**
The `approveAndCall` function in DepositBox approves an external router (`call.approveTo`) for the full `call.amount` before making an external call to `call.callTo`. If the swap router is malicious or compromised, it can transfer the approved tokens to any address during the external call, before the approval is reset to 0.

```solidity
function approveAndCall(
    ApprovedCall memory call,
    address nativeRefund
) external payable onlyManager returns (bytes memory result) {
    // ...
    _approveForExtRouter(call.token, call.approveTo, call.amount);  // Approval granted
    result = call.callTo.functionCallWithValue(call.data, nativeAmount + nativeFee);  // External call
    _approveForExtRouter(call.token, call.approveTo, 0);  // Approval reset (too late if malicious)
    // ...
}
```

The `DepositModule._swapForDeposit` function allows user-specified `swapApprove` and `swapExtRouter` addresses in the signed message, meaning a user could be tricked into signing a message with a malicious router.

**Impact:**
- Complete loss of user funds in deposit box
- Attacker can drain any token approved during the swap
- Severity: Critical (direct fund loss, high likelihood with phishing)

**Recommendation:**
1. Implement a whitelist of approved swap routers
2. Validate that `swapApprove` and `swapExtRouter` are in the whitelist before execution
3. Consider using a pull pattern instead of approval

---

## High Findings

### H-01: Agent Selector Whitelist Allows Cash Transfer to Arbitrary Accounts

**Location:** `contracts/core/router/modules/AuthModule.sol:207-224`

**Description:**
The `_checkAgentAllowedToCall` function whitelists `ITradeModule.cashTransfer.selector`, which allows agents to transfer cash between accounts. While the `cashTransfer` function validates that both accounts have the same `tokenId`, an agent could potentially transfer funds from the user's isolated margin account to the cross-margin account, affecting margin calculations.

```solidity
function _checkAgentAllowedToCall(bytes memory callData) internal pure {
    bytes4 selector = bytes4(callData);
    require(
        selector == ITradeModule.cashTransfer.selector ||  // Allows cash transfer
        // ... other selectors
    );
}
```

The `cashTransfer` function in TradeModule:
```solidity
function cashTransfer(CashTransferReq memory req) external setNonAuth {
    MarketCache memory cache = _getMarketCache(req.marketId);
    MarketAcc user = _account().toIsolated(cache.tokenId, req.marketId);
    _MARKET_HUB.cashTransfer(user.toCross(), user, req.signedAmount);
}
```

**Impact:**
- Agent can manipulate user's margin distribution
- Could lead to unexpected liquidations
- Severity: High (fund manipulation, medium likelihood)

**Recommendation:**
1. Review whether agents should have cash transfer permissions
2. Consider adding explicit user consent for cash transfers
3. Implement per-operation limits for agent actions

### H-02: FIndex Oracle Manual Update Bypasses All Verification

**Location:** `contracts/verifier/FundingRateVerifier.sol:98-100`

**Description:**
The `manualUpdate` function allows authorized parties to update the FIndex oracle with arbitrary values, bypassing all verification from Chainlink, Chaos Labs, or Pendle oracles.

```solidity
function manualUpdate(int112 fundingRate, uint32 fundingTimestamp) external onlyAuthorized {
    IFIndexOracle(FINDEX_ORACLE).updateFloatingIndex(fundingRate, fundingTimestamp);
}
```

While this is intended as an emergency mechanism, it creates a significant trust assumption. A compromised or malicious authorized party could submit fraudulent funding rates to manipulate settlements.

**Impact:**
- Arbitrary funding rate manipulation
- Settlement manipulation affecting all positions
- Severity: High (systemic risk, requires privileged access)

**Recommendation:**
1. Implement a timelock on manual updates
2. Require multi-sig for manual updates
3. Add bounds checking even for manual updates
4. Emit distinct events for manual vs verified updates

### H-03: AMM Oracle Rate Can Be Manipulated Through Strategic Trading

**Location:** `contracts/core/amm/BaseAMM.sol:203-225`

**Description:**
The AMM's oracle implied rate uses a fixed-window time-weighted average. An attacker can manipulate this rate by executing large trades just before the observation window boundary, then trading back after the window shifts.

```solidity
function _calcOracleImpliedRateInternal(
    uint32 blockTimestamp
) internal view returns (int128 _oracleImpliedRate, uint32 _observationWindow) {
    int128 _prevOracleImpliedRate = _storage.prevOracleImpliedRate;
    uint32 _lastTradedTime = _storage.lastTradedTime;
    int128 _lastTradedRate = _calcImpliedRate().Int128();

    _observationWindow = _storage.oracleImpliedRateWindow;

    _oracleImpliedRate = FixedWindowObservationLib.calcCurrentOracleRate(
        _prevOracleImpliedRate,
        _observationWindow,
        _lastTradedTime,
        _lastTradedRate,
        blockTimestamp
    );
}
```

The `_updateOracle` is called at the start of each trade via `onlyRouterWithOracleUpdate`, meaning the attacker's manipulation trade itself updates the oracle state.

**Impact:**
- Oracle rate manipulation affecting external integrations
- Potential arbitrage opportunities
- Severity: High (economic exploit, medium likelihood)

**Recommendation:**
1. Implement manipulation-resistant TWAP (e.g., geometric mean)
2. Add rate change limits per block
3. Consider using external oracle for rate verification

---

## Medium Findings

### M-01: Withdrawal Cooldown Can Be Reset by Cancel and Re-request

**Location:** `contracts/core/markethub/MarketHubEntry.sol:114-138`

**Description:**
A user can cancel their withdrawal request and immediately re-request, effectively resetting the cooldown timer. While this doesn't bypass the cooldown, it could be used to delay liquidation or extend the window for exploiting inflated balances.

```solidity
function cancelVaultWithdrawal(address root, TokenId tokenId) external onlyRouter {
    // ... returns funds to cash balance
    user.unscaled = 0;
    _withdrawal[root][tokenId] = user;
}

function requestVaultWithdrawal(address root, TokenId tokenId, uint256 unscaled) external onlyRouter {
    // ... starts new cooldown
    user.start = uint32(block.timestamp);
    _withdrawal[root][tokenId] = user;
}
```

**Impact:**
- Cooldown timer manipulation
- Extended exploit windows
- Severity: Medium (timing manipulation)

**Recommendation:**
1. Track cumulative withdrawal amounts
2. Implement minimum time between cancel and re-request
3. Consider progressive cooldown for repeated requests

### M-02: Market Entry Fee Can Be Avoided Through Matured Markets

**Location:** `contracts/core/markethub/MarginManager.sol:45-55`

**Description:**
The market entrance fee is only charged once per market (`hasEnteredMarketBefore`). However, the exit validation allows exiting matured markets even with positions. A user could potentially exploit this to avoid fees in edge cases.

```solidity
function _addMarketToUser(MarketAcc user, MarketId marketId) internal returns (uint128 entranceFee) {
    if (!acc[user].hasEnteredMarketBefore[marketId]) {
        acc[user].hasEnteredMarketBefore[marketId] = true;
        entranceFee = cashFeeData[user.tokenId()].marketEntranceFee;
        _transferToTreasury(user, entranceFee);
    }
    _addToEnteredMarkets(user, marketId);
}
```

**Impact:**
- Minor fee avoidance
- Severity: Medium (economic impact, low likelihood)

**Recommendation:**
1. Review fee logic for matured market edge cases
2. Consider per-entry fees instead of one-time fees

### M-03: Liquidation Health Ratio Check Uses Stale Settlement Data

**Location:** `contracts/core/markethub/MarketHubEntry.sol:273-295`

**Description:**
In the `liquidate` function, the violator's health ratio is calculated before the liquidation trade is executed. If market conditions change between the check and execution (e.g., through a concurrent transaction), the liquidation might execute against a now-healthy position.

```solidity
function liquidate(...) external onlyAuthorized returns (...) {
    // ...
    int256 vioHealthRatio = _settleProcessGetHR(vio);  // Check before liquidation
    
    address market = _marketIdToAddrRaw(marketId);
    LiqResult memory res = IMarket(market).liquidate(liq, vio, sizeToLiq, vioHealthRatio, critHR);
    // ...
}
```

**Impact:**
- Liquidation of healthy positions in race conditions
- Severity: Medium (requires specific timing)

**Recommendation:**
1. Re-validate health ratio after liquidation trade
2. Implement atomic health check and liquidation

### M-04: Simulation Function Can Be Called in View Context

**Location:** `contracts/core/markethub/MarketHubEntry.sol:178-181`

**Description:**
The `simulateTransfer` function checks `tx.origin == address(0)` to restrict to simulation context. However, this check can be bypassed in certain scenarios (e.g., some L2 peculiarities or future EVM changes).

```solidity
function simulateTransfer(MarketAcc user, int256 amount) external {
    require(tx.origin == address(0), Err.MMSimulationOnly());
    acc[user].cash += amount;
}
```

**Impact:**
- Potential state manipulation if bypass found
- Severity: Medium (depends on EVM behavior)

**Recommendation:**
1. Use a dedicated simulation contract
2. Add additional access control
3. Consider using staticcall detection instead

### M-05: AMM Minimum Liquidity May Be Insufficient for High-Value Markets

**Location:** `contracts/core/amm/BaseAMM.sol:50, 97-98`

**Description:**
The minimum liquidity is set to `10^6` (1 million wei), which is locked to `ACCOUNT_ONE`. For high-value tokens or markets, this may not provide sufficient protection against first-depositor attacks.

```solidity
uint256 private constant _MINIMUM_LIQUIDITY = 10 ** 6;

// In constructor:
_mint(params.seeder, initialState.totalLp - _MINIMUM_LIQUIDITY);
_mint(ACCOUNT_ONE, _MINIMUM_LIQUIDITY);
```

**Impact:**
- First depositor attack in high-value markets
- LP share manipulation
- Severity: Medium (economic exploit, specific conditions)

**Recommendation:**
1. Scale minimum liquidity based on token decimals
2. Consider dynamic minimum based on market value
3. Implement virtual liquidity pattern

---

## Low Findings

### L-01: Missing Zero Address Validation in Constructor Parameters

**Location:** Multiple contracts

**Description:**
Several constructors accept address parameters without validating they are non-zero:
- `Router.sol` - module addresses
- `MarketHubEntry.sol` - permission controller, factory, router
- `FundingRateVerifier.sol` - oracle addresses

**Impact:**
- Deployment with invalid addresses
- Severity: Low (deployment-time issue)

**Recommendation:**
Add `require(addr != address(0))` checks for critical addresses.

### L-02: FundingRateOracle Owner Can Set Arbitrary Rates Within Bounds

**Location:** `contracts/oracle/FundingRateOracle.sol:28-41`

**Description:**
The `updateFundingRate` function only validates that the rate is within `minFundingRate` and `maxFundingRate` bounds. The owner can set any rate within these bounds without external verification.

```solidity
function updateFundingRate(int112 fundingRate, uint32 fundingTimestamp, uint32 epochDuration) external onlyOwner {
    require(fundingRate >= minFundingRate && fundingRate <= maxFundingRate, FundingRateOutOfBound());
    require(fundingTimestamp > latestUpdate.fundingTimestamp, FundingTimestampNotIncreasing());
    // ...
}
```

**Impact:**
- Rate manipulation within bounds
- Severity: Low (requires owner compromise)

**Recommendation:**
1. Implement rate change limits per update
2. Add timelock for significant rate changes

### L-03: No Upper Bound on Personal Cooldown

**Location:** `contracts/core/markethub/Storage.sol`

**Description:**
The personal cooldown can be set to arbitrarily high values by admin, potentially locking user funds indefinitely.

**Impact:**
- User fund lockup
- Severity: Low (requires admin action)

**Recommendation:**
Implement maximum cooldown limit.

### L-04: ETH Transfer in FundingRateVerifier Uses Low-Level Call

**Location:** `contracts/verifier/FundingRateVerifier.sol:108-111`

**Description:**
The `withdraw` function uses a low-level call for ETH transfer without checking the return data length.

```solidity
function withdraw(address receiver, uint256 amount) external onlyAuthorized {
    (bool success, ) = payable(receiver).call{value: amount}("");
    require(success, "ETH transfer failed");
}
```

**Impact:**
- Potential issues with contract receivers
- Severity: Low (edge case)

**Recommendation:**
Use OpenZeppelin's `Address.sendValue` or implement proper return data handling.

---

## Informational Findings

### I-01: Consider Using Custom Errors Consistently

**Description:**
The codebase uses a mix of custom errors (via `Err` library) and string error messages. Consistent use of custom errors would reduce gas costs and improve error handling.

**Location:** Various contracts

**Recommendation:**
Standardize on custom errors throughout the codebase.

### I-02: Magic Numbers in AMM Math

**Description:**
The AMM math contracts contain several magic numbers without clear documentation:
- Rate scaling factors
- Precision constants
- Time constants

**Location:** `PositiveAMMMath.sol`, `NegativeAMMMath.sol`

**Recommendation:**
Define named constants with documentation explaining their derivation.

### I-03: Missing NatSpec Documentation

**Description:**
Several public/external functions lack comprehensive NatSpec documentation, making it harder to understand intended behavior and security assumptions.

**Location:** Various contracts

**Recommendation:**
Add complete NatSpec documentation including `@param`, `@return`, and `@dev` tags for all public interfaces.

---

## Disclaimer

These findings are based on static code review of the Pendle Boros smart contracts. The severity ratings follow Cantina's guidelines and consider both technical impact and likelihood of exploitation. Some findings may require dynamic testing or formal verification to fully assess their exploitability.
