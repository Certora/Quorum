"""
Quorum Proposal Checker

This script is designed to fetch and compare smart contract source code for a specific proposal address
on a chosen blockchain chain for a designated customer. The workflow includes:

1. Parsing command-line arguments to obtain the customer identifier, blockchain chain, and proposal address.
2. Loading the ground truth configuration for the specified customer.
3. Cloning or updating necessary Git repositories based on the configuration.
4. Executing a series of checks on the proposal's smart contract source code to ensure integrity and compliance.

Usage:
    python check_proposal.py --customer <CUSTOMER_NAME> --chain <CHAIN> --proposal_address <PROPOSAL_ADDRESS>

Example:
    python check_proposal.py --customer Aave --chain Ethereum --proposal_address 0x1234567890abcdef1234567890abcdef12345678
"""

import argparse
from typing import Tuple

from Quorum.utils.chain_enum import Chain
from Quorum.apis.git_api.git_manager import GitManager
from Quorum.checks.proposal_check import proposals_check
import Quorum.utils.config_loader as ConfigLoader
import Quorum.utils.arg_validations as arg_valid


def parse_args() -> Tuple[str, Chain, str]:
    """
    Parses command-line arguments required for executing proposal checks.

    This function utilizes Python's argparse module to define and parse the necessary command-line
    arguments:
        --customer: Name or identifier of the customer.
        --chain: Blockchain chain to target, must be one of the defined Chain enum values.
        --proposal_address: Ethereum proposal address, validated using `arg_valid.validate_address`.

    Returns:
        A tuple containing:
            customer (str): Customer name or identifier.
            chain (Chain): Selected blockchain chain.
            proposal_address (str): Validated Ethereum proposal address.

    Raises:
        argparse.ArgumentError: If required arguments are missing or invalid.
    """
    parser = argparse.ArgumentParser(
        description="Fetch and compare smart contract source code for a given proposal."
    )
    parser.add_argument(
        '--customer',
        type=str,
        required=True,
        help="Customer name or identifier."
    )
    parser.add_argument(
        '--chain',
        type=Chain,
        choices=list(Chain),
        required=True,
        help="Blockchain chain to target."
    )
    parser.add_argument(
        '--proposal_address',
        type=arg_valid.validate_address,
        required=True,
        help="Ethereum proposal address (e.g., 0x...)."
    )
    args = parser.parse_args()

    return args.customer, args.chain, args.proposal_address


def main() -> None:
    """
    Main execution function that orchestrates fetching, cloning/updating repositories,
    and performing proposal checks based on the provided command-line arguments.

    Workflow:
        1. Parse command-line arguments to retrieve customer, chain, and proposal address.
        2. Load the ground truth configuration for the specified customer.
        3. Initialize and update Git repositories as per the configuration.
        4. Execute the proposal checks for the provided proposal address using the loaded configuration.

    Raises:
        ValueError: If any of the required arguments (customer, chain, proposal_address) are missing.
        FileNotFoundError: If the customer configuration file does not exist.
        requests.HTTPError: If any of the HTTP requests to fetch data fail.
    """
    # Parse command-line arguments
    customer, chain, proposal_address = parse_args()

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


if __name__ == "__main__":
    main()
