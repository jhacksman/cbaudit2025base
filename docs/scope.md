# Coinbase Bug Bounty Program Scope

## Program Overview

- **Platform**: Cantina
- **URL**: https://cantina.xyz/bounties/55316f42-3c5e-4746-9bd0-0f18dcbc344b
- **Launch Date**: July 8, 2025
- **Maximum Reward**: $5,000,000
- **Focus**: Onchain Bug Bounty Program for smart contracts

The Coinbase Onchain Bug Bounty Program targets vulnerabilities in deployed smart contracts for Coinbase's on-chain products. It emphasizes production-use contracts on mainnets, with rewards scaled by severity and tier. Off-chain issues should be reported via HackerOne instead.

## Key Objectives
- Identify vulnerabilities like reentrancy, privilege escalation, arithmetic errors, gas inefficiencies, and more
- Ensure reports include reproduction steps, impact, and fixes
- Testing must occur in local/private environments—no mainnet or public testnet exploitation

## Reward Structure

Rewards are discretionary, based on report quality, exploitability, and impact/likelihood.

| Tier | Contracts | Critical (Max) | High (Max) | Medium (Max) | Low (Max) |
|------|-----------|----------------|------------|--------------|-----------|
| Tier 0 | Base, cbBTC, cbETH | $5,000,000 | $500,000 | $50,000 | $5,000 (discretionary) |
| Tier 1 | All other mainnet contracts deployed by Coinbase for production products | $500,000 | $50,000 | $5,000 | $500 (discretionary) |

### Severity Classification
- **Critical**: Immediate threat (e.g., fund theft, permanent DoS)
- **High**: Significant risk with conditions (e.g., reentrancy leading to loss)
- **Medium**: Moderate impact (e.g., temporary DoS)
- **Low**: Minor issues (e.g., gas optimizations)
- **Informational**: No reward, but useful insights

## Tier 0 Assets (Critical Priority)

Focus on smart contracts deployed by Coinbase with production use-cases on mainnets. Below are key Tier 0 assets with addresses and purposes.

### 1. cbETH (Coinbase Wrapped Staked ETH)

**Description**: Represents ETH staked through Coinbase, with a floating exchange rate. It's an ERC20 token backed 1:1 by staked ETH reserves.

**Networks**: Ethereum Mainnet, Base Mainnet, Optimism

**Key Contracts**:

| Contract Type | Address | Purpose | Source |
|---------------|---------|---------|--------|
| Proxy (Ethereum) | 0xbe9895146f7af43049ca1c1ae358b0541ea49704 | Upgradeable proxy for token logic | Verified on Etherscan (FiatTokenProxy) |
| Implementation (Ethereum) | 0x31724ca0c982a31fbb5c57f4217ab585271fc9a5 | Core logic (StakedTokenV1: inherits from FiatTokenV2_1, adds oracle for exchange rate updates) | Verified on Etherscan |
| Proxy (Optimism) | 0xaddb6a0412de1ba0f936dcaeb8aaa24578dcf3b2 | Optimism deployment | Verified on Optimistic Etherscan |
| Proxy (Base) | 0x2ae3f1ec7f1f5012cfeab0185bfc7aa3cf0dec22 | Base deployment | Verified on BaseScan |

**Functionality Summary**: Mint/burn via minters, blacklist support, exchange rate oracle for staking rewards. Based on Centre's FiatToken with extensions.

### 2. cbBTC (Coinbase Wrapped BTC)

**Description**: ERC20 token backed 1:1 by Bitcoin held by Coinbase, compatible with DeFi.

**Networks**: Ethereum Mainnet, Base Mainnet, Solana (note: Solana may require separate tools for audit)

**Key Contracts**:

| Contract Type | Address | Purpose | Source |
|---------------|---------|---------|--------|
| Proxy (Ethereum) | 0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf | Upgradeable proxy | Verified on Etherscan (FiatTokenProxy) |
| Implementation (Ethereum) | 0x7458bfdc30034eb860b265e6068121d18fa5aa72 | Core logic (FiatTokenV2_1: ERC20 with minting, burning, blacklisting) | Verified on Etherscan |
| Proxy (Base) | 0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf | Base deployment | Verified on BaseScan |
| Solana Contract | cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij | Solana deployment (SPL token) | Not EVM; audit via Solana tools |

