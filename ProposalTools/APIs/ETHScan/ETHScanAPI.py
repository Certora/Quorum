import os
import requests
import json

from ProposalTools.APIs.AbsSourceCode import SourceCode, SourceCodeInterface


class ETHScanAPI(SourceCodeInterface):
    """
    ETHScanAPI is a class that interacts with the Etherscan API to fetch smart contract source code.

    Attributes:
        api_key (str): The API key for authenticating with Etherscan.
        base_url (str): The base URL for Etherscan API requests.
    """

    def __init__(self) -> None:
        """
        Initialize the ETHScanAPI with the API key from the environment variable.

        Raises:
            ValueError: If the ETHSCAN_API_KEY environment variable is not set.
        """
        super().__init__()
        self.api_key = os.getenv("ETHSCAN_API_KEY")
        if not self.api_key:
            raise ValueError("ETHSCAN_API_KEY environment variable is not set.")
        self.base_url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&apikey={self.api_key}"
    
    def get_source_code(self, proposal_address: str) -> list[SourceCode]:
        """
        Fetch the source code of a smart contract from Etherscan.

        Args:
            proposal_address (str): The Ethereum address of the smart contract.

        Returns:
            list[SourceCode]: A list of SourceCode objects containing the source code files.

        Raises:
            ValueError: If the response from Etherscan indicates an error or if the source code cannot be parsed.
        """
        url = f"{self.base_url}&address={proposal_address}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['status'] != '1':
            raise ValueError(f"Error fetching source code: {data.get('message', 'Unknown error')}")

        result = data['result'][0]["SourceCode"]

        try:
            json_data = json.loads(result)
        except json.JSONDecodeError:
            # Handle cases where the source code is not properly formatted JSON
            try:
                json_data = json.loads(result.removeprefix("{").removesuffix("}"))
            except json.JSONDecodeError:
                raise ValueError("Failed to parse source code JSON after attempting fixes.")

        sources = json_data.get("sources", {})

        source_codes = [
            SourceCode(source_name, source_code["content"].splitlines())
            for source_name, source_code in sources.items()
        ]

        return source_codes
