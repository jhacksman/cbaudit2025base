# Pendle Boros Attack Surface Analysis

## Overview

This document maps the attack surface of the Pendle Boros protocol, identifying potential vulnerability vectors, trust assumptions, and high-priority audit areas.

## 1. Margin System Manipulation

### 1.1 Cross-Margin Calculation Errors

**Attack Vectors:**
- Incorrect aggregation of position values across markets
- Rounding errors in margin requirement calculations
- Race conditions between settlement and margin checks

**Relevant Code:**
- `MarginManager._settleProcess()` - Iterates through entered markets
- `MarginManager._isEnoughIMStrict()` - IM validation
- `MarginManager._isHRAboveThres()` - Health ratio calculation

**Mitigations in Place:**
- Strict IM checks after cash-reducing operations
- Critical health checks after position changes
- Settlement before margin validation

**Residual Risks:**
- Complex multi-market scenarios may have edge cases
- Integer overflow/underflow in margin calculations

### 1.2 Isolated Margin Bypass

**Attack Vectors:**
- Transferring cash between cross and isolated accounts to avoid margin requirements
- Exploiting timing between cash transfer and margin check

**Relevant Code:**
- `TradeModule.cashTransfer()` - Cash transfer between accounts
- `MarketHubEntry.cashTransfer()` - Underlying transfer logic

**Mitigations:**
- `_checkIMStrict()` called after transfers
- Account type validation

### 1.3 Market Entry/Exit Manipulation

**Attack Vectors:**
- Entering market without sufficient minimum cash
- Exiting market while still having positions
- Bypassing market entrance fee

**Relevant Code:**
- `MarginManager._validateMarketEntry()` - Entry validation
- `MarketHubEntry.exitMarket()` - Exit validation

**Mitigations:**
- Minimum cash requirement checked on first market entry
- Position emptiness check on exit (unless matured)
- One-time entrance fee tracked per market

## 2. Liquidation Logic

### 2.1 Incorrect Liquidation Eligibility

**Attack Vectors:**
- Liquidating healthy positions
- Self-liquidation for profit
- Manipulating health ratio calculation

**Relevant Code:**
- `MarketHubEntry.liquidate()` - Main liquidation entry
- `MarketEntry.liquidate()` - Market-level liquidation
- `MarginManager._settleProcessGetHR()` - Health ratio calculation

**Mitigations:**
- Health ratio validation before liquidation
- Liquidator cannot be same as violator
- Critical health threshold (`critHR`) enforcement

**Residual Risks:**
- Oracle manipulation affecting position values
- Timing attacks around settlement

### 2.2 Liquidation Incentive Manipulation

**Attack Vectors:**
- Extracting excessive value through liquidation fees
- Partial liquidation gaming

**Relevant Code:**
- `MarketEntry._calcLiqTradeAft()` - Liquidation trade calculation
- Liquidation fee rate configuration

### 2.3 Force Deleverage Abuse

**Attack Vectors:**
- Triggering force deleverage inappropriately
- Manipulating deleverage nonce

**Relevant Code:**
- `MarketRiskManagement.forceDeleverage()` - Force deleverage
- `MarketEntry._incDelevLiqNonce()` - Nonce increment

## 3. AMM Vulnerabilities

### 3.1 Implied Rate Manipulation

**Attack Vectors:**
- Large trades to manipulate implied rate
- Oracle rate manipulation through trading patterns
- Exploiting time-weighted average calculation

**Relevant Code:**
- `BaseAMM._calcOracleImpliedRateInternal()` - Oracle rate calculation
- `FixedWindowObservationLib.calcCurrentOracleRate()` - TWAP calculation
- `BaseAMM._updateOracle()` - Oracle state update

**Mitigations:**
- Fixed window observation for oracle rate
- Rate bounds (`minAbsRate`, `maxAbsRate`)
- Cut-off timestamp before maturity

**Residual Risks:**
- Window manipulation through strategic trading
- Flash loan attacks on implied rate

### 3.2 LP Token Manipulation

**Attack Vectors:**
- First depositor attack (donation attack)
- Inflation attack on LP tokens
- Manipulating LP value through position changes

**Relevant Code:**
- `BaseAMM.mintByBorosRouter()` - LP minting
- `BaseAMM.burnByBorosRouter()` - LP burning
- `BOROS20` - LP token implementation

**Mitigations:**
- Minimum liquidity locked to `ACCOUNT_ONE` (10^6)
- Total supply cap enforcement
- Negative cash check on mint

### 3.3 AMM State Desynchronization

**Attack Vectors:**
- Desync between AMM state and market position
- Exploiting withdraw-only mode transitions

**Relevant Code:**
- `BaseAMM._isWithdrawOnly()` - Checks delevLiqNonce
- `BaseAMM._writeState()` - State persistence

