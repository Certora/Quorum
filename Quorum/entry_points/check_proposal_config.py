"""
Quorum JSON Configuration Proposal Analyzer

This script is designed to fetch and compare smart contract source code based on a JSON configuration file
for various customers and their respective blockchain chains. The workflow includes:

1. Parsing command-line arguments to obtain the path to a JSON configuration file.
2. Loading the ground truth configuration for each specified customer.
3. Cloning or updating necessary Git repositories based on the configuration.
4. Executing a series of proposal checks on the provided proposal addresses to ensure integrity and compliance.

Usage:
    python check_proposal_config.py --config <CONFIG_FILE_PATH>

Example:
    python check_proposal_config.py --config execution.json
"""

import argparse
from typing import Dict, Any

from Quorum.apis.git_api.git_manager import GitManager
from Quorum.checks.proposal_check import proposals_check
import Quorum.utils.config_loader as ConfigLoader
import Quorum.utils.arg_validations as arg_valid
from Quorum.utils.chain_enum import Chain


def parse_args() -> Dict[str, Any]:
    """
    Parses command-line arguments required for executing proposal analysis based on a JSON configuration file.

    This function utilizes Python's argparse module to define and parse the necessary command-line
    arguments:
        --config: Path to the JSON configuration file containing customer and proposal details.

    Returns:
        dict: Parsed JSON data from the configuration file.

    Raises:
        argparse.ArgumentError: If the provided configuration file path is invalid or the file cannot be loaded.
    """
    parser = argparse.ArgumentParser(
        description="Fetch and compare smart contract source code based on a JSON configuration file."
    )
    parser.add_argument(
        '--config',
        type=arg_valid.load_config,
        required=True,
        help="Path to the JSON configuration file."
    )
    args = parser.parse_args()

    return args.config


def main() -> None:
    """
    Main execution function that orchestrates fetching, cloning/updating repositories,
    and performing proposal checks based on the provided JSON configuration file.

    Workflow:
        1. Parse command-line arguments to retrieve the configuration data.
        2. Iterate over each customer and their associated chain and proposal information.
        3. Load the ground truth configuration for each customer.
        4. Initialize GitManager with customer and configuration, then clone or update repositories.
        5. Retrieve price feed providers from the configuration.
        6. Execute proposal checks for each set of proposal addresses on the specified chains.

    Raises:
        ValueError: If the specified customer is not supported.
        FileNotFoundError: If the customer configuration file does not exist.
        requests.HTTPError: If any of the HTTP requests to fetch data fail.
    """
    # Parse command-line arguments to get the configuration data
    config_data: Dict[str, Any] = parse_args()

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


if __name__ == "__main__":
    main()
