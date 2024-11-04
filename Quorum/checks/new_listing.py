from pydantic import BaseModel

from Quorum.checks.check import Check
import Quorum.utils.pretty_printer as pp


class ListingDetails(BaseModel):
    asset: str
    assetSymbol: str = None
    priceFeedAddress: str = None


class FunctionCallDetails(BaseModel):
    pool: str
    asset: str
    asset_seed: str


class NewListingCheck(Check):

    def new_listing_check(self) -> None:
        """
        Checks if the proposal address is a new listing on the blockchain.
        This method retrieves functions from the source codes and checks if there are any new listings.
        If new listings are detected, it handles them accordingly. Otherwise, it prints a message indicating
        no new listings were found.
        """
        functions = self._get_functions_from_source_codes()
        if function := functions.get("newListings", functions.get("newListingsCustom")):
            pp.pretty_print(f"New listings detected for {self.proposal_address}", pp.Colors.WARNING)
            self._write_to_file("new_listings.json", data=function)
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
