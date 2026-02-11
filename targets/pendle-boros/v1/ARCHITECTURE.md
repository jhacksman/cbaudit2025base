# Pendle Boros Protocol Architecture

## Overview

Pendle Boros is an on-chain interest rate swap marketplace built on Arbitrum. It combines a central limit order book (CLOB) with an automated market maker (AMM) to provide liquidity for interest rate derivative trading.

```
                                    +------------------+
                                    |     Router       |
                                    | (Diamond Proxy)  |
                                    +--------+---------+
                                             |
              +------------------------------+------------------------------+
              |              |               |               |              |
      +-------v------+ +-----v-----+ +-------v------+ +------v-----+ +------v------+
      | TradeModule  | | AuthModule| | DepositModule| | AMMModule  | | MiscModule  |
      +--------------+ +-----------+ +--------------+ +------------+ +-------------+
              |              |               |               |
              +------------------------------+---------------+
                                             |
                                    +--------v---------+
                                    |    MarketHub     |
                                    | (Margin Manager) |
                                    +--------+---------+
                                             |
              +------------------------------+------------------------------+
              |                              |                              |
      +-------v------+              +--------v--------+             +-------v------+
      |   Market 1   |              |    Market 2     |             |   Market N   |
      | (Order Book) |              |   (Order Book)  |             | (Order Book) |
      +-------+------+              +--------+--------+             +-------+------+
              |                              |                              |
      +-------v------+              +--------v--------+             +-------v------+
      |    AMM 1     |              |     AMM 2       |             |    AMM N     |
      | (Liquidity)  |              |   (Liquidity)   |             | (Liquidity)  |
      +--------------+              +-----------------+             +--------------+
```

## Core Components

### 1. Router (Diamond-like Proxy)

The Router serves as the main entry point for all user interactions. It implements a Diamond-like proxy pattern, delegating calls to specialized modules based on function selectors.

**Location:** `contracts/core/router/Router.sol`

**Modules:**
- `TradeModule` - Vault deposits/withdrawals, order placement, cash transfers
- `AuthModule` - Signature verification, agent management, relayer authentication
- `DepositModule` - Deposit box operations with external swap integration
- `AMMModule` - AMM liquidity operations (mint, burn, swap)
- `ConditionalModule` - Conditional order execution
- `MiscModule` - Utility functions

**Key Design:**
- Immutable module addresses set at construction
- Uses `RouterFacetLib` for selector-to-module resolution
- Supports both direct calls and relayer-mediated signed transactions

### 2. MarketHub (Central Margin Manager)

The MarketHub is the central accounting system managing user margins, market entries, and settlement across all markets.

**Location:** `contracts/core/markethub/MarketHubEntry.sol`

**Responsibilities:**
- User cash balance management (cross-margin and isolated)
- Market entry/exit validation
- Margin requirement enforcement (IM and MM)
- Settlement processing across markets
- Withdrawal cooldown enforcement
- Fee collection and treasury management

**Key State:**
```solidity
struct AccountState {
    int256 cash;                           // User's cash balance
    MarketId[] enteredMarkets;             // Markets user has positions in
    mapping(MarketId => bool) hasEnteredMarketBefore;
}

struct Withdrawal {
    uint224 unscaled;  // Amount requested
    uint32 start;      // Request timestamp
}
```

**Margin Types:**
- **Cross-Margin:** Single cash pool backing positions across multiple markets
- **Isolated Margin:** Dedicated cash pool for a specific market position

### 3. Market (Order Book)

Each Market represents a specific interest rate swap instrument with its own order book and position tracking.

**Location:** `contracts/core/market/MarketEntry.sol`

**Components:**
- `MarketEntry` - Main entry point with proxy delegation
- `MarketSetAndView` - Configuration and view functions
- `MarketOrderAndOtc` - Order matching and OTC trade execution
- `MarketRiskManagement` - Force deleverage and order purging

**Key Features:**
- Tick-based order book with configurable tick step
- Support for limit orders, market orders, and OTC trades
- Position settlement with funding rate accrual
- Liquidation support with configurable health ratios

**Order Types:**
- **Limit Orders:** Placed at specific ticks in the order book
- **Market Orders:** Execute against existing liquidity
- **OTC Trades:** Direct peer-to-peer trades with fee

### 4. AMM (Automated Market Maker)

The AMM provides passive liquidity for interest rate swaps using a specialized bonding curve.

**Location:** `contracts/core/amm/BaseAMM.sol`

**Variants:**
- `PositiveAMM` - For markets with positive implied rates
- `NegativeAMM` - For markets with negative implied rates

**Key State:**
```solidity
struct AMMStorage {
    uint128 minAbsRate;           // Minimum absolute rate
    uint128 maxAbsRate;           // Maximum absolute rate
    uint32 cutOffTimestamp;       // Trading cutoff before maturity
    uint32 oracleImpliedRateWindow;
    uint64 feeRate;
    uint256 totalSupplyCap;
    uint128 totalFloatAmount;     // Total floating exposure
    uint128 normFixedAmount;      // Normalized fixed amount
    uint32 lastTradedTime;
    int128 prevOracleImpliedRate;
}
```

**Operations:**
- `mintByBorosRouter` - Add liquidity (cash + size)
- `burnByBorosRouter` - Remove liquidity
- `swapByBorosRouter` - Trade against AMM

