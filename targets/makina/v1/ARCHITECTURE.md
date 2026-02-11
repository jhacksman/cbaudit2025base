# Makina Protocol Architecture

## Overview

Makina is a cross-chain strategy execution protocol that enables operators to issue tokenized strategies with full DeFi composability. The protocol uses a hub-and-spoke architecture where a central Machine contract on the hub chain coordinates with Caliber execution engines deployed across multiple spoke chains.

## Core Architecture

```
                                    ┌─────────────────────────────────────────────────────────────┐
                                    │                      HUB CHAIN (Ethereum)                    │
                                    │                                                              │
    ┌──────────────┐               │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
    │   Users      │◄──────────────┼──┤  Depositor  │───►│   Machine   │◄───┤  Fee Manager    │  │
    │              │               │  └─────────────┘    │             │    └─────────────────┘  │
    │  Deposit/    │               │                     │  - Shares   │                         │
    │  Redeem      │               │  ┌─────────────┐    │  - AUM      │    ┌─────────────────┐  │
    │              │◄──────────────┼──┤  Redeemer   │───►│  - Bridges  │◄───┤ Oracle Registry │  │
    └──────────────┘               │  └─────────────┘    └──────┬──────┘    └─────────────────┘  │
                                    │                           │                                 │
                                    │                    ┌──────▼──────┐                         │
                                    │                    │ Hub Caliber │                         │
                                    │                    │  (Weiroll)  │                         │
                                    │                    └──────┬──────┘                         │
                                    │                           │                                 │
                                    │         ┌─────────────────┼─────────────────┐              │
                                    │         │                 │                 │              │
                                    │  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐      │
                                    │  │ Across V3   │   │ LayerZero   │   │   Other     │      │
                                    │  │ Adapter     │   │ V2 Adapter  │   │  Adapters   │      │
                                    │  └──────┬──────┘   └──────┬──────┘   └─────────────┘      │
                                    └─────────┼─────────────────┼──────────────────────────────────┘
                                              │                 │
                    ┌─────────────────────────┼─────────────────┼─────────────────────────┐
                    │                         │   CROSS-CHAIN   │                         │
                    │                         │    BRIDGES      │                         │
                    │                         │                 │                         │
                    └─────────────────────────┼─────────────────┼─────────────────────────┘
                                              │                 │
    ┌─────────────────────────────────────────┼─────────────────┼─────────────────────────────────┐
    │                    SPOKE CHAIN (Base, Arbitrum, etc.)     │                                 │
    │                                         │                 │                                 │
    │  ┌──────────────────┐            ┌──────▼─────────────────▼──────┐                         │
    │  │  Spoke Caliber   │◄───────────┤      Caliber Mailbox          │                         │
    │  │   (Weiroll)      │            │  - Bridge State Tracking      │                         │
    │  │                  │            │  - Accounting Data Provider   │                         │
    │  │  - Positions     │            └───────────────────────────────┘                         │
    │  │  - Swaps         │                                                                      │
    │  │  - DeFi Actions  │                                                                      │
    │  └──────────────────┘                                                                      │
    │                                                                                             │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Machine (src/machine/Machine.sol)

The Machine is the central hub contract that manages the tokenized strategy. It handles:

**State Management:**
- `_shareToken`: ERC20 share token representing user ownership
- `_accountingToken`: Base token for AUM calculations (e.g., USDC)
- `_lastTotalAum`: Cached total AUM across all chains
- `_spokeCalibersData`: Cross-chain caliber state including bridge tracking

**Key Functions:**
- `deposit()`: Mint shares for deposited assets (via Depositor)
- `redeem()`: Burn shares and return assets (via Redeemer)
- `updateTotalAum()`: Aggregate AUM from all calibers and update share price
- `transferToHubCaliber()`: Move funds to hub caliber for deployment
- `transferToSpokeCaliber()`: Bridge funds to spoke chains
- `updateSpokeCaliberAccountingData()`: Process Wormhole CCQ responses

**Share Price Calculation:**
```solidity
sharePrice = SHARE_TOKEN_UNIT * (aum + 1) / (supply + 10^decimalsOffset)
```

### 2. Caliber (src/caliber/Caliber.sol)

The Caliber is the execution engine that deploys assets to external DeFi protocols. It uses the Weiroll VM for flexible instruction execution.

**Key Features:**
- **Weiroll VM Integration**: Executes arbitrary DeFi interactions via command chaining
- **Merkle Proof Validation**: All instructions must be pre-approved via merkle tree
- **Position Tracking**: Maintains position values with staleness checks
- **Loss Protection**: Enforces maximum slippage on position changes

**Instruction Types:**
1. `ACCOUNTING`: Read-only position valuation (must not change state)
2. `MANAGEMENT`: Position entry/exit with value tracking
3. `HARVEST`: Claim rewards without spending base tokens
4. `FLASHLOAN_MANAGEMENT`: Flashloan-assisted position management

**Position Management Flow:**
```
1. Account for current position value
2. Validate instruction against merkle root
3. Execute management instruction via Weiroll
4. Re-account for new position value
5. Verify value change within loss tolerance
6. Update cooldown timestamp
```

### 3. CaliberMailbox (src/caliber/CaliberMailbox.sol)

The CaliberMailbox handles cross-chain communication between the hub Machine and spoke Calibers.

**Responsibilities:**
- Route incoming bridge transfers to the spoke Caliber
- Initiate outgoing bridge transfers from the spoke Caliber
- Track bridge state (`_bridgesIn`, `_bridgesOut`) for accounting
- Provide accounting data for Wormhole CCQ queries

**Bridge State Tracking:**
```
bridgesIn:  Funds received from hub (not yet acknowledged by hub)
bridgesOut: Funds sent to hub (not yet received by hub)
```

### 4. Bridge Adapters

**AcrossV3BridgeAdapter (src/bridge/adapters/AcrossV3BridgeAdapter.sol):**
- Integrates with Across V3 SpokePool
- Handles deposit and message relay
- Supports transfer cancellation and refunds

**LayerZeroV2BridgeAdapter (src/bridge/adapters/LayerZeroV2BridgeAdapter.sol):**
- Integrates with LayerZero V2 endpoint
- Supports composed messages for complex operations
- Configurable gas limits and options

**BridgeController (src/bridge/controller/BridgeController.sol):**
- Base contract for bridge coordination
- Manages pending/sent transfer states
- Enforces bridge loss limits

### 5. Governance (MakinaGovernable)

The protocol uses a multi-role governance model:

**Roles:**
| Role | Description | Powers |
|------|-------------|--------|
| Mechanic | Day-to-day operator | Execute positions, swaps, bridges |
| Security Council | Emergency responder | Recovery mode, slashing, bridge reset |
| Risk Manager | Risk parameter setter | Instruction root updates, share limits |
| Risk Manager Timelock | Timelocked risk changes | Fee rates, loss tolerances, thresholds |
| Accounting Agents | Accounting updaters | Position accounting (when restricted) |

**Operating Modes:**
- **Normal Mode**: Mechanic is operator, accounting open or restricted
- **Recovery Mode**: Security Council is operator, position increases blocked
- **Restricted Accounting Mode**: Only authorized agents can update accounting

### 6. Oracle Registry (src/registries/OracleRegistry.sol)

Aggregates Chainlink price feeds for token valuation.

**Features:**
- Two-hop feed routes (token -> intermediate -> quote)
- Staleness threshold enforcement
- Decimal normalization

**Price Calculation:**
```
price = 10^(quoteDecimals + quoteFeedsDecimals - baseFeedsDecimals) 
        * (baseFeed1 * baseFeed2) / (quoteFeed1 * quoteFeed2)
