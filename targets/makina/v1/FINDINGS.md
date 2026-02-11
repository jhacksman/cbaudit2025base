# Makina Protocol Security Findings

## Summary

This document contains security findings from a comprehensive audit of the Makina protocol. Findings are categorized by severity according to Cantina's guidelines.

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High | 4 |
| Medium | 6 |
| Low | 5 |
| Informational | 3 |

---

## Critical Findings

### [C-01] Cross-Chain Accounting Data Can Be Stale During AUM Update

**Severity:** Critical

**Location:** `Machine.sol:406-418`, `MachineUtils.sol:38-60`

**Description:**

The `updateTotalAum()` function aggregates AUM from spoke calibers using cached CCQ data. However, there is a race condition where the CCQ data can become stale between the time it was last updated and when `updateTotalAum()` is called.

```solidity
// Machine.sol:406
function updateTotalAum() external override nonReentrant onlyAccountingAuthorized returns (uint256) {
    MachineStorage storage $ = _getMachineStorage();
    uint256 _lastTotalAum =
        MachineUtils.updateTotalAum($, IHubCoreRegistry(registry).oracleRegistry(), msg.sender != securityCouncil());
    // ...
}
```

The staleness check in `MachineUtils._getTotalAum()` uses `$._caliberStaleThreshold`:

```solidity
// MachineUtils.sol:239-244
if (
    currentTimestamp > spokeCaliberData.timestamp
        && currentTimestamp - spokeCaliberData.timestamp >= $._caliberStaleThreshold
) {
    revert Errors.CaliberAccountingStale(chainId);
}
```

**Impact:**

An attacker can exploit the time window between CCQ updates to manipulate share prices:

1. Wait for spoke caliber accounting to approach staleness threshold
2. Manipulate spoke chain positions (e.g., via flash loan)
3. Call `updateTotalAum()` on hub before new CCQ data arrives
4. Deposit at manipulated share price
5. New CCQ data arrives with correct (lower) values
6. Redeem for profit

**Recommendation:**

1. Reduce `caliberStaleThreshold` to minimize the attack window
2. Implement a "freshness bonus" that requires recent CCQ updates for deposits
3. Add a cooldown between CCQ updates and deposits

---

## High Findings

### [H-01] Share Price Manipulation via Donation Attack

**Severity:** High

**Location:** `Machine.sol:277-288`, `MachineUtils.sol:164-170`

**Description:**

The share price calculation uses the total AUM which includes idle token balances:

```solidity
// MachineUtils.sol:279-284
len = $._idleTokens.length();
for (uint256 i; i < len; ++i) {
    address token = $._idleTokens.at(i);
    totalAum +=
        _accountingValueOf(oracleRegistry, $._accountingToken, token, IERC20(token).balanceOf(address(this)));
}
```

An attacker can donate tokens directly to the Machine contract to inflate the AUM and manipulate the share price.

**Impact:**

1. Attacker donates tokens to Machine
2. AUM increases, share price increases
3. Attacker's existing shares are now worth more
4. Attacker redeems at inflated price

While the `maxSharePriceChangeRate` provides some protection, it may be insufficient for large donations or over extended time periods.

**Recommendation:**

1. Track expected balances separately from actual balances
2. Implement a "virtual balance" system that ignores unexpected donations
3. Add a donation cooldown that delays accounting of new tokens

---

### [H-02] Instruction Root Update Timelock May Be Insufficient

**Severity:** High

**Location:** `Caliber.sol:524-536`

**Description:**

The instruction root update mechanism uses a timelock, but the timelock duration is configurable and may be set too low:

```solidity
// Caliber.sol:524-536
function scheduleAllowedInstrRootUpdate(bytes32 newAllowedInstrRoot) external override onlyRiskManager {
    CaliberStorage storage $ = _getCaliberStorage();
    _updateAllowedInstrRoot();
    if ($._pendingTimelockExpiry != 0) {
        revert Errors.ActiveUpdatePending();
    }
    if (newAllowedInstrRoot == $._allowedInstrRoot) {
        revert Errors.SameRoot();
    }
    $._pendingAllowedInstrRoot = newAllowedInstrRoot;
    $._pendingTimelockExpiry = block.timestamp + $._timelockDuration;
    emit NewAllowedInstrRootScheduled(newAllowedInstrRoot, $._pendingTimelockExpiry);
}
```

If the Risk Manager is compromised, they can schedule a malicious instruction root. The timelock provides a window for guardians to cancel, but if the duration is too short, the attack may succeed.

**Impact:**

