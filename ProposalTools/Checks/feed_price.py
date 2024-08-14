import json
from pathlib import Path
from typing import Any

from ProposalTools.API.chainlink_api import ChainLinkAPI
from ProposalTools.Utils.chain_enum import Chain
from ProposalTools.Checks.check import Check
from ProposalTools.Utils.source_code import SourceCode
import ProposalTools.Utils.pretty_printer as pp


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
    
    def verify_feed_price(self) -> None:
        """
        Verifies the price feeds in the source code against the Chainlink API for the specified chain.

        This method retrieves price feeds from the Chainlink API, compares them against the addresses
        found in the source code, and then categorizes them into verified or violated based on the comparison.
        """
        # Retrieve price feeds from Chainlink API and map them by contract address
        price_feeds = self.api.get_price_feeds_info(self.chain)
        price_feeds_dict = {feed.contractAddress: feed for feed in price_feeds}

        # Iterate through each source code file to find and verify address variables
        for source_code in self.source_codes:
            verified_sources_path = f"{Path(source_code.file_name).stem.removesuffix('.sol')}/verified_sources.json"
            verified_variables = []
            
            unverified_sources_path = f"{Path(source_code.file_name).stem.removesuffix('.sol')}/unverified_sources.json"
            unverified_variables = []

            state_variables = source_code.get_state_variables()
            if state_variables:
                address_variables = [
                    v for v in state_variables.values()
                    if v.get("typeName").get("name") == "address"
                ]
                # Check each address variable against the Chainlink data
                for variable in address_variables:
                    address = variable.get("expression").get("number")
                    if address:
                        if address in price_feeds_dict:
                            pp.pretty_print(f"Found {address} on Chainlink", pp.Colors.SUCCESS)
                            feed = price_feeds_dict[address]
                            verified_variables.append(feed.__dict__)
                        else:
                            pp.pretty_print(f"Could not find {address} on Chainlink", pp.Colors.FAILURE)
                            unverified_variables.append(dict(variable))
            
            if verified_variables:
                self._write_to_file(verified_sources_path, verified_variables)
            if unverified_variables:
                self._write_to_file(unverified_sources_path, unverified_variables)