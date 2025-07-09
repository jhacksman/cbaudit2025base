# Coinbase Bug Bounty Program Scope

## Program Overview

- **Platform**: Cantina
- **URL**: https://cantina.xyz/bounties/55316f42-3c5e-4746-9bd0-0f18dcbc344b
- **Launch Date**: July 8, 2025
- **Maximum Reward**: $5,000,000
- **Focus**: Onchain Bug Bounty Program for smart contracts

## Reward Structure

### Tier 0 - Critical Vulnerabilities
- **Reward**: Up to $5,000,000
- **Scope**: Base, cbBTC, and cbETH

### Tier 1 - High Vulnerabilities  
- **Reward**: Up to $500,000
- **Scope**: Everything not in Tier 0 (all other mainnet contracts deployed by Coinbase)

### Additional Tiers
- **Medium**: Up to $50,000
- **Low**: Up to $5,000
- **Informational**: Discretionary

## Tier 0 Assets (Critical Priority)

### 1. Base Network
**Description**: An L2 that rolls up to Ethereum (L1)
**Documentation**: https://docs.base.org/base-chain/network-information/base-contracts
**Scope**: L2 & L1 mainnet addresses as specified in documentation

#### Key Base Contracts (L2 - Base Mainnet)
- **SystemConfig**: 0x73a79Fab69143498Ed3712e519A88a918e1f4072
- **L2OutputOracle**: 0x56315b90c40730925ec5485cf004d835058518A0
- **OptimismPortal**: 0x49048044D57e1C92A77f79988d21Fa8fAF74E97e
- **L1CrossDomainMessenger**: 0x866E82a600A1414e583f7F13623F1aC5d58b0Afa
- **L1StandardBridge**: 0x3154Cf16ccdb4C6d922629664174b904d80F2C35
- **OptimismMintableERC20Factory**: 0x05cc379EBD9B30BbA19C6fA282AB29218EC61D84
- **L1ERC721Bridge**: 0x608d94945A64503E642E6370Ec598e519a2C1E53

#### Key Base Contracts (L1 - Ethereum Mainnet)
- **AddressManager**: 0x8EfB6B5c4767B09Dc9AA6Af4eAA89F749522BaE2
- **ProxyAdmin**: 0x0475cBCAebd9CE8AfA5025828d5b98DFb67E059E
- **SystemConfig**: 0x73a79Fab69143498Ed3712e519A88a918e1f4072
- **OptimismPortal**: 0x49048044D57e1C92A77f79988d21Fa8fAF74E97e
- **L2OutputOracle**: 0x56315b90c40730925ec5485cf004d835058518A0

### 2. cbBTC (Coinbase Wrapped BTC)
**Description**: Wrapped BTC, backed 1:1 by Bitcoin (BTC) held by Coinbase
**Documentation**: https://www.coinbase.com/blog/coinbase-wrapped-btc-cbbtc-is-now-live

#### cbBTC Contract Addresses
- **Base**: 0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf
- **Ethereum**: 0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf
- **Arbitrum**: 0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf
- **Solana**: cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij

### 3. cbETH (Coinbase Wrapped Staked ETH)
**Description**: Wrapped staked ETH that represents ETH staked through Coinbase
**Documentation**: https://www.coinbase.com/price/coinbase-wrapped-staked-eth

#### cbETH Contract Addresses
- **Ethereum**: 0xBe9895146f7AF43049ca1c1AE358B0541Ea49704
- **Arbitrum**: 0x1DEBd73E752bEaF79865Fd6446b0c970EaE7732f
- **Optimism**: 0xadDb6A0412DE1BA0F936DCaeb8Aaa24578dcF3B2
- **Polygon**: 0x4b4327dB1600B8B1440163F667e199CEf35385f5
- **Base**: 0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22

## Tier 1 Assets

**Scope**: All mainnet contracts associated with products not in Tier 0 that are deployed by Coinbase
**Networks**: Ethereum, Arbitrum, Optimism, Polygon, Base, and any other networks where Coinbase has deployed contracts

## Networks in Scope

1. **Ethereum Mainnet**
2. **Base Mainnet** 
3. **Arbitrum**
4. **Optimism**
5. **Polygon**
6. **Solana**

## Key Focus Areas for Audit

### Base Network Priorities
1. **Bridge Security**: L1/L2 bridge contracts and cross-chain messaging
2. **System Contracts**: Core infrastructure contracts (SystemConfig, OutputOracle, Portal)
3. **Token Bridges**: ERC20 and ERC721 bridge implementations

### Token Contract Priorities
1. **Access Control**: Admin functions and privilege escalation
2. **Minting/Burning**: Token supply management mechanisms
3. **Cross-chain Functionality**: Multi-network deployment consistency
4. **Staking Mechanisms**: cbETH staking and reward distribution

### General Smart Contract Vulnerabilities
1. **Reentrancy**: State manipulation through external calls
2. **Integer Overflow/Underflow**: Arithmetic vulnerabilities
3. **Access Control**: Unauthorized function execution
4. **Logic Errors**: Business logic flaws
5. **Economic Attacks**: MEV and economic manipulation

## Out of Scope

- Testnet contracts (unless specifically mentioned)
- Frontend applications and web interfaces
- Infrastructure not directly related to smart contracts
- Social engineering attacks
- Physical security

## Submission Requirements

- Vulnerabilities must be real and demonstrable
- Proof of concept required for all findings
- Clear impact assessment and remediation suggestions
- Follow responsible disclosure practices