A compromised Risk Manager can add malicious instructions that drain funds from the Caliber.

**Recommendation:**

1. Enforce a minimum timelock duration at the protocol level
2. Require multi-sig approval for instruction root updates
3. Implement an emergency pause that blocks all instruction execution

---

### [H-03] Bridge State Tracking Can Desynchronize

**Severity:** High

**Location:** `Machine.sol:291-326`, `CaliberMailbox.sol:111-151`

**Description:**

The bridge state tracking between Machine and CaliberMailbox relies on coordinated updates that can become desynchronized:

```solidity
// Machine.sol:303-319
if (refund) {
    uint256 mOut = caliberData.machineBridgesOut.get(token);
    uint256 newMOut = mOut - inputAmount;
    (, uint256 cIn) = caliberData.caliberBridgesIn.tryGet(token);
    if (cIn > newMOut) {
        revert Errors.BridgeStateMismatch();
    }
    caliberData.machineBridgesOut.set(token, newMOut);
} else {
    (, uint256 mIn) = caliberData.machineBridgesIn.tryGet(token);
    uint256 newMIn = mIn + inputAmount;
    (, uint256 cOut) = caliberData.caliberBridgesOut.tryGet(token);
    if (newMIn > cOut) {
        revert Errors.BridgeStateMismatch();
    }
    caliberData.machineBridgesIn.set(token, newMIn);
}
```

The state is updated based on CCQ data from spoke chains, but there's a time delay between spoke state changes and hub awareness.

**Impact:**

1. Funds in transit may be double-counted or not counted at all
2. AUM calculations may be incorrect during bridge operations
3. Share price manipulation during bridge transfers

**Recommendation:**

1. Implement pessimistic accounting that excludes in-flight funds
2. Add a bridge transfer cooldown before AUM updates
3. Require explicit confirmation of bridge completion before accounting

---

### [H-04] Recovery Mode Grants Excessive Powers to Security Council

**Severity:** High

**Location:** `MakinaGovernable.sol:134-137`, `Machine.sol:618-639`

**Description:**

In recovery mode, the Security Council becomes the sole operator with extensive powers:

```solidity
// MakinaGovernable.sol:134-137
function isOperator(address user) public view override returns (bool) {
    MakinaGovernableStorage storage $ = _getMakinaGovernableStorage();
    return user == ($._recoveryMode ? $._securityCouncil : $._mechanic);
}
```

The Security Council can also reset bridge state, which could be used to cover tracks:

```solidity
// Machine.sol:618-639
function resetBridgingState(address token) external override onlySecurityCouncil {
    // ... resets all bridge tracking for a token
}
```

**Impact:**

A compromised Security Council can:
1. Enable recovery mode
2. Execute arbitrary operations as operator
3. Reset bridge state to hide fund movements
4. Disable recovery mode

**Recommendation:**

1. Require multi-sig for recovery mode activation
2. Implement time-delayed recovery mode with public notice
3. Add audit logging that cannot be reset
4. Limit Security Council powers even in recovery mode

---

## Medium Findings

### [M-01] Fee Calculation Can Be Manipulated via Timing

**Severity:** Medium

**Location:** `MachineUtils.sol:66-116`, `WatermarkFeeManager.sol:137-178`

**Description:**

The fee calculation depends on elapsed time and share price:

```solidity
// MachineUtils.sol:75-88
uint256 fixedFee = Math.min(
    IFeeManager(_feeManager).calculateFixedFee(currentShareSupply, elapsedTime),
    (currentShareSupply * elapsedTime).mulDiv($._maxFixedFeeAccrualRate, RATE_SCALE)
);
```

An attacker can time their deposits/redemptions around fee minting to minimize fees paid or maximize fees extracted.

**Impact:**

- Users can avoid paying their fair share of fees
- Fee recipients may receive less than expected

**Recommendation:**

1. Implement continuous fee accrual rather than discrete minting
2. Add randomness to fee mint timing
3. Pro-rate fees based on time-weighted share holdings

---

### [M-02] Swap Module Allows Arbitrary External Calls

**Severity:** Medium

**Location:** `SwapModule.sol:51-88`

**Description:**

The SwapModule executes arbitrary calls to configured execution targets:

```solidity
// SwapModule.sol:71-75
IERC20(order.inputToken).forceApprove(approvalTarget, order.inputAmount);
// solhint-disable-next-line
(bool success,) = executionTarget.call(order.data);
if (!success) {
    revert Errors.SwapFailed();
}
```

While the swapper targets are configured by governance, a malicious or compromised target could:
1. Steal approved tokens
2. Execute unexpected state changes
3. Reenter the protocol

