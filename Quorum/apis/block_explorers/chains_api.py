import os
import requests
from json.decoder import JSONDecodeError
import json5 as json

from Quorum.utils.chain_enum import Chain
from Quorum.apis.block_explorers.source_code import SourceCode

class ChainAPI:
    """
    A class to interact with blockchain explorer APIs for fetching contract ABIs, 
    source code, and calling smart contract functions using the 'eth_call' proxy.

    Attributes:
        chain_mapping (dict): Maps Chain enum to APIinfo containing base URL and API key function.
    """
    
    # Mapping between Chain enum members and their corresponding Chain IDs
    CHAIN_ID_MAP = {
        Chain.ETH: 1,
        Chain.ARB: 42161,
        Chain.AVAX: 43114,
        Chain.BASE: 8453,
        Chain.BSC: 56,
        Chain.GNO: 100,
        Chain.OPT: 10,
        Chain.POLY: 137,
        Chain.SCROLL: 534352,
        Chain.ZK: 324,
        Chain.LINEA: 59144,
    }
    
    BASE_URL = "https://api.etherscan.io/v2/api?chainid={chain_id}&apikey={api_key}"
    
    def __init__(self, chain: Chain) -> None:
        """
        Initializes the ChainAPI with the appropriate blockchain network's base URL and API key.

        Args:
            chain (Chain): The blockchain network to interact with (from the Chain enum).

        Raises:
            ValueError: If the selected chain is unsupported or the API key is not set.
        """
        if chain not in self.CHAIN_ID_MAP and chain != Chain.MET:
            raise ValueError(f"Unsupported chain: {chain}. Available chains: {', '.join([c.name for c in self.CHAIN_ID_MAP.keys()])}")
        # MET is not supported via ETHScan API
        if chain == Chain.MET:
            self.base_url = "https://api.routescan.io/v2/network/mainnet/evm/1088/etherscan/api"
        else:
            chain_id = self.CHAIN_ID_MAP[chain]
            api_key = os.getenv("ETHSCAN_API_KEY")
            if not api_key:
                raise ValueError("ETHSCAN_API_KEY environment variable is not set.")
            
            self.base_url = self.BASE_URL.format(chain_id=chain_id, api_key=api_key)
        
        self.session = requests.Session()

    def get_source_code(self, proposal_address: str) -> list[SourceCode]:
        """
        Fetches the source code of a smart contract from the blockchain explorer API.

        Args:
            proposal_address (str): The address of the smart contract to retrieve the source code.

        Returns:
            list[SourceCode]: A list of SourceCode objects containing the file names and source code contents.

        Raises:
            ValueError: If the API request fails or the source code could not be retrieved.
        """
        url = f"{self.base_url}&module=contract&action=getsourcecode&address={proposal_address}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] != '1':
            raise ValueError(f"Error fetching source code: {data.get('message', 'Unknown error')}\n{data.get('result')}")

        result = data['result'][0]["SourceCode"]
        try:
            json_data = json.loads(result)
        except (JSONDecodeError, ValueError):
            # Handle non-JSON formatted responses
            json_data = json.loads(result.removeprefix("{").removesuffix("}"))
        
        sources = json_data.get("sources", {proposal_address: {"content": result}})
        source_codes = [
            SourceCode(file_name=source_name, file_content=source_code["content"].splitlines())
            for source_name, source_code in sources.items()
        ]
        return source_codes
