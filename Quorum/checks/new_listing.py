from Quorum.checks.check import Check
import Quorum.utils.pretty_printer as pp
import Quorum.utils.config as config
from Quorum.llm.chains.first_deposit_chain import FirstDepositChain, ListingArray


class NewListingCheck(Check):

    def new_listing_check(self) -> None:
        """
        Checks if the proposal address is a new listing on the blockchain.
        This method retrieves functions from the source codes and checks if there are any new listings.
        If new listings are detected, it handles them accordingly. Otherwise, it prints a message indicating
        no new listings were found.
        """
        functions = self._get_functions_from_source_codes()
        if functions.get("newListings", functions.get("newListingsCustom")):
            pp.pretty_print(f"New listings detected for {self.proposal_address}", pp.Colors.WARNING)
            
            # Check if Anthropic API key is configured
            if not config.ANTHROPIC_API_KEY:
                pp.pretty_print(
                    "First deposit check is skipped. If you have a LLM API key, you can add it to your environment variables to enable this check",
                    pp.Colors.WARNING
                )
                return
            
            proposal_code = self.source_codes[0].file_content
            proposal_code_str = '\n'.join(proposal_code)
            listings: ListingArray | None = FirstDepositChain().execute(proposal_code_str)
            if listings is None:
                pp.pretty_print(f"Failed to retrieve new listings for {self.proposal_address}", pp.Colors.FAILURE)
                return
            for listing in listings.listings:
                if listing.approve_indicator and listing.supply_indicator:
                    pp.pretty_print(
                        f"New listing detected for {listing}", pp.Colors.SUCCESS
                    )
                else:
                    pp.pretty_print(f"New listing detected for {listing.asset_symbol} but no approval or supply detected", pp.Colors.FAILURE)
            self._write_to_file("new_listings.json", listings.model_dump())
                     
        else:
            pp.pretty_print(f"No new listings detected for {self.proposal_address}", pp.Colors.INFO)
    
    def _get_functions_from_source_codes(self) -> dict:
        """
        Retrieves functions from the source codes.
        This method retrieves functions from the source codes and returns them in a dictionary.
        """
        functions = {}
        for source_code in self.source_codes:
            functions.update(source_code.get_functions())
        return functions