**Oracle Integration:**
- Maintains time-weighted average implied rate
- Uses fixed window observation for oracle rate calculation

### 5. FIndexOracle (Floating Index Oracle)

Tracks the cumulative floating index for settlement calculations.

**Location:** `contracts/core/market/findexOracle/FIndexOracle.sol`

**Key Concepts:**
- `FIndex` - Composite of timestamp, floating index, and fee index
- Epoch-based updates aligned with maturity
- Keeper-triggered updates with timing validation

**Update Flow:**
1. Keeper calls `updateFloatingIndex` with delta and timestamp
2. Oracle validates timing against epoch boundaries
3. New FIndex calculated and stored
4. Market notified via `updateFIndex`

### 6. FundingRateVerifier

Multi-source funding rate verification supporting multiple oracle providers.

**Location:** `contracts/verifier/FundingRateVerifier.sol`

**Supported Sources:**
- **Chainlink** - Data Streams with report verification
- **Chaos Labs** - On-chain oracle with update ID
- **Pendle** - Native Pendle oracle integration
- **Manual** - Admin override for emergencies

### 7. Access Control

Role-based access control using OpenZeppelin's AccessControlEnumerable.

**Location:** `contracts/core/roles/PendleAccessController.sol`

**Key Roles:**
- `DEFAULT_ADMIN_ROLE` - Full administrative access
- `DIRECT_MARKET_HUB_ROLE` - Direct MarketHub access (for Router)
- `INITIALIZER_ROLE` - Contract initialization

**Permission Model:**
- Function-level permissions via `(target, selector, caller)` mapping
- `onlyAuthorized` modifier checks `canCall` on permission controller

## Account System

### Account Types

```solidity
// Account encoding in MarketAcc (bytes32)
// [root address (20 bytes)][accountId (1 byte)][tokenId (2 bytes)][marketId (9 bytes)]

Account Types:
- Main (accountId = 0): Primary cross-margin account
- AMM (accountId = 1): AMM-specific account
- Subaccount (accountId = 2-255): User-created subaccounts
```

### Account Hierarchy

```
Root Address
    |
    +-- Main Account (Cross-Margin)
    |       |
    |       +-- Isolated Position (Market A)
    |       +-- Isolated Position (Market B)
    |
    +-- AMM Account
    |       |
    |       +-- AMM Position (Market A)
    |
    +-- Subaccount 2
    +-- Subaccount 3
    ...
```

## Trading Flow

### Order Placement

1. User signs order message
2. Relayer submits to Router via `AuthModule.agentExecute`
3. Router delegates to `TradeModule.placeSingleOrder`
4. TradeModule calls `MarketHub.orderAndOtc`
5. MarketHub validates margin and calls `Market.orderAndOtc`
6. Market matches orders and updates positions
7. MarketHub processes fees and margin checks

### Liquidation Flow

1. Liquidator identifies underwater position
2. Calls `MarketHub.liquidate` with violator and size
3. MarketHub validates liquidator's margin
4. Market executes liquidation trade
5. Positions transferred, fees collected
6. Both parties' margins rechecked

## Withdrawal Cooldown

To mitigate flash loan attacks and provide time for liquidations:

1. User requests withdrawal via `requestVaultWithdrawal`
2. Cooldown period starts (configurable per user)
3. After cooldown, anyone can call `finalizeVaultWithdrawal`
4. Funds transferred to user

**Key Protection:** Inflated balances from exploits are subject to cooldown, reducing effective funds at risk to ~20% of exploitable amount.

## Fee System

### Fee Types

1. **Market Entrance Fee** - One-time fee when first entering a market
2. **Taker Fee** - Fee on matched trades
3. **OTC Fee** - Fee on OTC trades
4. **Settlement Fee** - Accrued over time based on position size
5. **AMM Fee** - Swap fee on AMM trades

### Fee Flow

```
User Trade
    |
    v
+---+---+
| Fees  |
+---+---+
    |
    v
Treasury Cash (per token)
    |
    v
Admin Withdrawal
```

## Incentive Distribution

### Merkle-Based Distribution

**Location:** `contracts/distributor/MultiTokenMerkleDistributor.sol`

**Flow:**
1. Off-chain calculation of incentive amounts
2. Merkle root published on-chain
3. Users claim with proof
4. Optional pre-verification for gas optimization

## Key Invariants

1. **Margin Invariant:** User's total value (cash + position value) >= required margin
2. **Health Ratio:** For liquidation, HR = (value + cash) / margin < threshold
3. **AMM State:** totalFloatAmount and normFixedAmount must remain consistent
4. **FIndex Monotonicity:** FIndex timestamps must be strictly increasing
5. **Cooldown Enforcement:** Withdrawals must wait for cooldown period
6. **Market Entry:** Users must have minimum cash before entering markets

## Upgrade Pattern

- Router: TransparentUpgradeableProxy
- MarketHub: TransparentUpgradeableProxy with beacon pattern for markets
- Markets: Beacon proxy pattern
- AMMs: Direct deployment (immutable)
- AccessController: TransparentUpgradeableProxy

## External Dependencies

1. **OpenZeppelin Contracts** - Access control, proxy patterns, token standards
2. **Chainlink Data Streams** - Funding rate verification
3. **Chaos Labs Oracle** - Alternative funding rate source
4. **External Swap Routers** - For deposit box token swaps
