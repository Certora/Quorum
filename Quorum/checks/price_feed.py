from pathlib import Path
import re

from Quorum.apis.price_feeds import PriceFeedProviderBase
from Quorum.utils.chain_enum import Chain
from Quorum.checks.check import Check
from Quorum.apis.block_explorers.source_code import SourceCode
import Quorum.utils.pretty_printer as pp


def remove_solidity_comments(source_code: str) -> str:
    """
    Removes single-line and multi-line comments from Solidity source code.

    Args:
        source_code (str): The Solidity source code as a single string.

    Returns:
        str: The source code with comments removed.
    """
    # Regex pattern to match single-line comments (//...)
    single_line_comment_pattern = r"//.*?$"

    # Regex pattern to match multi-line comments (/*...*/)
    multi_line_comment_pattern = r"/\*.*?\*/"

    # First, remove multi-line comments
    source_code = re.sub(multi_line_comment_pattern, "", source_code, flags=re.DOTALL)

    # Then, remove single-line comments
    source_code = re.sub(
        single_line_comment_pattern, "", source_code, flags=re.MULTILINE
    )

    return source_code


class PriceFeedCheck(Check):
    """
    The PriceFeedCheck class is responsible for verifying the price feed addresses in the source code
    against official Chainlink or Chronical data.
    """

    def __init__(
        self,
        customer: str,
        chain: Chain,
        proposal_address: str,
        source_codes: list[SourceCode],
        providers: list[PriceFeedProviderBase],
    ) -> None:
        """
        Initializes the PriceFeedCheck object with customer information, proposal address,
        and source codes to be checked.

        Args:
            customer (str): The name of the customer for whom the verification is being performed.
            chain (Chain): The blockchain network to verify the price feeds against.
            proposal_address (str): The address of the proposal being verified.
            source_codes (list[SourceCode]): A list of source code objects containing the Solidity contracts to be checked.
            providers (list[PriceFeedProviderInterface]): A list of price feed providers to be used for verification.
        """
        super().__init__(customer, chain, proposal_address, source_codes)
        self.address_pattern = r"0x[a-fA-F0-9]{40}"
        self.providers = providers

    def __check_price_feed_address(self, address: str, file_name: str) -> dict | None:
        """
        Check if the given address is present in the price feed providers.

        Args:
            address (str): The address to be checked.
            file_name (str): The name of the source code file where the address was found.

        Returns:
            dict | None: The price feed data if the address is found, otherwise None.
        """
        for provider in self.providers:
            if price_feed := provider.get_price_feed(self.chain, address):

                color = pp.Colors.SUCCESS
                message = f"Found {address} on {provider.get_name()}\n"
                message += str(price_feed)
                if (
                    price_feed.proxy_address
                    and price_feed.proxy_address.lower() != address.lower()
                ):
                    message += f"Proxy address: {price_feed.proxy_address}\n"
                if address.lower() != price_feed.address.lower():
                    color = pp.Colors.FAILURE
                    message += (
                        "This is an implementation contract with a proxy address\n"
                    )
                    message += f"Origin Address: {price_feed.address}\n"

                pp.pretty_print(message, color)
                return price_feed.model_dump()

        pp.pretty_print(
            f"Address {address} not found in any address validation provider: {[p.get_name() for p in self.providers]}",
            pp.Colors.INFO,
        )
        return None

    def verify_price_feed(self) -> None:
        """
        Verifies the price feed addresses in the source code against official Chainlink or Chronical data.

        This method iterates through each source code file to find and verify the address variables
        against the official Chainlink and Chronical price feeds. It categorizes the addresses into
        verified and violated based on whether they are found in the official source.
        """
        # Iterate through each source code file to find and verify address variables
        for source_code in self.source_codes:
            verified_sources_path = f"{Path(source_code.file_name).stem.removesuffix('.sol')}/verified_sources.json"
            verified_variables = []

            # Combine all lines into a single string
            contract_text = "\n".join(source_code.file_content)

            # Remove comments from the source code
            clean_text = remove_solidity_comments(contract_text)

            # Extract unique addresses using regex
            addresses = set(re.findall(self.address_pattern, clean_text))

            for address in addresses:
                if feed := self.__check_price_feed_address(
                    address, source_code.file_name
                ):
                    verified_variables.append(feed)

            if verified_variables:
                self._write_to_file(verified_sources_path, verified_variables)
