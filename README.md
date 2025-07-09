# Coinbase Base Network Bug Bounty Audit 2025

This repository contains a comprehensive audit of Coinbase's Base network bug bounty program launched on Cantina platform.

## Overview

- **Bounty Program**: [Coinbase Bug Bounty on Cantina](https://cantina.xyz/bounties/55316f42-3c5e-4746-9bd0-0f18dcbc344b)
- **Maximum Reward**: $5,000,000
- **Focus**: Base network smart contracts and on-chain infrastructure
- **Start Date**: July 8, 2025

## Repository Structure

```
/
├── README.md                 # This file
├── docs/
│   ├── scope.md             # Complete bounty scope documentation
│   ├── methodology.md       # Audit methodology and tools
│   └── findings/            # Vulnerability findings and reports
├── contracts/
│   ├── base/               # Base network L1/L2 contracts
│   ├── cbbtc/              # cbBTC token contracts
│   └── cbeth/              # cbETH token contracts
├── tools/                  # Audit tools and configurations
└── scripts/                # Automation scripts
```

## Scope Summary

### Tier 0 (Critical - Up to $5,000,000)
- **Base**: L2 that rolls up to Ethereum (L1)
- **cbBTC**: Wrapped BTC, backed 1:1 by Coinbase
- **cbETH**: Wrapped staked ETH representing ETH staked through Coinbase

### Tier 1 (High - Up to $500,000)
- All other mainnet contracts associated with products not in Tier 0 deployed by Coinbase

## Networks in Scope
- Ethereum Mainnet
- Base Mainnet
- Arbitrum
- Optimism
- Polygon
- Solana

## Getting Started

1. Review the complete scope in `docs/scope.md`
2. Understand the audit methodology in `docs/methodology.md`
3. Check contract addresses and source code in respective directories
4. Review findings and reports in `docs/findings/`

## Audit Progress

- [x] Initial scope research and documentation
- [ ] Methodology development
- [ ] Tool setup and configuration
- [ ] Base network contract analysis
- [ ] cbBTC contract analysis
- [ ] cbETH contract analysis
- [ ] Vulnerability testing and validation

## Contributing

This audit follows a structured PR-based workflow with approval gates at each major milestone.