## 4. Oracle Security

### 4.1 FIndex Oracle Manipulation

**Attack Vectors:**
- Submitting invalid floating index deltas
- Timing attacks on epoch boundaries
- Keeper compromise

**Relevant Code:**
- `FIndexOracle.updateFloatingIndex()` - Index update
- `FIndexOracle._calcUpdateTime()` - Timing validation
- `FIndexOracle._calcNewFIndex()` - New index calculation

**Mitigations:**
- Keeper-only updates
- Epoch boundary validation
- Max update delay enforcement

**Residual Risks:**
- Keeper key compromise
- Delayed updates affecting settlement

### 4.2 Funding Rate Verification Bypass

**Attack Vectors:**
- Submitting invalid Chainlink reports
- Exploiting verification fee limits
- Cross-source inconsistency

**Relevant Code:**
- `FundingRateVerifier.updateWithChainlink()` - Chainlink verification
- `FundingRateVerifier.updateWithChaosLabs()` - Chaos Labs verification
- `FundingRateVerifier.manualUpdate()` - Manual override

**Mitigations:**
- Multiple oracle sources
- Verification fee limits
- `onlyAuthorized` access control

**Residual Risks:**
- Manual update abuse by authorized parties
- Oracle source disagreement handling

### 4.3 Stale Oracle Data

**Attack Vectors:**
- Trading with stale FIndex data
- Exploiting delayed oracle updates

**Relevant Code:**
- `FIndexOracle.isDueForUpdateNow()` - Staleness check
- `maxUpdateDelay` configuration

## 5. Access Control Vulnerabilities

### 5.1 Agent Permission Escalation

**Attack Vectors:**
- Agent performing unauthorized operations
- Expired agent still executing trades
- Agent approval manipulation

**Relevant Code:**
- `AuthModule.agentExecute()` - Agent execution
- `AuthModule._checkAgentAllowedToCall()` - Selector whitelist
- `AuthModule._approveAgent()` - Agent approval

**Mitigations:**
- Explicit selector whitelist for agent calls
- Expiry timestamp enforcement
- Nonce-based replay protection

**Residual Risks:**
- Whitelist may include dangerous selectors
- Expiry check timing edge cases

### 5.2 Relayer Trust

**Attack Vectors:**
- Malicious relayer censoring transactions
- Relayer front-running user orders
- Signature replay across chains

**Relevant Code:**
- `AuthBase.onlyRelayer` modifier
- Signature verification in AuthModule

**Mitigations:**
- Nonce-based replay protection
- Expiry timestamps on messages
- Chain ID in signature domain

### 5.3 Access Controller Misconfiguration

**Attack Vectors:**
- Granting excessive permissions
- Removing critical permissions
- Admin key compromise

**Relevant Code:**
- `PendleAccessController.setAllowedAddress()` - Permission setting
- `PendleAccessController.canCall()` - Permission check

## 6. Withdrawal Cooldown Bypass

### 6.1 Cooldown Timing Attacks

**Attack Vectors:**
- Manipulating personal cooldown settings
- Exploiting cooldown calculation edge cases
- Flash loan + cooldown interaction

**Relevant Code:**
- `MarketHubEntry.requestVaultWithdrawal()` - Request initiation
- `MarketHubEntry.finalizeVaultWithdrawal()` - Finalization
- `_getPersonalCooldown()` - Cooldown retrieval

**Mitigations:**
- Global cooldown minimum
- Timestamp-based validation
- Anyone can finalize (no griefing)

**Residual Risks:**
- Cooldown may be insufficient for large exploits
- Personal cooldown manipulation by admin

### 6.2 Withdrawal Amount Manipulation

**Attack Vectors:**
- Inflating withdrawal amount through exploits
- Canceling and re-requesting to reset cooldown

**Relevant Code:**
- `MarketHubEntry.cancelVaultWithdrawal()` - Cancellation
- Withdrawal struct tracking

## 7. Order Book Vulnerabilities

### 7.1 Order Matching Manipulation

**Attack Vectors:**
- Front-running order placement
- Manipulating match rate
- Tick-level manipulation

**Relevant Code:**
- `MarketOrderAndOtc.orderAndOtc()` - Order execution
- `CoreOrderUtils` - Order matching logic
- Tick-based order book implementation

**Mitigations:**
- Desired match rate validation
- Strict cancel option
- TIF (Time-in-Force) enforcement

### 7.2 OTC Trade Exploitation

**Attack Vectors:**
- Unfavorable OTC trade execution
- OTC fee manipulation
- Counter-party manipulation

**Relevant Code:**
- OTC trade handling in `MarketOrderAndOtc`
- OTC fee calculation

### 7.3 Order Cancellation Issues

**Attack Vectors:**
- Canceling orders during matching
- Force cancel abuse
- Nonce manipulation