```

### 7. Security Module (src/security-module/SecurityModule.sol)

Provides a staking mechanism for protocol security.

**Features:**
- Lock machine shares to earn security module shares
- Cooldown period before withdrawal
- Slashing by Security Council
- Share price reflects slashing losses

**Slashing Constraints:**
- Maximum slashable percentage (`maxSlashableBps`)
- Minimum balance after slash (`minBalanceAfterSlash`)

## Cross-Chain Accounting

The protocol uses Wormhole Cross-Chain Queries (CCQ) to synchronize accounting data:

```
1. Spoke Caliber updates position values
2. CaliberMailbox exposes getSpokeCaliberAccountingData()
3. Wormhole guardians query spoke chains
4. Machine receives signed CCQ response
5. Machine validates signatures and updates spoke data
6. Total AUM aggregated from all sources
```

**AUM Components:**
- Hub Caliber net AUM
- Spoke Calibers net AUM (via CCQ)
- In-flight bridge transfers
- Idle tokens in Machine

## Fee System

**Fee Types:**
1. **Fixed Fee**: Time-based fee on total supply
2. **Performance Fee**: Fee on share price appreciation above watermark

**Fee Constraints:**
- `maxFixedFeeAccrualRate`: Maximum fixed fee per second
- `maxPerfFeeAccrualRate`: Maximum performance fee per second
- `feeMintCooldown`: Minimum time between fee mints

**Fee Distribution:**
Fees are minted as shares and distributed via the FeeManager contract.

## Swap Module (src/swap/SwapModule.sol)

Standalone module for executing swaps through external DEX aggregators.

**Features:**
- Configurable swapper targets (approval + execution)
- Only callable by registered Calibers
- Minimum output amount enforcement

## Pre-Deposit Vault (src/pre-deposit/PreDepositVault.sol)

Campaign-phase vault for capital onboarding before Machine launch.

**Features:**
- Accept deposits during campaign
- Migrate to Machine on launch
- Initial share distribution based on deposits

## Key Invariants

1. **Share Price Monotonicity**: Share price should not decrease except for slashing/losses
2. **Bridge State Consistency**: `machineBridgesIn <= caliberBridgesOut` and vice versa
3. **Position Freshness**: Positions must be accounted within staleness threshold
4. **Instruction Authorization**: All Weiroll instructions must pass merkle proof
5. **Loss Tolerance**: Position changes must be within configured loss bounds
6. **Recovery Mode Restrictions**: No position increases in recovery mode

## Upgrade Pattern

All core contracts use the ERC-7201 namespaced storage pattern for upgradeability:
```solidity
bytes32 private constant StorageLocation = keccak256(...) & ~bytes32(uint256(0xff));
```

Contracts are deployed behind proxies and managed via OpenZeppelin AccessManager.
