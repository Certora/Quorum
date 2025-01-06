import argparse
from typing import Dict, Any

from Quorum.apis.git_api.git_manager import GitManager
from Quorum.checks.proposal_check import proposals_check
import Quorum.utils.config_loader as ConfigLoader
from Quorum.utils.chain_enum import Chain


def run_config(args: argparse.Namespace) -> None:
    """
    Processes and validates proposal configurations for different customers across blockchain networks.

    This function takes command-line arguments containing configuration data and performs the following:
    - Loads ground truth configurations for each customer
    - Manages Git repositories through GitManager
    - Validates blockchain chains
    - Executes proposal checks for specified addresses

    Args:
        args (argparse.Namespace): Command-line arguments containing the configuration data
                                 in args.config as a dictionary

    Returns:
        None

    Raises:
        ValueError: If an unsupported or invalid blockchain chain is specified

    Example config_data structure:
        {
            "customer_name": {
                "chain_name": {
                    "Proposals": ["0x123...", "0x456..."]
                }
            }
        }
    """
    # Parse command-line arguments to get the configuration data
    config_data: Dict[str, Any] = args.config

    # Iterate over each customer and their respective chain and proposal information in the config
    for customer, chain_info in config_data.items():
        # Load the ground truth configuration for the specified customer
        ground_truth_config = ConfigLoader.load_customer_config(customer)

        # Initialize GitManager with customer and configuration, then clone or update repositories
        git_manager = GitManager(customer, ground_truth_config)
        git_manager.clone_or_update()

        # Retrieve price feed providers from the configuration, defaulting to an empty list if not specified
        price_feed_providers = ground_truth_config.get("price_feed_providers", [])

        # Iterate over each blockchain chain and its associated proposals for the customer
        for chain, proposals in chain_info.items():
            try:
                # Validate and convert the chain identifier to the Chain enum
                chain_enum = Chain(chain)
            except ValueError as e:
                # Handle unsupported or invalid chain identifiers
                raise ValueError(f"Unsupported or invalid chain '{chain}' for customer '{customer}': {e}")

            # Check if there are any proposals to process for the current chain
            if proposals.get("Proposals"):
                # Execute proposal checks for the specified customer, chain, and proposal addresses
                proposals_check(
                    customer=customer,
                    chain=chain_enum,
                    proposal_addresses=proposals["Proposals"],
                    providers=price_feed_providers
                )
