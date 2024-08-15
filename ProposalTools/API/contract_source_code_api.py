from dataclasses import dataclass
import requests
from typing import List, Callable
import os
import json

from ProposalTools.Utils.chain_enum import Chain
from ProposalTools.Utils.source_code import SourceCode


@dataclass
class APIinfo:
    """
    Data class for storing API base URL and API key retrieval function.
    """
    base_url: str
    api_key: Callable[[], str]

class ContractSourceCodeAPI():
    """
    Manages interactions with blockchain explorer APIs to fetch smart contract source codes.

    Attributes:
        chain_mapping (dict): Maps Chain enum to APIinfo containing base URL and API key function.
    """
    chain_mapping = {
        Chain.ETH: APIinfo(base_url="https://api.etherscan.io/api",
                           api_key=lambda: os.getenv('ETHSCAN_API_KEY')),
        Chain.ARB: APIinfo(base_url="https://api.arbiscan.io/api",
                           api_key=lambda: os.getenv('ARBSCAN_API_KEY')),
        Chain.AVAX: APIinfo(base_url="https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api",
                            api_key=lambda: os.getenv('AVAXSCAN_API_KEY', "FREE")),
        Chain.BASE: APIinfo(base_url="https://api.basescan.org/api",
                            api_key=lambda: os.getenv('BASESCAN_API_KEY')),
        Chain.BSC: APIinfo(base_url="https://api.bscscan.com/api",
                           api_key=lambda: os.getenv('BSCSCAN_API_KEY')),
        Chain.GNO: APIinfo(base_url="https://api.gnosisscan.io/api",
                           api_key=lambda: os.getenv('GNOSCAN_API_KEY')),
        Chain.MET: APIinfo(base_url="https://api.routescan.io/v2/network/mainnet/evm/1088/etherscan/api",
                           api_key=lambda: os.getenv('METSCAN_API_KEY', "FREE")),
        Chain.OPT: APIinfo(base_url="https://api-optimistic.etherscan.io/api",
                           api_key=lambda: os.getenv('OPTSCAN_API_KEY')),
        Chain.POLY: APIinfo(base_url="https://api.polygonscan.com/api",
                            api_key=lambda: os.getenv('POLYSCAN_API_KEY')),
        Chain.SCR: APIinfo(base_url="https://api.scrollscan.com/api",
                           api_key=lambda: os.getenv('SCRSCAN_API_KEY'))
    }
    
    def __init__(self, chain: Chain) -> None:
        """
        Initialize APIManager with a specific blockchain chain.

        Args:
            chain (Chain): The blockchain network to use (from the Chain enum).

        Raises:
            ValueError: If the chain is not supported or the API key is not set.
        """
        if chain not in self.chain_mapping:
            raise ValueError(f"Unsupported chain: {chain}. Try one of the following: {', '.join([c.name for c in self.chain_mapping.keys()])}")
        
        api_info = self.chain_mapping[chain]
        self.api_key = api_info.api_key()
        if not self.api_key:
            raise ValueError(f"{chain}SCAN_API_KEY environment variable is not set.")
        
        self.base_url = f"{api_info.base_url}?module=contract&action=getsourcecode&apikey={self.api_key}"

    def get_source_code(self, proposal_address: str) -> List[SourceCode]:
        """
        Fetch the source code of a smart contract from the blockchain explorer API.

        Args:
            proposal_address (str): The address of the smart contract.

        Returns:
            List[SourceCode]: A list of SourceCode objects containing file names and contents.

        Raises:
            ValueError: If there's an error fetching the source code.
        """
        url = f"{self.base_url}&address={proposal_address}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] != '1':
            raise ValueError(f"Error fetching source code: {data.get('message', 'Unknown error')}\n{data.get('result')}")
        
        result = data['result'][0]["SourceCode"]
        try:
            json_data = json.loads(result)
        except json.JSONDecodeError:
            # Handle non-JSON formatted response
            json_data = json.loads(result.removeprefix("{").removesuffix("}"))
        
        sources = json_data.get("sources", {proposal_address: {"content": result}})
        source_codes = [
            SourceCode(file_name=source_name, file_content=source_code["content"].splitlines())
            for source_name, source_code in sources.items()
        ]
        return source_codes
