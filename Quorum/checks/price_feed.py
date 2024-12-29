from pathlib import Path
import re

from Quorum.apis.price_feeds import PriceFeedProviderBase
from Quorum.utils.chain_enum import Chain
from Quorum.checks.check import Check
from Quorum.apis.block_explorers.source_code import SourceCode
import Quorum.utils.pretty_printer as pp


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
            providers: list[PriceFeedProviderBase]
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
        self.address_pattern = r'0x[a-fA-F0-9]{40}'
        self.providers = providers

    def __check_price_feed_address(self, address: str) -> dict | None:
        """
        Check if the given address is present in the price feed providers.

        Args:
            address (str): The address to be checked.

        Returns:
            dict | None: The price feed data if the address is found, otherwise None.
        """
        for provider in self.providers:
            if (price_feed := provider.get_price_feed(self.chain, address)):
                pp.pretty_print(
                    f"Found {address} on {provider.get_name()}\n"
                    f"info: {price_feed}",
                    pp.Colors.SUCCESS
                )
                return price_feed.model_dump()
            
        pp.pretty_print(
            f"Address {address} not found in any address validation provider: {[p.get_name() for p in self.providers]}",
            pp.Colors.INFO
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

            contract_text = '\n'.join(source_code.file_content)
            addresses = set(re.findall(self.address_pattern, contract_text))
            for address in addresses:
                if feed := self.__check_price_feed_address(address):
                    verified_variables.append(feed)
            
            if verified_variables:
                self._write_to_file(verified_sources_path, verified_variables)
