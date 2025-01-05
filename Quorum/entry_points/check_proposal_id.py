"""
Quorum Proposal Analyzer

This script is designed to fetch and compare smart contract source code for a specific proposal ID
associated with a designated customer on a chosen blockchain chain. The workflow includes:

1. Parsing command-line arguments to obtain the customer identifier and proposal ID.
2. Validating the customer against supported APIs.
3. Fetching all payload addresses related to the proposal using the appropriate governance API.
4. Loading the ground truth configuration for the specified customer.
5. Cloning or updating necessary Git repositories based on the configuration.
6. Executing a series of checks on each payload's smart contract source code to ensure integrity and compliance.

Usage:
    python check_proposal_id.py --customer <CUSTOMER_NAME> --proposal_id <PROPOSAL_ID>

Example:
    python check_proposal_id.py --customer Aave --proposal_id 12345
"""

import argparse
from typing import Tuple

from Quorum.apis.git_api.git_manager import GitManager
from Quorum.apis.governance.aave_governance import AaveGovernanceAPI
from Quorum.checks.proposal_check import proposals_check
import Quorum.utils.config_loader as ConfigLoader


# Mapping of supported customers to their corresponding governance API instances.
# This allows for easy extension to support additional customers in the future.
CUSTOMER_TO_API = {
    "aave": AaveGovernanceAPI()
}


def parse_args() -> Tuple[str, int]:
    """
    Parses command-line arguments required for executing proposal analysis.

    This function utilizes Python's argparse module to define and parse the necessary command-line
    arguments:
        --customer: Name or identifier of the customer.
        --proposal_id: ID of the proposal to analyze.

    Returns:
        A tuple containing:
            customer (str): Customer name or identifier.
            proposal_id (int): Proposal ID.

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
        help="Customer name or identifier (e.g., 'Aave')."
    )
    parser.add_argument(
        '--proposal_id',
        type=int,
        required=True,
        help="Proposal ID to analyze (integer value)."
    )
    args = parser.parse_args()

    return args.customer, args.proposal_id


def main() -> None:
    """
    Main execution function that orchestrates fetching, cloning/updating repositories,
    and performing proposal checks based on the provided command-line arguments.

    Workflow:
        1. Parse command-line arguments to retrieve customer and proposal ID.
        2. Validate the customer against supported APIs.
        3. Fetch all payload addresses associated with the proposal ID using the governance API.
        4. Load the ground truth configuration for the specified customer.
        5. Initialize GitManager with customer and configuration, then clone or update repositories.
        6. Retrieve price feed providers from the configuration.
        7. Execute proposal checks for each set of payload addresses.

    Raises:
        ValueError: If the specified customer is not supported.
        FileNotFoundError: If the customer configuration file does not exist.
        requests.HTTPError: If any of the HTTP requests to fetch data fail.
    """
    # Parse command-line arguments
    customer, proposal_id = parse_args()

    # Normalize customer identifier to lowercase for consistent mapping
    customer_key = customer.lower()

    # Validate if the specified customer is supported
    if customer_key not in CUSTOMER_TO_API:
        raise ValueError(f"Customer '{customer}' is not supported. Supported customers: {list(CUSTOMER_TO_API.keys())}.")

    # Retrieve the appropriate governance API instance for the customer
    api = CUSTOMER_TO_API[customer_key]

    # Fetch all payload addresses associated with the given proposal ID
    payloads_addresses = api.get_all_payloads_addresses(proposal_id)

    # Load the ground truth configuration for the specified customer
    ground_truth_config = ConfigLoader.load_customer_config(customer)

    # Initialize GitManager with customer and configuration, then clone or update repositories
    git_manager = GitManager(customer, ground_truth_config)
    git_manager.clone_or_update()

    # Retrieve price feed providers from the configuration, defaulting to an empty list if not specified
    price_feed_providers = ground_truth_config.get("price_feed_providers", [])

    # Iterate over each payload's data and perform proposal checks
    for payload_data in payloads_addresses:
        """
        payload_data is expected to be an object with at least the following attributes:
            - chain: The blockchain chain associated with the payload.
            - addresses: A list of smart contract addresses associated with the payload.
        """
        proposals_check(
            customer=customer,
            chain=payload_data.chain,
            proposal_addresses=payload_data.addresses,
            providers=price_feed_providers
        )


if __name__ == "__main__":
    main()
