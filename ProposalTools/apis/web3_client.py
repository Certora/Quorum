import os
from typing import Any, Optional

from web3 import Web3
from web3.exceptions import ContractLogicError

from ProposalTools.apis.contract_code.contract_source_code_api import ContractSourceCodeAPI, Chain


class Web3API:
    """
    Web3API is a client for interacting with Ethereum smart contracts through the Infura API.

    This class manages connection to the Ethereum blockchain using Web3 and Infura, and provides
    functionality for interacting with deployed smart contracts.

    Attributes:
        w3_client (Web3): The Web3 client connected to an Ethereum provider.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the Web3API client with the Infura API.

        Args:
            api_key (Optional[str]): The Infura API key to connect to the Ethereum blockchain. 
                                     If not provided, it will be fetched from the environment variable `INFURA_API_KEY`.

        Raises:
            ValueError: If the Infura API key is not set or invalid.
            ConnectionError: If the connection to the Infura API fails.
        """
        self.api_key = api_key or os.getenv("ETH_MAINNET_API")
        if self.api_key is None:
            raise ValueError("Infura API key is required. Set it in the 'INFURA_API_KEY' environment variable or pass it as an argument.")

        infura_url = f"https://mainnet.infura.io/v3/{self.api_key}"
        self.w3_client = Web3(Web3.HTTPProvider(infura_url))

        # Verify connection to Ethereum node
        if not self.w3_client.isConnected():
            raise ConnectionError("Failed to connect to Infura API. Check your network connection and API key.")

        # ETHScan API to retrieve the abi
        self.contract_code_api = ContractSourceCodeAPI(Chain.ETH)

    def call_contract_function(self, contract_address: str, function_name: str, *args: Any) -> Any:
        """
        Calls a specified function on an Ethereum smart contract.

        Args:
            contract_address (str): The Ethereum address of the smart contract.
            function_name (str): The name of the contract function to call.
            *args (Any): Any arguments that need to be passed to the contract function.

        Returns:
            Any: The result of the contract function call.

        Raises:
            ValueError: If the contract ABI or function name is invalid.
            ContractLogicError: If there's an error calling the contract function (e.g., invalid function name or input).
        """
        contract_abi = self.contract_code_api.get_contract_abi(contract_address)

        try:
            contract = self.w3_client.eth.contract(address=contract_address, abi=contract_abi)
        except Exception as e:
            raise ValueError(f"Error initializing contract: {str(e)}")

        try:
            contract_function = getattr(contract.functions, function_name)
        except AttributeError:
            raise ValueError(f"Function '{function_name}' not found in contract.")

        try:
            return contract_function(*args).call()
        except ContractLogicError as e:
            raise ContractLogicError(f"Error executing contract function '{function_name}': {str(e)}")
