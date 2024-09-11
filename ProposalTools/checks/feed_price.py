from pathlib import Path
import re

from ProposalTools.apis.chainlink_api import ChainLinkAPI
from ProposalTools.utils.chain_enum import Chain
from ProposalTools.checks.check import Check
from ProposalTools.apis.block_explorers.source_code import SourceCode
import ProposalTools.utils.pretty_printer as pp


class FeedPriceCheck(Check):
    """
    Verifies the price feed addresses in the provided source code against official Chainlink data.

    This class is responsible for verifying that the price feed addresses found in the source code
    match the addresses provided by the Chainlink API. It also categorizes these addresses into 
    verified and violated based on whether they are found in the official source.
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
        self.api = ChainLinkAPI()
        self.address_pattern = r'0x[a-fA-F0-9]{40}'

        # Retrieve price feeds from Chainlink API and map them by contract address
        price_feeds = self.api.get_price_feeds_info(self.chain)
        self.price_feeds_dict = {feed.contractAddress: feed for feed in price_feeds}
        self.price_feeds_dict.update({feed.proxyAddress: feed for feed in price_feeds if feed.proxyAddress})

    
    def verify_feed_price(self) -> None:
        """
        Verifies the price feeds in the source code against the Chainlink API for the specified chain.

        This method retrieves price feeds from the Chainlink API, compares them against the addresses
        found in the source code, and then categorizes them into verified or violated based on the comparison.
        """
        # Iterate through each source code file to find and verify address variables
        for source_code in self.source_codes:
            verified_sources_path = f"{Path(source_code.file_name).stem.removesuffix('.sol')}/verified_sources.json"
            verified_variables = []

            contract_text = '\n'.join(source_code.file_content)
            addresses = re.findall(self.address_pattern, contract_text)
            for address in addresses:
                if address in self.price_feeds_dict:
                    feed = self.price_feeds_dict[address]
                    pp.pretty_print(
                        f"Found {address} on Chainlink\nname:{feed.name} Decimals:{feed.decimals}",
                        pp.Colors.SUCCESS
                    )
                    verified_variables.append(feed.dict())
            
            if verified_variables:
                self._write_to_file(verified_sources_path, verified_variables)
            else:
                pp.pretty_print(f"No address related to chain link found in {Path(source_code.file_name).stem}", pp.Colors.INFO)