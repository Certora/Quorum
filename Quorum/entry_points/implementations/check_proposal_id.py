import argparse

from Quorum.apis.git_api.git_manager import GitManager
from Quorum.apis.governance.aave_governance import AaveGovernanceAPI
from Quorum.checks.proposal_check import proposals_check
import Quorum.utils.config_loader as ConfigLoader


CUSTOMER_TO_API = {
    "aave": AaveGovernanceAPI()
}


def run_proposal_id(args: argparse.Namespace) -> None:
    """
    Executes a validation process for a given proposal ID associated with a specific customer.

    This function performs several key operations:
    1. Validates the customer and retrieves their governance API
    2. Fetches payload addresses for the given proposal ID
    3. Loads customer configuration and sets up git repositories
    4. Performs proposal checks for each payload

    Args:
        args (argparse.Namespace): Command line arguments containing:
            - customer (str): The identifier of the customer
            - proposal_id (str/int): The ID of the proposal to check

    Raises:
        ValueError: If the specified customer is not supported

    Example:
        args = argparse.Namespace(customer='example', proposal_id='123')
        run_proposal_id(args)
    """

    # Parse command-line arguments
    customer, proposal_id = args.customer, args.proposal_id

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
