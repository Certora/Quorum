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
        if functions.get('newListings', functions.get('newListingsCustom')):
            pp.pprint(f"New listings detected for {self.proposal_address}", pp.Colors.WARNING)
            
            # Check if Anthropic API key is configured
            if not config.ANTHROPIC_API_KEY:
                pp.pprint(
                    'New listings were detected in payload but first deposit check is skipped.\n'
                    'If you have a LLM API key, you can add it to your environment variables to enable this check',
                    pp.Colors.WARNING
                )
                return
            
            proposal_code = self.source_codes[0].file_content
            proposal_code_str = '\n'.join(proposal_code)
            listings: ListingArray | None = FirstDepositChain().execute(proposal_code_str)
            if listings is None:
                pp.pprint('New listings were detected in payload but LLM failed to retrieve them.',
                                pp.Colors.FAILURE)
                return
            
            msg = f'{len(listings.listings)} new asset listings were detected:\n'
            for i, listing in enumerate(listings.listings, 1):
                if listing.approve_indicator and listing.supply_indicator:
                    msg += f'\t{i}. New listing detected for {listing.asset_symbol}\n'
                else:
                    msg += f'\t{i}. New listing detected for {listing.asset_symbol} but no approval or supply detected\n'
            pp.pprint(msg, pp.Colors.INFO)
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
