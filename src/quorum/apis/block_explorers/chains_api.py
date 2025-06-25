import os
import sys
from json.decoder import JSONDecodeError

import json5 as json
import requests

from quorum.apis.block_explorers.bytecode import ContractAnalysisResult
from quorum.apis.block_explorers.source_code import SourceCode
from quorum.utils.chain_enum import Chain


class ChainAPI:
    """
    A class to interact with blockchain explorer APIs for fetching contract ABIs,
    source code, and calling smart contract functions using the 'eth_call' proxy.

    Attributes:
        chain_mapping (dict): Maps Chain enum to APIinfo containing base URL and API key function.
    """

    # Mapping between Chain enum members and their corresponding Chain IDs
    CHAIN_ID_MAP: dict[Chain, int] = {
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
        Chain.CELO: 42220,
        Chain.SONIC: 146,
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
            raise ValueError(
                f"Unsupported chain: {chain}. Available chains: {', '.join([c.name for c in self.CHAIN_ID_MAP.keys()])}"
            )
        # MET is not supported via ETHScan API
        if chain == Chain.MET:
            self.base_url = (
                "https://api.routescan.io/v2/network/mainnet/evm/1088/etherscan/api"
            )
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

        if data["status"] != "1":
            raise ValueError(
                f"Error fetching source code: {data.get('message', 'Unknown error')}\n{data.get('result')}"
            )

        result = data["result"][0]["SourceCode"]
        try:
            json_data = json.loads(result)
        except (JSONDecodeError, ValueError):
            # Handle non-JSON formatted responses
            json_data = json.loads(result.removeprefix("{").removesuffix("}"))

        sources = json_data.get("sources", {proposal_address: {"content": result}})
        source_codes = [
            SourceCode(
                file_name=source_name, file_content=source_code["content"].splitlines()
            )
            for source_name, source_code in sources.items()
        ]
        return source_codes

    def get_complete_contract_analysis(
        self, contract_address: str
    ) -> ContractAnalysisResult:
        """
        Performs a complete analysis of a contract including runtime bytecode,
        creation bytecode, and extracted constructor arguments.

        Args:
            contract_address: The Ethereum address of the smart contract.

        Returns:
            ContractAnalysisResult: A structured object containing:
            - runtime_bytecode: The deployed bytecode
            - creation_bytecode: The creation transaction input
            - constructor_args: Extracted constructor arguments (if available)
            - errors: List of any errors encountered during extraction

        Raises:
            ValueError: If the contract address is invalid or no bytecode can be retrieved.
        """
        result = ContractAnalysisResult()

        try:
            # Get runtime bytecode (this should always work for valid contracts)
            result.runtime_bytecode = self.__get_runtime_bytecode(contract_address)
        except ValueError as e:
            result.errors.append(f"Runtime bytecode error: {e!s}")
            raise e

        try:
            # Get creation bytecode (may fail for some contracts)
            result.creation_bytecode = self.__get_creation_bytecode(contract_address)

            # Try to extract constructor arguments
            if result.creation_bytecode and result.runtime_bytecode:
                result.constructor_args = self.__extract_raw_constructor_args(
                    result.creation_bytecode, result.runtime_bytecode
                )
        except ValueError as e:
            result.errors.append(f"Creation bytecode error: {e!s}")

        return result

    def __get_runtime_bytecode(self, contract_address: str) -> str:
        """
        Retrieves the final, deployed bytecode of a smart contract.
        This is the code stored on the blockchain at the contract's address.

        Args:
            contract_address: The Ethereum address of the smart contract.

        Returns:
            The runtime bytecode as a hexadecimal string, or an empty string on error.

        Raises:
            ValueError: If the API request fails or the bytecode could not be retrieved.
        """
        url = f"{self.base_url}&module=proxy&action=eth_getCode&address={contract_address}&tag=latest"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "0" or "error" in data:
            error_message = data.get("result") or data.get("error", {}).get("message")
            raise ValueError(f"Error fetching runtime bytecode: {error_message}")

        bytecode = data.get("result", "")
        if bytecode and bytecode != "0x":
            return bytecode
        else:
            raise ValueError(
                "No runtime bytecode found at this address. It might be a regular account or an unverified contract."
            )

    def __get_creation_bytecode(self, contract_address: str) -> str:
        """
        Retrieves the initial creation bytecode of a smart contract.
        This is the full 'input' data from the transaction that created the contract.

        Args:
            contract_address: The Ethereum address of the smart contract.

        Returns:
            The creation bytecode as a hexadecimal string, or an empty string on error.

        Raises:
            ValueError: If the API request fails or the creation transaction could not be found.
        """
        # Step 1: Find the transaction hash that created the contract
        tx_hash = self.__get_creation_transaction_hash(contract_address)
        if not tx_hash:
            raise ValueError(
                "Could not find creation transaction hash for this contract."
            )

        # Step 2: Use the transaction hash to get the full transaction details
        url = f"{self.base_url}&module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "0" or "error" in data:
            error_message = data.get("result") or data.get("error", {}).get("message")
            raise ValueError(f"Error fetching creation transaction: {error_message}")

        creation_bytecode = data.get("result", {}).get("input", "")
        if not creation_bytecode:
            raise ValueError("No creation bytecode found in transaction.")

        return creation_bytecode

    def __get_creation_transaction_hash(self, contract_address: str) -> str:
        """
        Finds the transaction hash that created the specified contract.
        NOTE: This uses the 'getcontractcreation' Etherscan Pro endpoint. It may
        work with a free key for some addresses but is not guaranteed.

        Args:
            contract_address: The Ethereum address of the smart contract.

        Returns:
            The creation transaction hash, or an empty string on error.

        Raises:
            ValueError: If the API request fails or the creation transaction could not be found.
        """
        url = f"{self.base_url}&module=contract&action=getcontractcreation&contractaddresses={contract_address}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "0" or "error" in data:
            error_message = (
                data.get("result")
                or data.get("message")
                or data.get("error", {}).get("message")
            )
            raise ValueError(f"Error finding creation transaction: {error_message}")

        result = data.get("result", [])
        if not result or not isinstance(result, list) or len(result) == 0:
            raise ValueError("No creation transaction found for this contract.")

        tx_hash = result[0].get("txHash", "")
        if not tx_hash:
            raise ValueError("Creation transaction hash not found in API response.")

        return tx_hash

    def __extract_raw_constructor_args(
        self, creation_code: str, runtime_code: str
    ) -> str:
        """
        Attempts to extract ABI-encoded constructor arguments from the creation bytecode,
        by comparing it to the deployed runtime bytecode.

        Args:
            creation_code: The full input data from the creation transaction (hex string).
            runtime_code: The bytecode stored at the contract's address (hex string).

        Returns:
            The extracted constructor arguments as a hex string, or an empty string if not found.

        Heuristic:
            - The creation code contains the runtime code, and constructor arguments are often
              appended at the end of the creation code.
            - If the creation code ends with the runtime code, arguments are likely embedded or absent.
            - Otherwise, if the runtime code is found within the creation code, the trailing data
              after the runtime code is considered as constructor arguments.
            - This method is not guaranteed to work for all contracts, especially those compiled
              with optimizations or using 'immutable' variables.
        """
        if not creation_code or not runtime_code or runtime_code == "0x":
            return ""

        creation_code_no_prefix = creation_code[2:]
        runtime_code_no_prefix = runtime_code[2:]

        if creation_code_no_prefix.endswith(runtime_code_no_prefix):
            return ""

        if runtime_code_no_prefix in creation_code_no_prefix:
            parts = creation_code_no_prefix.split(runtime_code_no_prefix, 1)
            if len(parts) == 2 and parts[1]:
                return "0x" + parts[1]

        print("Could not reliably extract constructor arguments.", file=sys.stderr)
        print(
            "This can happen with optimized contracts or those using 'immutable' variables.",
            file=sys.stderr,
        )
        return ""
