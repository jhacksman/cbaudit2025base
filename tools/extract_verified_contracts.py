#!/usr/bin/env python3
"""
Comprehensive contract source code extraction tool for Coinbase Bug Bounty 2025
Extracts verified source code from multiple blockchain explorers using APIs
"""

import requests
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ContractExtractor:
    def __init__(self, base_dir: str = "/home/ubuntu/cbaudit2025base"):
        self.base_dir = Path(base_dir)
        self.contracts_dir = self.base_dir / "contracts"
        
        self.etherscan_api = "https://api.etherscan.io/api"
        self.basescan_api = "https://api.basescan.org/api"
        self.optimism_api = "https://api-optimistic.etherscan.io/api"
        self.sourcify_api = "https://repo.sourcify.dev/contracts/full_match"
        
        self.contracts = {
            "cbbtc": {
                "ethereum": {
                    "proxy": "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf",
                    "implementation": "0x7458bfdc30034eb860b265e6068121d18fa5aa72"
                },
                "base": {
                    "proxy": "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf"
                }
            },
            "cbeth": {
                "ethereum": {
                    "proxy": "0xbe9895146f7af43049ca1c1ae358b0541ea49704",
                    "implementation": "0x31724ca0c982a31fbb5c57f4217ab585271fc9a5"
                },
                "optimism": {
                    "proxy": "0xaddb6a0412de1ba0f936dcaeb8aaa24578dcf3b2"
                },
                "base": {
                    "proxy": "0x2ae3f1ec7f1f5012cfeab0185bfc7aa3cf0dec22"
                }
            },
            "base": {
                "ethereum": {
                    "OptimismPortal": "0x49048044D57e1C92A77f79988d21Fa8fAF74E97e",
                    "L2OutputOracle": "0x56315b90dC61def39dcdf92c5ac048FF29F771DB",
                    "SystemConfig": "0x73a79Fab691434f2a4AC4b8b1b425f700b92a56A",
                    "L1StandardBridge": "0x3154Cf16ccdb4C6d922629664174bAF68eb54570",
                    "L1CrossDomainMessenger": "0x866E82a60037fedB8Cb9aa00261E2Df0918ddd48",
                    "L1ERC721Bridge": "0x6085AeBD3a0eda6d3A5a8Be4176dcc49c5510570"
                },
                "base": {
                    "WETH9": "0x4200000000000000000000000000000000000006",
                    "L2StandardBridge": "0x4200000000000000000000000000000000000010",
                    "L2CrossDomainMessenger": "0x4200000000000000000000000000000000000007",
                    "ProxyAdmin": "0x4200000000000000000000000000000000000018"
                }
            }
        }
        
        self.chain_ids = {
            "ethereum": 1,
            "base": 8453,
            "optimism": 10
        }
        
        self.api_endpoints = {
            "ethereum": self.etherscan_api,
            "base": self.basescan_api,
            "optimism": self.optimism_api
        }

    def get_contract_source_etherscan(self, address: str, network: str) -> Optional[Dict]:
        """Extract contract source from Etherscan-compatible API"""
        api_url = self.api_endpoints.get(network)
        if not api_url:
            print(f"No API endpoint for network: {network}")
            return None
            
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                return data["result"][0]
            else:
                print(f"Failed to get source for {address} on {network}: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error fetching from {network} API for {address}: {e}")
            return None

    def get_contract_source_sourcify(self, address: str, network: str) -> Optional[Dict]:
        """Extract contract source from Sourcify"""
        chain_id = self.chain_ids.get(network)
        if not chain_id:
            print(f"No chain ID for network: {network}")
            return None
            
        url = f"{self.sourcify_api}/{chain_id}/{address}/"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                files = response.json()
                source_files = {}
                
                for file_info in files:
                    if file_info.get("name", "").endswith(".sol"):
                        file_url = f"{url}{file_info['name']}"
                        file_response = requests.get(file_url, timeout=30)
                        if file_response.status_code == 200:
                            source_files[file_info["name"]] = file_response.text
                
                if source_files:
                    return {"SourceCode": source_files}
                    
        except Exception as e:
            print(f"Error fetching from Sourcify for {address} on {network}: {e}")
            
        return None

    def parse_source_code(self, source_data: Dict) -> Dict[str, str]:
        """Parse source code from API response"""
        source_code = source_data.get("SourceCode", "")
        
        if not source_code:
            return {}
            
        if isinstance(source_code, dict):
            return source_code
            
        if source_code.startswith("{{"):
            try:
                json_str = source_code[1:-1]
                parsed = json.loads(json_str)
                
                if "sources" in parsed:
                    files = {}
                    for file_path, file_data in parsed["sources"].items():
                        filename = os.path.basename(file_path)
                        files[filename] = file_data.get("content", "")
                    return files
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON source code: {e}")
                
        elif source_code.startswith("{"):
            try:
                parsed = json.loads(source_code)
                if "sources" in parsed:
                    files = {}
                    for file_path, file_data in parsed["sources"].items():
                        filename = os.path.basename(file_path)
                        files[filename] = file_data.get("content", "")
                    return files
            except json.JSONDecodeError:
                pass
                
        contract_name = source_data.get("ContractName", "Contract")
        return {f"{contract_name}.sol": source_code}

    def save_contract_files(self, files: Dict[str, str], output_dir: Path):
        """Save contract files to directory"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in files.items():
            if content.strip():  # Only save non-empty files
                file_path = output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Saved: {file_path}")

    def create_contract_metadata(self, contract_info: Dict, output_dir: Path):
        """Create metadata file for contract"""
        metadata = {
            "contract_name": contract_info.get("ContractName", "Unknown"),
            "compiler_version": contract_info.get("CompilerVersion", "Unknown"),
            "optimization": contract_info.get("OptimizationUsed", "Unknown"),
            "runs": contract_info.get("Runs", "Unknown"),
            "evm_version": contract_info.get("EVMVersion", "Unknown"),
            "library": contract_info.get("Library", ""),
            "license_type": contract_info.get("LicenseType", "Unknown"),
            "proxy": contract_info.get("Proxy", "0"),
            "implementation": contract_info.get("Implementation", ""),
            "swarm_source": contract_info.get("SwarmSource", "")
        }
        
        metadata_file = output_dir / "contract-metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved metadata: {metadata_file}")

    def extract_contract(self, address: str, network: str, contract_type: str, contract_name: str):
        """Extract a single contract"""
        print(f"\nExtracting {contract_type}/{network}/{contract_name}: {address}")
        
        source_data = self.get_contract_source_etherscan(address, network)
        
        if not source_data:
            print(f"Trying Sourcify for {address}...")
            source_data = self.get_contract_source_sourcify(address, network)
            
        if not source_data:
            print(f"Failed to extract source for {address} on {network}")
            return False
            
        files = self.parse_source_code(source_data)
        if not files:
            print(f"No source files found for {address}")
            return False
            
        output_dir = self.contracts_dir / contract_type / network / "verified" / contract_name
        
        self.save_contract_files(files, output_dir)
        
        self.create_contract_metadata(source_data, output_dir)
        
        print(f"Successfully extracted {len(files)} files for {contract_name}")
        return True

    def extract_all_contracts(self):
        """Extract all contracts in scope"""
        print("Starting comprehensive contract extraction...")
        
        total_contracts = 0
        successful_extractions = 0
        
        for contract_type, networks in self.contracts.items():
            for network, contracts in networks.items():
                for contract_name, address in contracts.items():
                    total_contracts += 1
                    
                    if self.extract_contract(address, network, contract_type, contract_name):
                        successful_extractions += 1
                    
                    time.sleep(1)
        
        print(f"\nExtraction complete: {successful_extractions}/{total_contracts} contracts extracted")
        
        self.create_extraction_summary(successful_extractions, total_contracts)

    def create_extraction_summary(self, successful: int, total: int):
        """Create extraction summary report"""
        summary = {
            "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_contracts": total,
            "successful_extractions": successful,
            "failed_extractions": total - successful,
            "success_rate": f"{(successful/total)*100:.1f}%" if total > 0 else "0%",
            "contracts_by_type": {}
        }
        
        for contract_type in self.contracts.keys():
            type_dir = self.contracts_dir / contract_type
            if type_dir.exists():
                file_count = sum(1 for f in type_dir.rglob("*.sol"))
                summary["contracts_by_type"][contract_type] = file_count
        
        summary_file = self.contracts_dir / "extraction-summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Extraction summary saved: {summary_file}")

def main():
    extractor = ContractExtractor()
    extractor.extract_all_contracts()

if __name__ == "__main__":
    main()
