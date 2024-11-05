from pathlib import Path
import re

from Quorum.apis.price_feeds import ChainLinkAPI, ChronicleAPI
from Quorum.utils.chain_enum import Chain
from Quorum.checks.check import Check
from Quorum.apis.block_explorers.source_code import SourceCode
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
        self.chainlink_api = ChainLinkAPI()
        self.chronicle_api = ChronicleAPI()

        self.address_pattern = r'0x[a-fA-F0-9]{40}'

        # Retrieve price feeds from Chainlink API and map them by contract address
        chain_link_price_feeds = self.chainlink_api.get_price_feeds_info(self.chain)
        self.chain_link_price_feeds = {feed.contractAddress: feed for feed in chain_link_price_feeds}
        self.chain_link_price_feeds.update({feed.proxyAddress: feed for feed in chain_link_price_feeds if feed.proxyAddress})

        # Retrieve price feeds from Chronical API and map them by contract address
        chronicle_price_feeds = self.chronicle_api.get_price_feeds_info(self.chain)
        self.chronicle_price_feeds_dict = {feed.get("address"): feed for feed in chronicle_price_feeds}

    
    def verify_feed_price(self) -> None:
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
                if address in self.chain_link_price_feeds:
                    feed = self.chain_link_price_feeds[address]
                    pp.pretty_print(
                        f"Found {address} on Chainlink\nname:{feed.name} Decimals:{feed.decimals}",
                        pp.Colors.SUCCESS
                    )
                    verified_variables.append(feed.dict())

                elif address in self.chronicle_price_feeds_dict:
                    feed = self.chronicle_price_feeds_dict[address]
                    pp.pretty_print(
                        f"Found {address} on Chronicle\nname:{feed.get('pair')}",
                        pp.Colors.SUCCESS
                    )
                    verified_variables.append(feed)
            
            if verified_variables:
                self._write_to_file(verified_sources_path, verified_variables)
            else:
                pp.pretty_print(f"No address related to chain link or chronicle found in {Path(source_code.file_name).stem}", pp.Colors.INFO)