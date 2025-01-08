from Quorum.checks.check import Check
import Quorum.utils.pretty_printer as pp
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
        if functions.get('newListings', functions.get('newListingsCustom')):
            pp.pprint(f'New listings detected for payload {self.proposal_address}', pp.Colors.WARNING)
            
            proposal_code = self.source_codes[0].file_content
            proposal_code_str = '\n'.join(proposal_code)
            try:
                listings: ListingArray | None = FirstDepositChain().execute(proposal_code_str)
            except:
                pp.pprint(
                    'New listings were detected in payload but first deposit check is skipped.\n'
                    'If you have a LLM API key, you can add it to your environment variables to enable this check',
                    pp.Colors.WARNING
                )
                return
            
            if listings is None:
                pp.pprint('New listings were detected in payload but LLM failed to retrieve them.',
                                pp.Colors.FAILURE)
                return
            
            pp.pprint(f'{len(listings.listings)} new asset listings were detected:', pp.Colors.INFO)
            for i, listing in enumerate(listings.listings, 1):
                pp.pprint(f'\t{i}. Variable: {listing.asset_symbol}\n'
                          f'\t   Asset address: {listing.asset_address}\n'
                          f'\t   Approve indicator: {listing.approve_indicator}\n'
                          f'\t   Supply seed amount: {listing.supply_seed_amount}\n'
                          f'\t   Supply indicator: {listing.supply_indicator}',
                          (pp.Colors.SUCCESS if listing.approve_indicator and listing.supply_indicator
                           else pp.Colors.FAILURE))
                
            self._write_to_file('new_listings.json', listings.model_dump())

        else:
            pp.pprint(f'No new listings detected for {self.proposal_address}', pp.Colors.INFO)

    def _get_functions_from_source_codes(self) -> dict:
        """
        Retrieves functions from the source codes.
        This method retrieves functions from the source codes and returns them in a dictionary.
        """
        functions = {}
        for source_code in self.source_codes:
            functions.update(source_code.get_functions())
        return functions
