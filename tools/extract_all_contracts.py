#!/usr/bin/env python3
"""
Comprehensive contract source code extraction script for cbBTC, cbETH, and Base network contracts.
This script extracts verified source code from Etherscan for all contracts in scope.
"""

import requests
import json
import os
import time
from pathlib import Path

CONTRACTS = {
    'cbbtc': {
        'ethereum': {
            'proxy': '0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf',
            'implementation': '0x7458bfdc30034eb860b265e6068121d18fa5aa72'
        },
        'base': {
            'proxy': '0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf'
        }
    },
    'cbeth': {
        'ethereum': {
            'proxy': '0xbe9895146f7af43049ca1c1ae358b0541ea49704',
            'implementation': '0x31724ca0c982a31fbb5c57f4217ab585271fc9a5'
        },
        'optimism': {
            'proxy': '0xaddb6a0412de1ba0f936dcaeb8aaa24578dcf3b2'
        },
        'base': {
            'proxy': '0x2ae3f1ec7f1f5012cfeab0185bfc7aa3cf0dec22'
        }
    },
    'base': {
        'ethereum': {
            'OptimismPortal': '0x49048044D57e1C92A77f79988d21Fa8fAF74E97e',
            'L2OutputOracle': '0x56315b90dC61def39dcdf92c5ac048FF29F771DB',
            'SystemConfig': '0x73a79Fab691434f2a4AC4b8b1b425f700b92a56A',
            'L1StandardBridge': '0x3154Cf16ccdb4C6d922629664174bAF68eb54570',
            'L1CrossDomainMessenger': '0x866E82a60037fedB8Cb9aa00261E2Df0918ddd48',
            'L1ERC721Bridge': '0x6085AeBD3a0eda6d3A5a8Be4176dcc49c5510570'
        },
        'base': {
            'WETH9': '0x4200000000000000000000000000000000000006',
            'L2StandardBridge': '0x4200000000000000000000000000000000000010',
            'L2CrossDomainMessenger': '0x4200000000000000000000000000000000000007',
            'ProxyAdmin': '0x4200000000000000000000000000000000000018'
        }
    }
}

API_ENDPOINTS = {
    'ethereum': 'https://api.etherscan.io/api',
    'base': 'https://api.basescan.org/api',
    'optimism': 'https://api-optimistic.etherscan.io/api'
}

def get_contract_source(address, network='ethereum', api_key=None):
    """
    Fetch verified source code for a contract from Etherscan API
    """
    api_url = API_ENDPOINTS.get(network, API_ENDPOINTS['ethereum'])
    
    params = {
        'module': 'contract',
        'action': 'getsourcecode',
        'address': address
    }
    
    if api_key:
        params['apikey'] = api_key
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == '1' and data['result']:
            return data['result'][0]
        else:
            print(f"Failed to get source for {address} on {network}: {data.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Error fetching source for {address} on {network}: {e}")
        return None

def save_contract_source(contract_data, output_dir, contract_name):
    """
    Save contract source code to files
    """
    if not contract_data:
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    source_code = contract_data.get('SourceCode', '')
    contract_name_from_api = contract_data.get('ContractName', contract_name)
    
    if source_code.startswith('{'):
        try:
            if source_code.startswith('{{') and source_code.endswith('}}'):
                source_code = source_code[1:-1]
            
            source_json = json.loads(source_code)
            
            sources = source_json.get('sources', {})
            if not sources:
                sources = source_json
            
            files_saved = 0
            for file_path, file_data in sources.items():
                if isinstance(file_data, dict):
                    content = file_data.get('content', '')
                else:
                    content = str(file_data)
                
                if content:
                    clean_path = file_path.replace('@', '').replace('/', '_').replace('\\', '_')
                    if not clean_path.endswith('.sol'):
                        clean_path += '.sol'
                    
                    file_output_path = os.path.join(output_dir, clean_path)
                    with open(file_output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"  Saved: {clean_path}")
                    files_saved += 1
            
            print(f"  Total files saved: {files_saved}")
            return files_saved > 0
            
        except json.JSONDecodeError as e:
            print(f"  Error parsing JSON source: {e}")
            pass
    
    if source_code:
        filename = f"{contract_name_from_api}.sol"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(source_code)
        
        print(f"  Saved: {filename}")
        return True
    
    return False

