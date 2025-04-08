from pydantic import BaseModel

import quorum.checks as Checks
import quorum.utils.pretty_printer as pp
from quorum.apis.block_explorers.chains_api import ChainAPI, SourceCode
from quorum.apis.git_api.git_manager import GitManager
from quorum.apis.governance.data_models import PayloadAddresses
from quorum.apis.price_feeds.price_feed_utils import PriceFeedProviderBase
from quorum.utils.chain_enum import Chain
from quorum.utils.quorum_configuration import QuorumConfiguration


class CustomerConfig(BaseModel):
    customer: str
    payload_addresses: list[PayloadAddresses]

    def __str__(self):
        s = f"Customer: {self.customer}\nChains and payloads:\n"
        for pa in self.payload_addresses:
            if len(pa.addresses) == 0:
                continue
            s += f"* {pa.chain}:\n"
            for address in pa.addresses:
                s += f"\t- {address}\n"
        return s


class ProposalConfig(BaseModel):
    customers_config: list[CustomerConfig]


def load_customer_config(
    customer: str,
) -> tuple[list[PriceFeedProviderBase], list[PriceFeedProviderBase]]:
    """
    Load the configuration for a specific customer.
    This function retrieves the price feed providers and token validation providers
    from the customer's configuration file.
    And clones or updates the Git repository if necessary.
    Args:
        customer (str): The customer name or identifier.
    Returns:
        tuple: A tuple containing two lists:
            - price_feed_providers: List of price feed provider instances.
            - token_providers: List of token validation provider instances.
    """
    ground_truth_config = QuorumConfiguration().load_customer_config(customer)
    git_manager = GitManager(customer, ground_truth_config)
    git_manager.clone_or_update()
    price_feed_providers = ground_truth_config.get("price_feed_providers", [])
    token_providers = ground_truth_config.get("token_validation_providers", [])
    return price_feed_providers, token_providers


def run_customer_local_validation(
    customer: str, chain: Chain, source_codes: list[SourceCode], payload_contract: str
) -> None:
    """
    Run local proposal validation for a specific customer and chain.
    This function performs a series of checks on the proposal address,
    including diff checks, global variable checks, explicit address checks,
    and new listing checks.
    Args:
        customer (str): The customer name or identifier.
        chain (Chain): The blockchain chain name.
        source_codes (list[SourceCode]): List of source code files.
    Returns:
        None
    """
    pp.pprint(
        f"Run local proposal validation for {customer} on {chain}",
        pp.Colors.INFO,
        pp.Heading.HEADING_1,
    )
    pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)
    # Load customer configuration
    price_feed_providers, token_providers = load_customer_config(customer)
    pp.pprint("Run Metadata", pp.Colors.INFO, pp.Heading.HEADING_2)
    pp.pprint(str(customer), pp.Colors.INFO)
    pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)
    # Perform checks
    perform_checks(
        customer=customer,
        chain=chain,
        proposal_id=payload_contract,
        source_codes=source_codes,
        price_feed_providers=price_feed_providers,
        token_providers=token_providers,
    )


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
        pp.pprint("Run Preparation", pp.Colors.INFO, pp.Heading.HEADING_1)
        price_feed_providers, token_providers = load_customer_config(
            customer=config.customer
        )
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

        pp.pprint("Run Metadata", pp.Colors.INFO, pp.Heading.HEADING_2)
        pp.pprint(str(config), pp.Colors.INFO)
        pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

        for pa in config.payload_addresses:
            proposals_check(
                customer=config.customer,
                chain=pa.chain,
                proposal_addresses=pa.addresses,
                price_feed_providers=price_feed_providers,
                token_providers=token_providers,
            )


def proposals_check(
    customer: str,
    chain: Chain,
    proposal_addresses: list[str],
    price_feed_providers: list[PriceFeedProviderBase],
    token_providers: list[PriceFeedProviderBase] | None = None,
) -> None:
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
        pp.pprint(
            f"Analyzing payload {proposal_address} on {chain}",
            pp.Colors.INFO,
            pp.Heading.HEADING_1,
        )

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

        perform_checks(
            customer=customer,
            chain=chain,
            proposal_id=proposal_address,
            source_codes=source_codes,
            price_feed_providers=price_feed_providers,
            token_providers=token_providers,
        )


def perform_checks(
    customer: str,
    chain: Chain,
    proposal_id: str,
    source_codes: list[SourceCode],
    price_feed_providers: list[PriceFeedProviderBase],
    token_providers: list[PriceFeedProviderBase] | None = None,
):
    """
    Perform a series of checks on the proposal address.
    This function orchestrates the execution of various checks on the proposal address,
    including diff checks, global variable checks, explicit address checks,
    and new listing checks.

    Args:
        customer (str): The customer name or identifier.
        chain (Chain): The blockchain chain name.
        proposal_id (str): The proposal address or local path to the proposal.
        source_codes (list[SourceCode]): List of source code files.
        price_feed_providers (list[PriceFeedProviderBase]): List of price feed providers.
        token_providers (list[PriceFeedProviderBase] | None): List of token validation providers.
    """

    # Diff check
    pp.pprint(
        "Check 1 - Comparing payload contract and imports with the source of truth",
        pp.Colors.INFO,
        pp.Heading.HEADING_2,
    )
    missing_files = Checks.DiffCheck(
        customer, chain, proposal_id, source_codes
    ).find_diffs()
    pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

    # Review diff check
    pp.pprint(
        "Check 2 - Verifying missing files against customer review repo",
        pp.Colors.INFO,
        pp.Heading.HEADING_2,
    )
    Checks.ReviewDiffCheck(customer, chain, proposal_id, missing_files).find_diffs()
    pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

    # Global variables check
    pp.pprint("Check 3 - Global variables", pp.Colors.INFO, pp.Heading.HEADING_2)
    Checks.GlobalVariableCheck(
        customer, chain, proposal_id, missing_files
    ).check_global_variables()
    pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

    # Feed price check
    pp.pprint(
        "Check 4 - Explicit addresses validation",
        pp.Colors.INFO,
        pp.Heading.HEADING_2,
    )
    Checks.PriceFeedCheck(
        customer,
        chain,
        proposal_id,
        missing_files,
        price_feed_providers,
        token_providers,
    ).verify_price_feed()
    pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)

    # New listing check
    pp.pprint(
        "Check 5 - First deposit for new listing",
        pp.Colors.INFO,
        pp.Heading.HEADING_2,
    )
    Checks.NewListingCheck(
        customer, chain, proposal_id, missing_files
    ).new_listing_check()
    pp.pprint(pp.SEPARATOR_LINE, pp.Colors.INFO)
