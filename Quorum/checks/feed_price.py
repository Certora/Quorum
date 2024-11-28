from pathlib import Path
import re
import json

from Quorum.apis.price_feeds import ChainLinkAPI, ChronicleAPI, PriceFeedProvider, PriceFeedData
from Quorum.utils.chain_enum import Chain
from Quorum.checks.check import Check
from Quorum.apis.block_explorers.source_code import SourceCode
import Quorum.config as config
import Quorum.utils.pretty_printer as pp


class FeedPriceCheck(Check):
    """
    The VerifyFeedPrice class is responsible for verifying the price feed addresses in the source code
    against official Chainlink or Chronical data.
    """

    def __init__(self, customer: str, chain: Chain, proposal_address: str, source_codes: list[SourceCode]) -> None:
        """
        Initializes the VerifyFeedPrice object with customer information, proposal address, 
        and source codes to be checked.

        Args:
            customer (str): The name of the customer for whom the verification is being performed.
            chain (Chain): The blockchain network to verify the price feeds against.
            proposal_address (str): The address of the proposal being verified.
            source_codes (list[SourceCode]): A list of source code objects containing the Solidity contracts to be checked.
        """
        super().__init__(customer, chain, proposal_address, source_codes)
        self.address_pattern = r'0x[a-fA-F0-9]{40}'
        
        # load providers price feeds
        self.providers_to_price_feed = self.__fetch_price_feed_providers()

    def __fetch_price_feed_providers(self) -> dict[PriceFeedProvider, dict]:
        """
        Load the price feed providers from the ground truth file.

        Returns:
            dict[PriceFeedProvider, dict]: A dictionary mapping the price feed provider to the price feed data.
        """
        with open(config.GROUND_TRUTH_PATH) as f:
            providers: list = json.load(f).get(self.customer, {}).get("price_feed_providers", [])

        if not providers:
            pp.pretty_print(f"No price feed providers found for {self.customer}", pp.Colors.FAILURE)
            return {}
        
        # Map providers to price feeds
        providers_to_price_feed = {}
        for provider in providers:
            if provider == PriceFeedProvider.CHAINLINK:
                providers_to_price_feed[provider] = ChainLinkAPI().get_price_feeds_info(self.chain)
            elif provider == PriceFeedProvider.CHRONICLE:
                providers_to_price_feed[provider] = ChronicleAPI().get_price_feeds_info(self.chain)
            else:
                pp.pretty_print(f"Unknown price feed provider: {provider}", pp.Colors.FAILURE)
                providers.remove(provider)

        return providers_to_price_feed

    def __check_price_feed_address(self, address: str) -> dict | None:
        """
        Check if the given address is present in the price feed providers.

        Args:
            address (str): The address to be checked.

        Returns:
            dict | None: The price feed data if the address is found, otherwise None.
        """
        for provider, price_feeds in self.providers_to_price_feed.items():
            if address in price_feeds:
                feed: PriceFeedData = price_feeds[address]
                pp.pretty_print(
                    f"Found {address} on {provider}\nname:{feed.name if feed.name else feed.pair}",
                    pp.Colors.SUCCESS
                )
                return feed.dict()
            
        pp.pretty_print(f"Address {address} not found in any price feed provider", pp.Colors.INFO)
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
            addresses = re.findall(self.address_pattern, contract_text)
            for address in addresses:
                if feed := self.__check_price_feed_address(address):
                    verified_variables.append(feed)
            
            if verified_variables:
                self._write_to_file(verified_sources_path, verified_variables)
