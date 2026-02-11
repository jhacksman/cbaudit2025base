# Pendle Boros Security Audit Scope

## Program Overview

**Platform:** Cantina  
**Program Type:** Bug Bounty (Live)  
**Total Reward Pool:** $500,000 USD  
**Deposit Required:** $20  
**Start Date:** September 19, 2025  
**Status:** Active  
**Bounty URL:** https://cantina.xyz/bounties/aa966ff2-4740-49da-af4a-40f85e2e82a3

## Protocol Description

Pendle Boros is the first on-chain marketplace for interest rate swaps, built on Arbitrum. The protocol enables users to take long or short positions on variable interest rates with leverage through a hybrid system combining a central limit order book (CLOB) and automated market maker (AMM).

Key features include:
- Interest rate swap trading with leverage
- Hybrid AMM + order book architecture
- Cross-margin and isolated margin accounts
- Funding rate oracle integration (Chainlink, Chaos Labs, Pendle)
- Withdrawal cooldown mechanism for security
- Agent-based trading delegation

## Deployed Networks

- **Arbitrum** (Primary deployment)

## Contracts in Scope

### Core Contracts (Arbitrum)

| Address | Contract | Description |
|---------|----------|-------------|
| `0x8080808080daB95eFED788a9214e400ba552DEf6` | Router | Main entry point, Diamond-like proxy delegating to modules |
| `0x1080808080f145b14228443212e62447C112ADaD` | MarketHub | Central margin management and market operations |
| `0x2080808080262c1706598c9DBDD3a0cD3601e5ea` | AccessController | Role-based access control |
| `0x3080808080Ee6a795c1a6Ff388195Aa5F11ECeE0` | MarketFactory | Creates new market instances |
| `0x3205e972714B52512c837AE6f5FCFDeB07f0f23C` | AMMFactory | Creates new AMM instances |
| `0x353C6Ba99500f9F5a7937aF7BF26c8E40817518B` | AdminModule | Administrative functions for AMM creation |
| `0xD0808080803c59dBF8825290bca8979786C2d65B` | MakerIncentiveDistributor | Merkle-based maker incentive distribution |
| `0xD180808080402FE41711Db560B8db5C41e21Df71` | AMMIncentiveDistributor | Merkle-based AMM LP incentive distribution |

### Dynamic Market Contracts

For each active market, the following contracts are in scope:
- **Market** - Order book and position management
- **AMM** - Automated market maker for the market
- **FIndexOracle** - Floating index oracle for settlement

Market list available at: https://api.boros.finance/core/docs#/Markets/MarketsController_getMarkets

### Source Repository

**GitHub:** https://github.com/pendle-finance/boros-core-public

### Contract Files in Scope

#### Core Router & Modules
- `contracts/core/router/Router.sol` - Diamond-like proxy router
- `contracts/core/router/modules/TradeModule.sol` - Trading operations
- `contracts/core/router/modules/AuthModule.sol` - Authentication and agent management
- `contracts/core/router/modules/DepositModule.sol` - Deposit box operations
- `contracts/core/router/modules/AMMModule.sol` - AMM interactions
- `contracts/core/router/modules/ConditionalModule.sol` - Conditional orders
- `contracts/core/router/modules/MiscModule.sol` - Miscellaneous operations

#### MarketHub
- `contracts/core/markethub/MarketHubEntry.sol` - Main entry point
- `contracts/core/markethub/MarketHubRiskManagement.sol` - Risk management
- `contracts/core/markethub/MarginManager.sol` - Margin calculations
- `contracts/core/markethub/Storage.sol` - Storage layout

#### Market
- `contracts/core/market/MarketEntry.sol` - Market entry point
- `contracts/core/market/MarketSetAndView.sol` - Settings and views
- `contracts/core/market/MarketOrderAndOtc.sol` - Order and OTC operations
- `contracts/core/market/MarketRiskManagement.sol` - Market risk management
- `contracts/core/market/findexOracle/FIndexOracle.sol` - Floating index oracle

