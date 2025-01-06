import argparse

from Quorum.checks.proposal_check import run_customer_proposal_validation, ProposalConfig, CustomerConfig, PayloadAddresses


def run_single(args: argparse.Namespace) -> None:
    """
    Run a single proposal check for a specific customer and chain.

    Args:
        args (argparse.Namespace): Command line arguments containing:
            - customer (str): The customer identifier
            - chain (str): The blockchain network identifier
            - proposal_address (str): The address of the proposal to check

    The function creates customer and proposal configurations based on the input arguments
    and executes a batch run for the single proposal.
    """
    customer, chain, proposal_address = args.customer, args.chain, args.proposal_address
    customer_config = CustomerConfig(customer=customer, payload_addresses=[PayloadAddresses(chain=chain, addresses=[proposal_address])])
    prop_config = ProposalConfig(customers_config=[customer_config])
    run_customer_proposal_validation(prop_config)