**Relevant Code:**
- `MarketEntry.cancel()` - Order cancellation
- `CancelData` struct handling

## 8. Deposit Box Security

### 8.1 External Swap Exploitation

**Attack Vectors:**
- Malicious swap router draining funds
- Approval not cleared after swap
- Reentrancy through swap callback

**Relevant Code:**
- `DepositBox.approveAndCall()` - External call execution
- `DepositModule._swapForDeposit()` - Swap orchestration

**Mitigations:**
- Approval reset to 0 after call
- Balance checks before/after swap
- Manager-only access

**Residual Risks:**
- Malicious swap router could steal approved tokens
- Native token handling edge cases

### 8.2 Deposit Box Ownership

**Attack Vectors:**
- Unauthorized access to deposit box
- Box ID collision

**Relevant Code:**
- `DepositBoxFactory.deployDepositBox()` - Box deployment
- `DepositBox.initialize()` - Ownership setting

## 9. Incentive Distribution

### 9.1 Merkle Proof Manipulation

**Attack Vectors:**
- Invalid proof acceptance
- Double claiming
- Merkle root manipulation

**Relevant Code:**
- `MultiTokenMerkleDistributor.claim()` - Claim execution
- `_verifyMerkleData()` - Proof verification

**Mitigations:**
- Standard OpenZeppelin MerkleProof
- Claimed amount tracking
- Admin-only root updates

### 9.2 Verified Amount Exploitation

**Attack Vectors:**
- Verify then claim race condition
- Stale verification exploitation

**Relevant Code:**
- `MultiTokenMerkleDistributor.verify()` - Pre-verification
- `MultiTokenMerkleDistributor.claimVerified()` - Verified claim

## 10. Initialization and Upgrade Risks

### 10.1 Uninitialized Proxy

**Attack Vectors:**
- Calling initialize on implementation
- Re-initialization attacks

**Relevant Code:**
- `_disableInitializers()` in constructors
- `initializer` modifier usage

**Mitigations:**
- Initializers disabled in constructors
- OpenZeppelin Initializable pattern

### 10.2 Upgrade Vulnerabilities

**Attack Vectors:**
- Storage collision on upgrade
- Logic contract takeover
- Upgrade to malicious implementation

**Relevant Code:**
- TransparentUpgradeableProxy pattern
- Beacon proxy for markets

## Trust Assumptions

### External Dependencies

| Dependency | Trust Level | Risk |
|------------|-------------|------|
| Chainlink Data Streams | High | Oracle manipulation, downtime |
| Chaos Labs Oracle | High | Data accuracy, availability |
| External Swap Routers | Medium | Malicious routing, MEV |
| Arbitrum L2 | High | Sequencer downtime, reorgs |

### Internal Roles

| Role | Trust Level | Capabilities |
|------|-------------|--------------|
| DEFAULT_ADMIN | Critical | Full system control |
| Keeper | High | Oracle updates |
| Relayer | Medium | Transaction submission |
| Agent | Low | Limited trading operations |

## High-Priority Audit Focus Areas

1. **Margin Calculation Edge Cases** - Complex multi-market scenarios
2. **AMM Math Precision** - Implied rate and LP calculations
3. **Oracle Update Timing** - Epoch boundary handling
4. **Withdrawal Cooldown** - Bypass scenarios
5. **Agent Permission Boundaries** - Selector whitelist completeness
6. **Deposit Box External Calls** - Reentrancy and approval handling
7. **Liquidation Incentives** - Economic soundness
8. **Cross-Account Cash Transfers** - Margin check ordering

## Attack Scenarios

### Scenario 1: Flash Loan Margin Manipulation

1. Attacker takes flash loan
2. Deposits to inflate cash balance
3. Opens large leveraged position
4. Manipulates market price
5. Withdraws profit (subject to cooldown)
6. Repays flash loan

**Mitigation:** Withdrawal cooldown limits effective extraction to ~20% of exploitable amount.

### Scenario 2: Oracle Manipulation Attack

1. Attacker identifies stale FIndex oracle
2. Opens position based on outdated rate
3. Oracle updates with large delta
4. Position becomes profitable
5. Closes position for profit

**Mitigation:** Max update delay limits staleness window.

### Scenario 3: Agent Privilege Escalation

1. User approves agent for trading
2. Agent discovers vulnerability in whitelisted function
3. Agent extracts funds through unexpected interaction
4. User's funds compromised

**Mitigation:** Strict selector whitelist, but completeness is critical.

### Scenario 4: AMM LP Donation Attack

1. Attacker is first LP with small deposit
2. Donates large amount to inflate share price
3. Subsequent LPs receive fewer shares
4. Attacker burns shares for profit

**Mitigation:** Minimum liquidity (10^6) locked to dead address.
