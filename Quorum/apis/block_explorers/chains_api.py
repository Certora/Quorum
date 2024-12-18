import os
import requests
from typing import Any
import json

from eth_abi import encode
from eth_utils import keccak

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
        Chain.SCR: 534352,
        Chain.ZK: 324
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
        if chain not in self.CHAIN_ID_MAP or chain != Chain.MET:
            raise ValueError(f"Unsupported chain: {chain}. Available chains: {', '.join([c.name for c in self.CHAIN_ID_MAP.keys()])}")
        
        if chain == Chain.MET:
            self.base_url = "https://api.routescan.io/v2/network/mainnet/evm/1088/etherscan/api"
        else:
            chain_id = self.CHAIN_ID_MAP[chain]
            api_key = os.getenv("ETHSCAN_API_KEY")
            if not self.api_key:
                raise ValueError(f"{chain}SCAN_API_KEY environment variable is not set.")
            
            self.base_url = self.BASE_URL.format(chain_id=chain_id, api_key=api_key)

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
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] != '1':
            raise ValueError(f"Error fetching source code: {data.get('message', 'Unknown error')}\n{data.get('result')}")

        result = data['result'][0]["SourceCode"]
        try:
            json_data = json.loads(result)
        except json.JSONDecodeError:
            # Handle non-JSON formatted responses
            json_data = json.loads(result.removeprefix("{").removesuffix("}"))
        
        sources = json_data.get("sources", {proposal_address: {"content": result}})
        source_codes = [
            SourceCode(file_name=source_name, file_content=source_code["content"].splitlines())
            for source_name, source_code in sources.items()
        ]
        return source_codes
    
    def get_contract_abi(self, contract_address: str) -> list[dict]:
        """
        Fetches the ABI of a smart contract from the blockchain explorer API.

        Args:
            contract_address (str): The address of the smart contract.

        Returns:
            list[dict]: The contract ABI as a list of dictionaries.

        Raises:
            ValueError: If the API request fails or the ABI could not be retrieved.
        """
        url = f"{self.base_url}&module=contract&action=getabi&address={contract_address}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['status'] != '1':
            raise ValueError(f"Error fetching contract ABI: {data.get('message', 'Unknown error')}\n{data.get('result')}")
        
        return json.loads(data['result'])

    def call_contract_function(self, contract_address: str, function_name: str, arguments: list[Any] | None = None) -> Any:
        """
        Encodes the ABI and calls a smart contract function using the blockchain explorer's eth_call proxy API.

        Args:
            contract_address (str): The address of the smart contract.
            function_name (str): The name of the function to call (e.g., "balanceOf").
            arguments (list[Any]): The arguments to pass to the contract function (if any).

        Returns:
            Any: The result of the contract function call, with cleaned output if the return type is an address.

        Raises:
            ValueError: If the API request fails or there is an error with the function call.
        """
        # Step 1: Fetch the contract ABI
        abi = self.get_contract_abi(contract_address)

        # Step 2: Retrieve the function ABI and compute the method ID
        function_abi = self._get_function_abi(function_name, abi)
        method_id = self._get_method_id(function_abi)

        # Step 3: Encode the arguments
        if arguments is None:
            arguments = []
        encoded_args = self._encode_arguments(function_abi, arguments)

        # Step 4: Prepare the data payload for the eth_call
        data = method_id + encoded_args

        # Step 5: Make the request to the blockchain explorer eth_call endpoint
        url = f"{self.base_url}&module=proxy&action=eth_call&to={contract_address}&data={data}&tag=latest"
        response = requests.get(url)
        response.raise_for_status()

        # Step 6: Handle the response
        result = response.json().get('result')
        if not result:
            raise ValueError(f"Error calling contract function: {response.json()}")

        # Step 7: Clean the result if the return type is an address
        if function_abi.get('outputs') and function_abi['outputs'][0]['type'] == 'address':
            result = "0x" + result[-40:]  # Keep only the last 20 bytes (40 hex chars) of the address

        return result

    def _get_function_abi(self, function_name: str, abi: list[dict]) -> dict:
        """
        Retrieves the ABI of a specific function from the contract ABI.

        Args:
            function_name (str): The name of the function.
            abi (list[dict]): The contract ABI.

        Returns:
            dict: The ABI of the function.

        Raises:
            ValueError: If the function is not found in the ABI.
        """
        for item in abi:
            if item['type'] == 'function' and item['name'] == function_name:
                return item
        raise ValueError(f"Function {function_name} not found in contract ABI.")

    def _get_method_id(self, function_abi: dict) -> str:
        """
        Generates the method ID from the function signature (first 4 bytes of the keccak-256 hash).

        Args:
            function_abi (dict): The ABI of the function.

        Returns:
            str: The 4-byte method ID as a hex string.
        """
        function_signature = f"{function_abi['name']}({','.join([input['type'] for input in function_abi['inputs']])})"
        return keccak(text=function_signature).hex()[:10]  # First 4 bytes = first 8 hex characters

    def _encode_arguments(self, function_abi: dict, arguments: list[Any]) -> str:
        """
        Encodes function arguments in ABI format.

        Args:
            function_abi (dict): The ABI of the function.
            arguments (list[Any]): The function arguments to encode.

        Returns:
            str: The ABI-encoded arguments as a hex string.
        """
        argument_types = [input['type'] for input in function_abi['inputs']]
        encoded_args = encode(argument_types, arguments)
        return encoded_args.hex()
