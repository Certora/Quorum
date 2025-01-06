import argparse

from Quorum.apis.git_api.git_manager import GitManager
from Quorum.checks.proposal_check import proposals_check
import Quorum.utils.config_loader as ConfigLoader

def run_single(args: argparse.Namespace) -> None:
    """
    Execute proposal verification for a single proposal address.

    This function processes a single proposal check by initializing necessary configurations
    and git repositories, then performs validation checks on the specified proposal.

    Args:
        args (argparse.Namespace): Command line arguments containing:
            - customer (str): Customer identifier
            - chain (str): Blockchain network identifier
            - proposal_address (str): Address of the proposal to check

    Raises:
        ValueError: If any of the required arguments (customer, chain, proposal_address) are missing

    Example:
        args = argparse.Namespace(
            customer='example_customer',
            chain='ethereum',
            proposal_address='0x1234...'
        run_single(args)
    """
    # Parse command-line arguments
    customer, chain, proposal_address = args.customer, args.chain, args.proposal_address

    # Ensure all required arguments are provided
    if not (customer and chain and proposal_address):
        raise ValueError(
            "Customer, chain, and proposal_address must be specified."
            " Provide all three arguments when not using a config file."
        )

    # Load the customer's ground truth configuration
    ground_truth_config = ConfigLoader.load_customer_config(customer)

    # Initialize GitManager with customer and configuration, then clone or update repositories
    git_manager = GitManager(customer, ground_truth_config)
    git_manager.clone_or_update()

    # Retrieve price feed providers from the configuration
    price_feed_providers = ground_truth_config.get("price_feed_providers", [])

    # Execute proposal checks
    proposals_check(
        customer=customer,
        chain=chain,
        proposal_addresses=[proposal_address],
        providers=price_feed_providers
    )