**Impact:**

Fund loss if swapper targets are compromised or misconfigured.

**Recommendation:**

1. Implement a whitelist of allowed swap calldata patterns
2. Add reentrancy protection around swap calls
3. Verify output amounts match expected DEX behavior

---

### [M-03] Position Staleness Check Can Be Bypassed in Batch Operations

**Severity:** Medium

**Location:** `Caliber.sol:338-393`

**Description:**

In `accountForPositionBatch()`, positions in provided groups are marked as stale before processing:

```solidity
// Caliber.sol:351-360
for (uint256 i; i < groupsLen; ++i) {
    uint256 groupId = groupIds[i];
    if (groupId == 0) {
        revert Errors.ZeroGroupId();
    }
    uint256 groupLen = $._positionIdGroups[groupId].length();
    for (uint256 j; j < groupLen; ++j) {
        delete $._positionById[$._positionIdGroups[groupId].at(j)].lastAccountingTime;
    }
}
```

However, if a position is not in a provided group but has `groupId != 0`, it can be accounted for without the group staleness check:

```solidity
// Caliber.sol:371-376
if (groupId != 0 && $._positionIdGroups[groupId].length() > 1) {
    if (!_includesGroupId(groupIds, groupId)) {
        revert Errors.GroupIdNotProvided();
    }
}
```

This only checks if the group has more than 1 position.

**Impact:**

Grouped positions may be accounted for inconsistently, leading to incorrect AUM calculations.

**Recommendation:**

1. Always require group IDs for grouped positions regardless of group size
2. Add explicit validation that all positions in a group are accounted together

---

### [M-04] Oracle Feed Route Can Have Precision Loss

**Severity:** Medium

**Location:** `OracleRegistry.sol:59-90`

**Description:**

The price calculation involves multiple divisions that can accumulate precision loss:

```solidity
// OracleRegistry.sol:78-89
if (quoteTokenDecimals + quoteFRDecimalsSum < baseFRDecimalsSum) {
    return _getFeedPrice(baseFR.feed1) * _getFeedPrice(baseFR.feed2)
        / (
            (10 ** (baseFRDecimalsSum - quoteTokenDecimals - quoteFRDecimalsSum)) * _getFeedPrice(quoteFR.feed1)
                * _getFeedPrice(quoteFR.feed2)
        );
}

return (10 ** (quoteTokenDecimals + quoteFRDecimalsSum - baseFRDecimalsSum)).mulDiv(
    _getFeedPrice(baseFR.feed1) * _getFeedPrice(baseFR.feed2),
    _getFeedPrice(quoteFR.feed1) * _getFeedPrice(quoteFR.feed2)
);
```

**Impact:**

- Small but consistent pricing errors
- Potential for arbitrage between expected and actual prices

**Recommendation:**

1. Use higher precision intermediate calculations
2. Add rounding direction parameter for different use cases
3. Implement price sanity checks against external sources

---

### [M-05] Security Module Cooldown Can Be Front-Run

**Severity:** Medium

**Location:** `SecurityModule.sol:196-219`, `SecurityModule.sol:276-288`

**Description:**

When a slashing event is anticipated, stakers can front-run by starting a cooldown:

```solidity
// SecurityModule.sol:196-219
function startCooldown(uint256 shares, address receiver)
    external
    override
    nonReentrant
    returns (uint256, uint256, uint256)
{
    // ... starts cooldown with current asset value
    uint256 assets = convertToAssets(shares);
    uint256 maturity = block.timestamp + $._cooldownDuration;
    // ...
    $._pendingCooldowns[cooldownId] = PendingCooldown({shares: shares, maxAssets: assets, maturity: maturity});
}
```

The `maxAssets` is locked at cooldown start, protecting the withdrawer from slashing:

```solidity
// SecurityModule.sol:259
assets = assets < pc.maxAssets ? assets : pc.maxAssets;
```

**Impact:**

- Stakers can avoid slashing by front-running
- Remaining stakers bear disproportionate slashing burden

**Recommendation:**

1. Implement a slashing queue that affects pending cooldowns
2. Add a "slashing notice period" before actual slashing
3. Pro-rate slashing across all stakers including those in cooldown

---

### [M-06] Weiroll Delegatecall Inherits All Contract Permissions

**Severity:** Medium

**Location:** `Caliber.sol:969-977`

**Description:**

The Caliber executes Weiroll instructions via delegatecall:

