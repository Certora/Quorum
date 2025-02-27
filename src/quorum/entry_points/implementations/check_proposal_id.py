import argparse

import quorum.utils.pretty_printer as pp
from quorum.apis.governance.aave_governance import (
    AaveGovernanceAPI,
    ChainNotFoundException,
    ProposalNotFoundException,
)
from quorum.checks.proposal_check import (
    CustomerConfig,
    ProposalConfig,
    run_customer_proposal_validation,
)

CUSTOMER_TO_API = {"aave": AaveGovernanceAPI()}


def run_proposal_id(args: argparse.Namespace) -> None:
    """
    Executes proposal validation for a specific customer and proposal ID.

    This function retrieves payload addresses for a given proposal and runs batch validation
    using the customer's API configuration.

    Args:
        args (argparse.Namespace): Command line arguments containing:
            - customer (str): Name of the customer to validate proposal for
            - proposal_id (str/int): ID of the proposal to validate

    Raises:
        ValueError: If the provided customer is not supported in CUSTOMER_TO_API mapping

    Returns:
        None
    """
    protocol_name, proposal_id = args.protocol_name, args.proposal_id
    customer_key = protocol_name.lower()
    if customer_key not in CUSTOMER_TO_API:
        raise ValueError(
            f"Customer '{protocol_name}' is not supported. Supported customers: {list(CUSTOMER_TO_API.keys())}."
        )

    api = CUSTOMER_TO_API[customer_key]
    try:
        payloads_addresses = api.get_all_payloads_addresses(proposal_id)
    except (ProposalNotFoundException, ChainNotFoundException) as e:
        pp.pprint(e, pp.Colors.FAILURE)
        return
    config = ProposalConfig(
        customers_config=[
            CustomerConfig(customer=protocol_name, payload_addresses=payloads_addresses)
        ]
    )

    run_customer_proposal_validation(config)