#### AMM
- `contracts/core/amm/BaseAMM.sol` - Base AMM implementation
- `contracts/core/amm/PositiveAMM.sol` - Positive rate AMM
- `contracts/core/amm/NegativeAMM.sol` - Negative rate AMM
- `contracts/core/amm/PositiveAMMMath.sol` - Positive AMM math
- `contracts/core/amm/NegativeAMMMath.sol` - Negative AMM math

#### Factories
- `contracts/factory/MarketFactory.sol` - Market creation
- `contracts/factory/AMMFactory.sol` - AMM creation

#### Oracle & Verifier
- `contracts/oracle/FundingRateOracle.sol` - Funding rate oracle
- `contracts/verifier/FundingRateVerifier.sol` - Multi-source funding rate verification

#### Access Control
- `contracts/core/roles/PendleAccessController.sol` - Access control
- `contracts/core/roles/PendleRoles.sol` - Role definitions

#### Deposit & Distribution
- `contracts/deposit/DepositBox.sol` - User deposit boxes
- `contracts/deposit/DepositBoxFactory.sol` - Deposit box factory
- `contracts/distributor/MultiTokenMerkleDistributor.sol` - Merkle distributor

#### Admin
- `contracts/admin/AdminModule.sol` - Admin operations

## Award Levels

| Severity | Maximum Payout | Minimum Payout |
|----------|----------------|----------------|
| **Critical** | $500,000 USD | $50,000 USD |
| **High** | $100,000 USD | $20,000 USD |
| **Medium** | $50,000 USD | $10,000 USD |
| **Low** | At discretion | - |

**Note:** Rewards are capped at 10% of economic impact for fund-loss scenarios.

## Severity Definitions

### Technical Exploits

Vulnerabilities in smart contract implementation that could lead to theft or loss of funds.

| Likelihood | >10% TVL | 1-10% TVL | <1% TVL |
|------------|----------|-----------|---------|
| **High** | Critical | High | Medium |
| **Medium** | High | Medium | Medium or Low |
| **Low** | Medium | Medium or Low | Low |

For vulnerabilities resulting in inflated account balances (subject to withdrawal cooldown), funds at risk are calculated as 20% of exploitable amount.

### Economic Exploits

Design flaws and manipulation strategies exploiting legitimate protocol mechanisms. Severity determined case-by-case based on potential total financial damage.

## Out of Scope

### Excluded from Bounty
- Issues not from contracts listed in scope
- Known issues from previous audits (ChainSecurity, Spearbit, WatchPug)
- Third-party protocols or tokens integrated with Boros
- Frontend applications and UI bugs
- Infrastructure vulnerabilities (DNS, servers, CDN)
- MEV that doesn't violate protocol invariants
- Issues requiring unlikely user behavior or social engineering
- Vulnerabilities in underlying blockchain infrastructure

### Specific Issue Types Not Eligible
- Informational findings without security impact
- Design choices and protocol architecture decisions
- User errors preventable by frontend validation
- Minor rounding errors without economic impact
- Gas consumption optimizations
- Vulnerabilities requiring extreme market conditions

## Previous Audits

Boros has been audited by 3 firms:
1. **ChainSecurity** - Available in `/audits/ChainSecurity/`
2. **Spearbit** - Available in `/audits/Spearbit/`
3. **WatchPug** - Available in `/audits/WatchPug/`

## Key Focus Areas

1. **Margin System Integrity** - Cross-margin and isolated margin calculations
2. **Liquidation Logic** - Health ratio calculations and liquidation execution
3. **AMM Math** - Implied rate calculations, swap pricing, LP operations
4. **Oracle Security** - FIndex oracle updates, funding rate verification
5. **Access Control** - Agent permissions, relayer authentication
6. **Withdrawal Cooldown** - Cooldown bypass, timing attacks
7. **Order Book Operations** - Order matching, OTC trades, cancellations
8. **Cross-Account Operations** - Cash transfers, subaccount management

## Resources

- **Documentation:** https://boros.pendle.finance/
- **Whitepapers:** `/whitepapers/Boros.pdf`, `/whitepapers/AMM.pdf`
- **API Docs:** https://api.boros.finance/core/docs
- **GitHub:** https://github.com/pendle-finance/boros-core-public
