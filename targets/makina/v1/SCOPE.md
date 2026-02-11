# Makina Protocol Bug Bounty Scope

## Program Overview

- **Platform**: Cantina
- **URL**: https://cantina.xyz/bounties/4e88f4df-c483-47d3-8d78-b9d7cc67be73
- **Status**: Live
- **Maximum Reward**: $500,000 (Critical), $50,000 (High)
- **Deposit Required**: $5
- **Safe Harbor**: 10% of TVL

## Protocol Description

Makina is an innovative protocol for superior onchain execution. It provides infrastructure for operators to issue tokenized strategies with full DeFi composability and strong risk controls. The protocol features:

- **Hub-and-spoke multi-chain design** for sophisticated cross-chain strategies
- **MakinaVM** - flexible yet controlled execution environment for interacting with external protocols
- **Comprehensive governance framework** with multiple stakeholder roles and timelocked controls

## Core Components

1. **Machine** - Core abstraction managing deposits, redemptions, and fees
2. **Caliber** - Handles cross-chain operations and accounting (execution engine)
3. **Governance** - Manages permissions, risk parameters, and system updates

## In-Scope Contracts

### makina-core (https://github.com/MakinaHQ/makina-core)

#### Machine Contracts
| Contract | Path | Description |
|----------|------|-------------|
| Machine.sol | src/machine/Machine.sol | Core component handling deposits, redemptions, share price calculation |
| MachineShare.sol | src/machine/MachineShare.sol | ERC20 share token for user ownership |

#### Caliber Contracts
| Contract | Path | Description |
|----------|------|-------------|
| Caliber.sol | src/caliber/Caliber.sol | Execution engine for deploying assets to external protocols |
| CaliberMailbox.sol | src/caliber/CaliberMailbox.sol | Cross-chain communication between Hub Machine and Spoke Calibers |

#### Bridge Contracts
| Contract | Path | Description |
|----------|------|-------------|
| BridgeAdapter.sol | src/bridge/adapters/BridgeAdapter.sol | Base bridge adapter |
| AcrossV3BridgeAdapter.sol | src/bridge/adapters/AcrossV3BridgeAdapter.sol | Across V3 bridge integration |
| LayerZeroV2BridgeAdapter.sol | src/bridge/adapters/LayerZeroV2BridgeAdapter.sol | LayerZero V2 bridge integration |
| BridgeController.sol | src/bridge/controller/BridgeController.sol | Bridge transfer coordination |
| AcrossV3BridgeConfig.sol | src/bridge/configs/AcrossV3BridgeConfig.sol | Across V3 configuration |
| LayerZeroV2BridgeConfig.sol | src/bridge/configs/LayerZeroV2BridgeConfig.sol | LayerZero V2 configuration |

#### Registry Contracts
| Contract | Path | Description |
|----------|------|-------------|
| HubCoreRegistry.sol | src/registries/HubCoreRegistry.sol | Hub component addresses |
| SpokeCoreRegistry.sol | src/registries/SpokeCoreRegistry.sol | Spoke component addresses |
| OracleRegistry.sol | src/registries/OracleRegistry.sol | Price feed aggregation |
| TokenRegistry.sol | src/registries/TokenRegistry.sol | Cross-chain token mapping |
| ChainRegistry.sol | src/registries/ChainRegistry.sol | EVM to Wormhole chain ID mapping |

#### Factory Contracts
| Contract | Path | Description |
|----------|------|-------------|
| HubCoreFactory.sol | src/factories/HubCoreFactory.sol | Hub deployment factory |
| SpokeCoreFactory.sol | src/factories/SpokeCoreFactory.sol | Spoke deployment factory |
| CaliberFactory.sol | src/factories/CaliberFactory.sol | Caliber deployment |
| BridgeAdapterFactory.sol | src/factories/BridgeAdapterFactory.sol | Bridge adapter deployment |

#### Other Core Contracts
| Contract | Path | Description |
|----------|------|-------------|
| SwapModule.sol | src/swap/SwapModule.sol | External swap protocol integration |
| PreDepositVault.sol | src/pre-deposit/PreDepositVault.sol | Pre-deposit campaign vault |
| MakinaGovernable.sol | src/utils/MakinaGovernable.sol | Access control base |
| MakinaContext.sol | src/utils/MakinaContext.sol | Context utilities |