**Functionality Summary**: Standard ERC20 with rate-limited minting, no floating exchange rate (fixed 1:1).

### 3. Base (L2 Rollup)

**Description**: Ethereum L2 using Optimism's OP Stack for scaling, with rollups to Ethereum L1.

**Networks**: Base Mainnet (L2), Ethereum Mainnet (L1 contracts)

**Key Contracts** (from Base docs; all deployed by Coinbase or Optimism under Coinbase incubation):

| Name | Address (L1 unless noted) | Purpose |
|------|--------------------------------|---------|
| OptimismPortal | 0x49048044D57e1C92A77f79988d21Fa8fAF74E97e | Entry point for deposits/withdrawals between L1 and L2 |
| L2OutputOracle | 0x56315b90dC61def39dcdf92c5ac048FF29F771DB | Oracle for L2 state outputs on L1 |
| SystemConfig | 0x73a79Fab691434f2a4AC4b8b1b425f700b92a56A | Configures system parameters like gas limits |
| L1StandardBridge | 0x3154Cf16ccdb4C6d922629664174bAF68eb54570 | Bridges standard tokens from L1 to L2 |
| L1CrossDomainMessenger | 0x866E82a60037fedB8Cb9aa00261E2Df0918ddd48 | Messaging between L1 and L2 |
| L1ERC721Bridge | 0x6085AeBD3a0eda6d3A5a8Be4176dcc49c5510570 | Bridges ERC721 tokens from L1 to L2 |
| WETH9 (L2) | 0x4200000000000000000000000000000000000006 | Wrapped ETH on L2 |
| L2StandardBridge (L2) | 0x4200000000000000000000000000000000000010 | L2 side of token bridging |
| L2CrossDomainMessenger (L2) | 0x4200000000000000000000000000000000000007 | L2 messaging to L1 |
| ProxyAdmin (L2) | 0x4200000000000000000000000000000000000018 | Manages proxy upgrades on L2 |

**Functionality Summary**: Optimistic rollup for cheap/fast transactions, with fraud proofs via L1 oracles. Audit for rollup integrity, bridge security, and config access control.

## Tier 1 Assets

**Scope**: Any other Coinbase-deployed mainnet contracts (e.g., smart wallet at GitHub coinbase/smart-wallet, or appchains). Search Etherscan for "coinbase" deployer to identify.

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
4. **Rollup Integrity**: Fraud proofs and state validation
5. **Configuration Access Control**: System parameter management

### Token Contract Priorities
1. **Access Control**: Admin functions and privilege escalation
2. **Minting/Burning**: Token supply management mechanisms
3. **Cross-chain Functionality**: Multi-network deployment consistency
4. **Staking Mechanisms**: cbETH staking and reward distribution
5. **Oracle Integration**: Exchange rate updates and validation
6. **Proxy Patterns**: Upgradeable contract security

### General Smart Contract Vulnerabilities
1. **Reentrancy**: State manipulation through external calls
2. **Integer Overflow/Underflow**: Arithmetic vulnerabilities
3. **Access Control**: Unauthorized function execution
4. **Logic Errors**: Business logic flaws
5. **Economic Attacks**: MEV and economic manipulation
6. **Gas Inefficiencies**: Optimization opportunities
7. **Proxy Vulnerabilities**: Implementation and storage collisions

## Out of Scope

- Off-chain components (report to HackerOne)
- Non-production contracts or proofs-of-concept
- Public testnets/mainnet testing without authorization
- Previously known vulnerabilities
- Social engineering, DoS beyond PoC, or malicious exploitation
- Contracts not deployed by Coinbase

## Rules and Guidelines

- Submit via Cantina within 24 hours of discovery
- No public disclosure until fixed
- Must be first reporter; comply with laws (no sanctioned countries)
- Ineligible: Current/former Coinbase employees or code contributors

## Submission Requirements

- Vulnerabilities must be real and demonstrable
- Proof of concept required for all findings
- Clear impact assessment and remediation suggestions
- Follow responsible disclosure practices
- Include reproduction steps and fix recommendations