```solidity
// Caliber.sol:973-976
bytes memory returndata =
    Address.functionDelegateCall(weirollVm, abi.encodeCall(IWeirollVM.execute, (commands, state)));
return abi.decode(returndata, (bytes[]));
```

This means the Weiroll VM has access to all of Caliber's storage and can make external calls with Caliber's identity.

**Impact:**

Malicious instructions could:
1. Modify Caliber storage directly
2. Approve tokens to arbitrary addresses
3. Call privileged functions on other contracts

**Recommendation:**

1. Use a separate execution context (call instead of delegatecall)
2. Implement storage access controls in Weiroll
3. Add post-execution invariant checks

---

## Low Findings

### [L-01] Missing Zero Address Checks in Setters

**Severity:** Low

**Location:** Multiple setter functions

**Description:**

Several setter functions don't validate against zero addresses:

- `Machine.setDepositor()`
- `Machine.setRedeemer()`
- `Machine.setFeeManager()`
- `MakinaGovernable.setMechanic()`

**Impact:**

Accidental misconfiguration could brick protocol functionality.

**Recommendation:**

Add zero address validation to all setter functions.

---

### [L-02] No Upper Bound on Staleness Thresholds

**Severity:** Low

**Location:** `Machine.setCaliberStaleThreshold()`, `Caliber.setPositionStaleThreshold()`

**Description:**

Staleness thresholds can be set to arbitrarily high values, effectively disabling staleness checks.

**Impact:**

Extremely stale data could be used for accounting.

**Recommendation:**

Implement maximum staleness threshold limits.

---

### [L-03] Bridge Adapter Cannot Be Updated

**Severity:** Low

**Location:** `BridgeController.sol:72-95`, `CaliberMailbox.sol:194-205`

**Description:**

Once a bridge adapter is set, it cannot be updated:

```solidity
// BridgeController.sol:79-81
if ($._bridgeAdapters[bridgeId] != address(0)) {
    revert Errors.BridgeAdapterAlreadyExists();
}
```

**Impact:**

If a bridge adapter has a vulnerability, it cannot be replaced without deploying new contracts.

**Recommendation:**

Allow bridge adapter updates with appropriate timelocks and safeguards.

---

### [L-04] Fee Split Rounding Can Leave Dust

**Severity:** Low

**Location:** `WatermarkFeeManager.sol:202-219`

**Description:**

Fee distribution uses `mulDiv` which can leave small amounts undistributed:

```solidity
// WatermarkFeeManager.sol:204
uint256 fee = mgmtFee.mulDiv($._mgmtFeeSplitBps[i], MAX_BPS);
```

**Impact:**

Small amounts of fees may accumulate in the Machine contract.

**Recommendation:**

Assign remaining dust to the last receiver or implement a sweep function.

---

### [L-05] Event Emission Missing for Some State Changes

**Severity:** Low

**Location:** Various

**Description:**

Some state changes don't emit events:
- `Caliber._invalidateGroupedPositions()`
- `MachineUtils._decodeAndMapBridgeAmounts()`

**Impact:**

Off-chain monitoring may miss important state changes.

**Recommendation:**

Add events for all significant state changes.

---

## Informational Findings

### [I-01] Consider Using OpenZeppelin's ReentrancyGuardUpgradeable

**Severity:** Informational

**Location:** `Machine.sol`, `Caliber.sol`

**Description:**

The contracts use non-upgradeable `ReentrancyGuard` which stores the lock status in a fixed storage slot. While this works, using `ReentrancyGuardUpgradeable` would be more consistent with the upgradeable pattern.

---

### [I-02] Magic Numbers Should Be Named Constants

**Severity:** Informational

**Location:** Various

**Description:**

Several magic numbers are used without named constants:
- `10_000` for basis points
- `1e18` for rate scaling
- Various timeout values

**Recommendation:**

Define named constants for all magic numbers.

---

### [I-03] Consider Adding NatSpec Documentation

**Severity:** Informational

**Location:** Various internal functions

**Description:**

Many internal functions lack NatSpec documentation, making the code harder to audit and maintain.

**Recommendation:**

Add comprehensive NatSpec documentation to all functions.

---

## Appendix: Known Issues (Out of Scope)

The following issues are known and explicitly out of scope per the bounty rules:

1. **January 2026 Oracle Manipulation Exploit** - The DUSD/USDC Curve pool manipulation attack has been addressed
2. **Centralization Risks** - The protocol acknowledges centralization in governance roles
3. **External Protocol Risks** - Risks from integrated DeFi protocols (Curve, Aave, etc.)
4. **Bridge Protocol Risks** - Risks inherent to Across V3 and LayerZero V2
