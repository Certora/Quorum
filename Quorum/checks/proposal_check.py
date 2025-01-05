import Quorum.checks as Checks
import Quorum.utils.pretty_printer as pp
from Quorum.utils.chain_enum import Chain
from Quorum.apis.block_explorers.chains_api import ChainAPI
from Quorum.apis.price_feeds.price_feed_utils import PriceFeedProviderBase


def proposals_check(customer: str, chain: Chain, proposal_addresses: list[str], providers: list[PriceFeedProviderBase]) -> None:
    """
    Check and compare source code files for given proposals.

    This function handles the main logic of fetching source code from the remote repository.

    Args:
        customer (str): The customer name or identifier.
        chain_name (str): The blockchain chain name.
        proposal_addresses (list[str]): List of proposal addresses.
        providers (list[PriceFeedProviderInterface]): List of price feed providers.
    """
    api = ChainAPI(chain)
    
    pp.pretty_print(f"Processing customer {customer}, for chain: {chain}", pp.Colors.INFO)
    for proposal_address in proposal_addresses:
        pp.pretty_print(f"Processing proposal {proposal_address}", pp.Colors.INFO)

        try:
            source_codes = api.get_source_code(proposal_address)
        except ValueError as e:
            error_message = (
                f"Payload address {proposal_address} is not verified on {chain.name} explorer.\n"
                "We do not recommend to approve this proposal until the code is approved!\n"
                "Try contacting the proposer and ask them to verify the contract.\n"
                "No further checks are being performed on this payload."
            )
            pp.pretty_print(error_message, pp.Colors.FAILURE)
            # Skip further checks for this proposal 
            continue

        # Diff check
        missing_files = Checks.DiffCheck(customer, chain, proposal_address, source_codes).find_diffs()

        # Review diff check
        Checks.ReviewDiffCheck(customer, chain, proposal_address, missing_files).find_diffs()

        # Global variables check
        Checks.GlobalVariableCheck(customer, chain, proposal_address, missing_files).check_global_variables()

        # Feed price check
        Checks.PriceFeedCheck(customer, chain, proposal_address, missing_files, providers).verify_price_feed()

        # New listing check
        Checks.NewListingCheck(customer, chain, proposal_address, missing_files).new_listing_check()
