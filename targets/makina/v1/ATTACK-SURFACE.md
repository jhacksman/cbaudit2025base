# Makina Protocol Attack Surface

## Overview

This document maps the attack surface of the Makina protocol, identifying potential vulnerability categories, entry points, and trust assumptions that could be exploited.

## Attack Surface Categories

### 1. Share Price Manipulation

**Entry Points:**
- `Machine.deposit()` - Mints shares based on current share price
- `Machine.redeem()` - Burns shares based on current share price
- `Machine.updateTotalAum()` - Updates AUM and share price
- `MachineUtils.getSharePrice()` - Share price calculation

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Donation Attack | Donate tokens to inflate AUM before deposit | High |
| Oracle Manipulation | Manipulate price feeds to inflate/deflate AUM | Critical |
| Sandwich Attack | Front-run deposits/redemptions with AUM manipulation | High |
| First Depositor | Exploit rounding in initial share minting | Medium |
| Stale Accounting | Exploit outdated position values | High |

**Mitigations in Place:**
- `maxSharePriceChangeRate` limits price change per second
- Staleness thresholds on positions and caliber data
- Oracle staleness checks
- Virtual shares offset in price calculation

**Residual Risks:**
- Price change rate may be too permissive
- Staleness thresholds may allow significant drift
- Multi-block manipulation within rate limits

### 2. Cross-Chain State Synchronization

**Entry Points:**
- `Machine.updateSpokeCaliberAccountingData()` - CCQ response processing
- `CaliberMailbox.manageTransfer()` - Bridge transfer handling
- `BridgeAdapter.handleV3AcrossMessage()` - Incoming bridge messages

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Stale CCQ Data | Use outdated cross-chain accounting | High |
| Bridge State Desync | Exploit inconsistency between hub/spoke bridge tracking | High |
| Message Replay | Replay old CCQ responses | Medium |
| Wormhole Guardian Compromise | Forge CCQ signatures | Critical |
| Bridge Adapter Spoofing | Impersonate bridge adapter | Critical |

**Mitigations in Place:**
- Timestamp validation on CCQ responses
- Bridge state consistency checks in `_checkBridgeState()`
- Wormhole signature verification
- Bridge adapter registration checks

**Residual Risks:**
- Time window between CCQ query and processing
- Complex bridge state tracking may have edge cases
- Reliance on external bridge security

### 3. Weiroll Instruction Execution

**Entry Points:**
- `Caliber.managePosition()` - Execute management instructions
- `Caliber.accountForPosition()` - Execute accounting instructions
- `Caliber.harvest()` - Execute harvest instructions
- `Caliber.manageFlashLoan()` - Execute flashloan instructions

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Malicious Instruction Root | Compromise risk manager to add malicious instructions | Critical |
| Merkle Proof Collision | Find collision in instruction merkle tree | Low |
| State Manipulation | Manipulate Weiroll state between instructions | High |
| Reentrancy via External Call | Reenter during Weiroll execution | High |
| Instruction Type Confusion | Execute wrong instruction type | Medium |

**Mitigations in Place:**
- Merkle proof validation for all instructions
- Timelock on instruction root updates
- Instruction root guardians can cancel updates
- ReentrancyGuard on key functions
- Instruction type validation

**Residual Risks:**
- Timelock may be too short
- Delegatecall to Weiroll VM inherits all risks
- Complex state machine may have edge cases

### 4. Access Control Boundaries

**Entry Points:**
- All `restricted` functions (AccessManager controlled)
- Role-specific modifiers (`onlyMechanic`, `onlySecurityCouncil`, etc.)
- `MakinaGovernable` role management

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Role Escalation | Gain unauthorized role access | Critical |
| Mechanic Compromise | Malicious operator drains funds | Critical |
| Security Council Abuse | Abuse recovery mode powers | Critical |
| AccessManager Misconfiguration | Incorrect role assignments | High |
| Timelock Bypass | Circumvent timelocked operations | High |

**Mitigations in Place:**
- Separation of duties (Mechanic vs Security Council)
- Timelocks on sensitive parameter changes
- Recovery mode restrictions
- Multi-sig requirements (external)

**Residual Risks:**
- Single point of failure if key roles compromised
- Recovery mode grants extensive powers
- Complex role hierarchy may have gaps

### 5. Oracle Manipulation

**Entry Points:**
- `OracleRegistry.getPrice()` - Price feed queries
- `Caliber._accountingValueOf()` - Position valuation
- `MachineUtils._accountingValueOf()` - AUM calculation

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Flash Loan Price Manipulation | Manipulate spot prices via flash loans | Critical |
| Stale Price Exploitation | Use outdated prices for favorable trades | High |
| Feed Route Manipulation | Compromise intermediate price feeds | High |
| Decimal Precision Attacks | Exploit decimal handling edge cases | Medium |

**Known Exploit (Jan 2026):**
- DUSD/USDC Curve pool manipulation
- Flash loan attack on synchronous deposit
- $4.13M loss

**Mitigations in Place:**
- Chainlink aggregator feeds (not spot prices)
- Staleness threshold checks
- Negative price rejection

**Residual Risks:**
- Chainlink feeds can still be manipulated in extreme conditions
- Multi-hop pricing compounds errors
- New token integrations may have weak feeds

### 6. Bridge Security

**Entry Points:**
- `AcrossV3BridgeAdapter` - Across V3 integration
- `LayerZeroV2BridgeAdapter` - LayerZero V2 integration
- `BridgeController` - Transfer coordination

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Bridge Protocol Exploit | Exploit underlying bridge vulnerability | Critical |
| Message Forgery | Forge cross-chain messages | Critical |
| Transfer Cancellation Abuse | Exploit cancel/refund logic | High |
| Slippage Exploitation | Manipulate bridge output amounts | Medium |
| Stuck Funds | Cause funds to be stuck in bridge | Medium |