#### Libraries
| Contract | Path | Description |
|----------|------|-------------|
| CaliberAccountingCCQ.sol | src/libraries/CaliberAccountingCCQ.sol | Cross-chain query accounting |
| DecimalsUtils.sol | src/libraries/DecimalsUtils.sol | Decimal handling |
| MachineUtils.sol | src/libraries/MachineUtils.sol | Machine utilities |
| LzOptionsBuilder.sol | src/libraries/LzOptionsBuilder.sol | LayerZero options |
| Errors.sol | src/libraries/Errors.sol | Error definitions |

### makina-periphery (https://github.com/MakinaHQ/makina-periphery)

#### Depositor/Redeemer Contracts
| Contract | Path | Description |
|----------|------|-------------|
| DirectDepositor.sol | src/depositors/DirectDepositor.sol | Direct deposit handling |
| AsyncRedeemer.sol | src/redeemers/AsyncRedeemer.sol | Async redemption queue |

#### Fee Management
| Contract | Path | Description |
|----------|------|-------------|
| WatermarkFeeManager.sol | src/fee-managers/WatermarkFeeManager.sol | Fee calculation with watermark |

#### Security Module
| Contract | Path | Description |
|----------|------|-------------|
| SecurityModule.sol | src/security-module/SecurityModule.sol | Security staking module |
| SMCooldownReceipt.sol | src/security-module/SMCooldownReceipt.sol | Cooldown receipt NFT |

#### Oracles
| Contract | Path | Description |
|----------|------|-------------|
| MachineShareOracle.sol | src/oracles/MachineShareOracle.sol | Share price oracle |
| ERC4626Oracle.sol | src/oracles/ERC4626Oracle.sol | ERC4626 vault oracle |

#### Flashloans
| Contract | Path | Description |
|----------|------|-------------|
| FlashloanAggregator.sol | src/flashloans/FlashloanAggregator.sol | Flashloan aggregation |

#### Other Periphery
| Contract | Path | Description |
|----------|------|-------------|
| HubPeripheryRegistry.sol | src/registries/HubPeripheryRegistry.sol | Periphery registry |
| HubPeripheryFactory.sol | src/factories/HubPeripheryFactory.sol | Periphery factory |
| Whitelist.sol | src/utils/Whitelist.sol | Whitelist management |

## Deployed Networks

- Ethereum Mainnet (Hub)
- Base (Spoke)
- Arbitrum (Spoke)
- Other EVM chains as Spokes

## Known Issues / Out of Scope

Based on the January 2026 exploit (rekt.news/makina-rekt):
- Oracle manipulation via unchecked synchronous deposits was exploited
- $4.13M lost through flash loan attack on DUSD/USDC Curve pool
- The attack vector was explicitly listed as out of scope in previous audits

## Severity Classification

| Severity | Max Reward | Description |
|----------|------------|-------------|
| Critical | $500,000 | Immediate threat (fund theft, permanent DoS) |
| High | $50,000 | Significant risk with conditions |

## Key Focus Areas

1. **Cross-chain Security**: Bridge adapters, message relay, state synchronization
2. **Share Price Manipulation**: Donation attacks, oracle manipulation
3. **Access Control**: Role-based permissions, privilege escalation
4. **Weiroll Execution**: Instruction validation, reentrancy in execution
5. **Fee Calculation**: Watermark manipulation, fee inflation
6. **Flashloan Interactions**: Atomic manipulation attacks
7. **Recovery Mode**: Security council powers, emergency functions

## Previous Audits

- ChainSecurity: Makina-Core (Sep 2025, Jan 2026)
- ChainSecurity: Makina-Periphery (Sep 2025, Jan 2026)
- SigmaPrime: Makina-Core & Periphery (Aug 2025)
- OtterSec: Makina-Core & Periphery (Nov 2025)
- Enigma Dark: Fuzz/Invariant Testing (Jul 2025)
- Cantina CTF: Oct 2025 ($100K competition, 161 findings)

## Resources

- Documentation: https://docs.makina.finance/
- GitHub: https://github.com/MakinaHQ
- Security: https://docs.makina.finance/contracts/security
- Safe Harbor: https://docs.makina.finance/contracts/safe-harbor