def create_contract_info(contract_data, output_dir, address, network):
    """
    Create a contract info file with metadata
    """
    if not contract_data:
        return
    
    info = {
        'address': address,
        'network': network,
        'contract_name': contract_data.get('ContractName', ''),
        'compiler_version': contract_data.get('CompilerVersion', ''),
        'optimization_used': contract_data.get('OptimizationUsed', ''),
        'runs': contract_data.get('Runs', ''),
        'constructor_arguments': contract_data.get('ConstructorArguments', ''),
        'evm_version': contract_data.get('EVMVersion', ''),
        'library': contract_data.get('Library', ''),
        'license_type': contract_data.get('LicenseType', ''),
        'proxy': contract_data.get('Proxy', ''),
        'implementation': contract_data.get('Implementation', ''),
        'swarm_source': contract_data.get('SwarmSource', '')
    }
    
    info_path = os.path.join(output_dir, 'contract-info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)
    
    print(f"  Saved contract info: contract-info.json")

def extract_all_contracts():
    """
    Extract all contracts in scope
    """
    base_dir = Path('/home/ubuntu/cbaudit2025base/contracts')
    
    total_extracted = 0
    
    for contract_type, networks in CONTRACTS.items():
        print(f"\n=== Extracting {contract_type.upper()} contracts ===")
        
        for network, contracts in networks.items():
            print(f"\n--- {network.upper()} network ---")
            
            for contract_name, address in contracts.items():
                print(f"\nExtracting {contract_name} ({address})...")
                
                output_dir = base_dir / contract_type / network / 'verified' / contract_name
                
                contract_data = get_contract_source(address, network)
                
                if contract_data:
                    if save_contract_source(contract_data, str(output_dir), contract_name):
                        total_extracted += 1
                        
                        create_contract_info(contract_data, str(output_dir), address, network)
                        
                        readme_path = output_dir / 'README.md'
                        with open(readme_path, 'w') as f:
                            f.write(f"# {contract_name}\n\n")
                            f.write(f"**Address**: {address}\n")
                            f.write(f"**Network**: {network}\n")
                            f.write(f"**Contract Name**: {contract_data.get('ContractName', 'N/A')}\n")
                            f.write(f"**Compiler Version**: {contract_data.get('CompilerVersion', 'N/A')}\n")
                            f.write(f"**Optimization**: {contract_data.get('OptimizationUsed', 'N/A')}\n")
                            f.write(f"**License**: {contract_data.get('LicenseType', 'N/A')}\n\n")
                            f.write("## Purpose\n\n")
                            if contract_type == 'cbbtc':
                                f.write("Coinbase Wrapped Bitcoin (cbBTC) - ERC20 token backed 1:1 by Bitcoin held by Coinbase.\n")
                            elif contract_type == 'cbeth':
                                f.write("Coinbase Wrapped Staked ETH (cbETH) - Represents ETH staked through Coinbase with floating exchange rate.\n")
                            elif contract_type == 'base':
                                f.write("Base network infrastructure contract for L2 scaling solution.\n")
                        
                        print(f"  ✓ Successfully extracted {contract_name}")
                    else:
                        print(f"  ✗ Failed to save source for {contract_name}")
                else:
                    print(f"  ✗ Failed to fetch source for {contract_name}")
                
                time.sleep(0.2)
    
    print(f"\n=== EXTRACTION COMPLETE ===")
    print(f"Total contracts extracted: {total_extracted}")
    
    return total_extracted

if __name__ == "__main__":
    print("Starting comprehensive contract extraction...")
    print("This will extract verified source code for all cbBTC, cbETH, and Base network contracts.")
    
    extracted_count = extract_all_contracts()
    
    if extracted_count > 0:
        print(f"\n✓ Successfully extracted {extracted_count} contracts!")
        print("All source code has been organized into the contracts/ directory.")
        print("Ready for vulnerability analysis!")
    else:
        print("\n✗ No contracts were successfully extracted.")
        print("Check network connectivity and contract addresses.")