**Mitigations in Place:**
- `maxBridgeLossBps` limits acceptable slippage
- Transfer state tracking
- Authorization for incoming transfers
- Cooldown on outgoing transfers

**Residual Risks:**
- Reliance on external bridge security
- Complex state machine for transfer lifecycle
- Recovery requires Security Council intervention

### 7. Fee System Manipulation

**Entry Points:**
- `MachineUtils.manageFees()` - Fee calculation and minting
- `WatermarkFeeManager` - Fee distribution
- `Machine.setFeeManager()` - Fee manager configuration

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Fee Inflation | Manipulate AUM to inflate fees | Medium |
| Watermark Manipulation | Reset watermark to collect unearned fees | Medium |
| Fee Manager Compromise | Redirect fees to attacker | High |
| Timing Attacks | Exploit fee mint cooldown | Low |

**Mitigations in Place:**
- `maxFixedFeeAccrualRate` and `maxPerfFeeAccrualRate` caps
- `feeMintCooldown` prevents frequent minting
- Timelocked fee parameter changes

**Residual Risks:**
- Fee caps may still allow significant extraction
- Complex fee calculation may have edge cases

### 8. Security Module Attacks

**Entry Points:**
- `SecurityModule.lock()` - Stake machine shares
- `SecurityModule.startCooldown()` - Initiate withdrawal
- `SecurityModule.redeem()` - Complete withdrawal
- `SecurityModule.slash()` - Burn staked shares

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Slashing Front-run | Withdraw before slashing event | High |
| Share Price Manipulation | Exploit SM share price calculation | Medium |
| Cooldown Bypass | Circumvent cooldown period | High |
| Slashing Mode Abuse | Exploit slashing mode restrictions | Medium |

**Mitigations in Place:**
- Cooldown period before withdrawal
- `maxSlashableBps` limits slashing
- `minBalanceAfterSlash` ensures minimum stake
- Slashing mode blocks new locks

**Residual Risks:**
- Cooldown may be too short for slashing response
- Share price calculation similar to Machine (same risks)

### 9. Flashloan Integration

**Entry Points:**
- `Caliber.manageFlashLoan()` - Flashloan callback
- `FlashloanAggregator` - Flashloan routing

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Reentrancy via Flashloan | Reenter protocol during flashloan | High |
| Flashloan Callback Manipulation | Manipulate state during callback | High |
| Affected Token Bypass | Modify tokens not in affectedTokens list | Medium |

**Mitigations in Place:**
- `_isManagingFlashloan` flag prevents reentrancy
- `_managedPositionId` must match instruction
- Instruction type validation

**Residual Risks:**
- Complex interaction with position management
- Delegatecall execution may have unexpected effects

### 10. Initialization and Upgrade Risks

**Entry Points:**
- All `initialize()` functions
- Proxy upgrade mechanisms
- Factory deployment functions

**Attack Vectors:**

| Vector | Description | Severity |
|--------|-------------|----------|
| Uninitialized Proxy | Call initialize on uninitialized proxy | Critical |
| Storage Collision | Upgrade causes storage layout conflict | Critical |
| Factory Manipulation | Deploy malicious contracts via factory | High |
| Implementation Takeover | Initialize implementation directly | Medium |

**Mitigations in Place:**
- `_disableInitializers()` in constructors
- ERC-7201 namespaced storage
- Factory access controls

**Residual Risks:**
- Complex upgrade paths may introduce bugs
- New implementations may have vulnerabilities

## Trust Assumptions

### External Dependencies

| Dependency | Trust Level | Risk if Compromised |
|------------|-------------|---------------------|
| Wormhole Guardians | High | CCQ data forgery |
| Chainlink Oracles | High | Price manipulation |
| Across V3 | Medium | Bridge fund loss |
| LayerZero V2 | Medium | Bridge fund loss |
| External DeFi Protocols | Low | Position losses |

### Internal Roles

| Role | Trust Level | Risk if Compromised |
|------|-------------|---------------------|
| Security Council | Critical | Full protocol control |
| Risk Manager | High | Malicious instruction approval |
| Mechanic | High | Fund misallocation |
| Accounting Agents | Medium | Stale/incorrect accounting |

## High-Priority Audit Focus Areas

1. **Share Price Calculation** - Rounding, virtual shares, edge cases
2. **Cross-Chain State Sync** - CCQ validation, bridge state tracking
3. **Weiroll Execution** - Instruction validation, state manipulation
4. **Oracle Integration** - Price feed security, staleness handling
5. **Access Control** - Role boundaries, recovery mode powers
6. **Bridge Adapters** - Transfer lifecycle, refund handling
7. **Fee Calculation** - Overflow, precision, timing

## Attack Scenarios

### Scenario 1: Oracle Manipulation (Known Exploit Pattern)
```
1. Attacker takes flash loan
2. Manipulates price feed (e.g., Curve pool)
3. Deposits at inflated share price
4. Repays flash loan
5. Redeems at normal price for profit
```

### Scenario 2: Cross-Chain Accounting Desync
```
1. Attacker initiates bridge transfer from spoke
2. Delays CCQ update on hub
3. Exploits stale AUM for favorable deposit
4. CCQ updates with lower AUM
5. Redeems for profit
```

### Scenario 3: Instruction Root Manipulation
```
1. Attacker compromises Risk Manager
2. Schedules malicious instruction root
3. Waits for timelock expiry
4. Executes malicious instruction to drain funds
```

### Scenario 4: Recovery Mode Abuse
```
1. Security Council compromised
2. Enables recovery mode
3. Uses operator powers to drain funds
4. Resets bridge state to cover tracks
```
