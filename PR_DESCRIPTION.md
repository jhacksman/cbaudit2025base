# Initial repository setup and comprehensive scope documentation

This PR establishes the foundation for the Coinbase Base network bug bounty audit with comprehensive scope documentation and repository structure.

## Changes
- Add README.md with project overview and structure
- Add detailed scope documentation in docs/scope.md
- Document all Tier 0 contracts: Base network, cbBTC, cbETH
- Include specific contract addresses across all networks
- Set up directory structure for systematic audit approach

## Scope Summary
- **Tier 0 (Critical - Up to $5,000,000)**: Base network, cbBTC, cbETH
- **Tier 1 (High - Up to $500,000)**: All other Coinbase mainnet contracts
- **Networks**: Ethereum, Base, Arbitrum, Optimism, Polygon, Solana

## Contract Addresses Documented
- Base network L1/L2 system contracts from https://docs.base.org/base-chain/network-information/base-contracts
- cbBTC across Base, Ethereum, Arbitrum, Solana
- cbETH across Ethereum, Arbitrum, Optimism, Polygon, Base

## Repository Structure Created
```
/
├── README.md                 # Project overview and structure
├── docs/
│   ├── scope.md             # Complete bounty scope documentation
│   ├── methodology.md       # Audit methodology (next PR)
│   └── findings/            # Vulnerability findings directory
├── contracts/
│   ├── base/               # Base network L1/L2 contracts
│   ├── cbbtc/              # cbBTC token contracts
│   └── cbeth/              # cbETH token contracts
├── tools/                  # Audit tools and configurations
└── scripts/                # Automation scripts
```

## Next Steps
After approval, will proceed with:
1. Methodology development and documentation
2. Tool setup and configuration
3. Base network contract analysis
4. Systematic vulnerability testing

## Branch Information
- **Branch**: `devin/1720551917-initial-scope-documentation`
- **Base**: `main`
- **Status**: Ready for review

Link to Devin run: https://app.devin.ai/sessions/6ada166e78da4f089b704d79511ebd72
Requested by: Jack Hacksman (slack@hannis.io)
