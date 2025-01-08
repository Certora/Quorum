from pydantic import BaseModel

import Quorum.checks as Checks
import Quorum.utils.pretty_printer as pp
from Quorum.utils.chain_enum import Chain
from Quorum.apis.block_explorers.chains_api import ChainAPI
from Quorum.apis.price_feeds.price_feed_utils import PriceFeedProviderBase
from Quorum.apis.governance.data_models import PayloadAddresses
from Quorum.apis.git_api.git_manager import GitManager
from Quorum.utils.quorum_configuration import QuorumConfiguration


class CustomerConfig(BaseModel):
    customer: str
    payload_addresses: list[PayloadAddresses]

    def __str__(self):
        s = f'Customer: {self.customer}\nChains and payloads:\n'
        for pa in self.payload_addresses:
            if len(pa.addresses) == 0:
                continue
            s += f'* {pa.chain}:\n'
            for address in pa.addresses:
                s += f'\t- {address}\n'
        return s


class ProposalConfig(BaseModel):
    customers_config: list[CustomerConfig]


def run_customer_proposal_validation(prop_config: ProposalConfig) -> None:
    """
    Execute proposal checks in batch for multiple customers and their configurations.

    This function processes proposal configurations for multiple customers, clones or updates
    their repositories, and performs proposal checks for specified addresses on different chains.

    Args:
        prop_config (ProposalConfig): Configuration object containing customer configs,
            payload addresses, and chain information for proposal validation.

    Returns:
        None

    Example:
        >>> prop_config = ProposalConfig(...)
        >>> run_batch(prop_config)
    """
    for config in prop_config.customers_config:
        pp.pprint('Run Preparation', pp.Colors.INFO, pp.Heading.HEADING_1)
        ground_truth_config = QuorumConfiguration().load_customer_config(config.customer)
        git_manager = GitManager(config.customer, ground_truth_config)
        git_manager.clone_or_update()
        price_feed_providers = ground_truth_config.get("price_feed_providers", [])
        token_providers = ground_truth_config.get("token_validation_providers", [])
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

        pp.pprint('Run Metadata', pp.Colors.INFO, pp.Heading.HEADING_2)
        pp.pprint(str(config), pp.Colors.INFO)
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

        for pa in config.payload_addresses:
            proposals_check(
                customer=config.customer,
                chain=pa.chain,
                proposal_addresses=pa.addresses,
                price_feed_providers=price_feed_providers,
                token_providers=token_providers
            )


def proposals_check(customer: str, chain: Chain, proposal_addresses: list[str],
                     price_feed_providers: list[PriceFeedProviderBase], token_providers: list[PriceFeedProviderBase] = None) -> None:
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
    
    for proposal_address in proposal_addresses:
        pp.pprint(f'Analyzing payload {proposal_address} on {chain}', pp.Colors.INFO, pp.Heading.HEADING_1)

        try:
            source_codes = api.get_source_code(proposal_address)
        except ValueError:
            error_message = (
                f"Payload address {proposal_address} is not verified on {chain.name} explorer.\n"
                "We do not recommend to approve this proposal until the code is approved!\n"
                "Try contacting the proposer and ask them to verify the contract.\n"
                "No further checks are being performed on this payload."
            )
            pp.pprint(error_message, pp.Colors.FAILURE)
            # Skip further checks for this proposal 
            continue

        # Diff check
        pp.pprint('Check 1 - Comparing payload contract and imports with the source of truth',
                  pp.Colors.INFO, pp.Heading.HEADING_2)
        missing_files = Checks.DiffCheck(customer, chain, proposal_address, source_codes).find_diffs()
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

        # Review diff check
        pp.pprint(f'Check 2 - Verifying missing files against customer review repo',
                  pp.Colors.INFO, pp.Heading.HEADING_2)
        Checks.ReviewDiffCheck(customer, chain, proposal_address, missing_files).find_diffs()
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

        # Global variables check
        pp.pprint('Check 3 - Global variables', pp.Colors.INFO, pp.Heading.HEADING_2)
        Checks.GlobalVariableCheck(customer, chain, proposal_address, missing_files).check_global_variables()
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

        # Feed price check
        pp.pprint('Check 4 - Explicit addresses validation', pp.Colors.INFO, pp.Heading.HEADING_2)
        Checks.PriceFeedCheck(customer, chain, proposal_address, missing_files, price_feed_providers, token_providers).verify_price_feed()
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)
        
        # New listing check
        pp.pprint('Check 5 - First deposit for new listing', pp.Colors.INFO, pp.Heading.HEADING_2)
        Checks.NewListingCheck(customer, chain, proposal_address, missing_files).new_listing_check()
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)
