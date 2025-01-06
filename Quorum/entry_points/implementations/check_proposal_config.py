import argparse
from typing import Any

from Quorum.checks.proposal_check import (
    run_customer_proposal_validation,
    ProposalConfig,
    CustomerConfig,
    PayloadAddresses
)


def run_config(args: argparse.Namespace) -> None:
    """
    Execute configuration for proposal validation.

    This function takes command line arguments containing configuration data,
    creates a ProposalConfig object, and runs batch processing with the configuration.

    Args:
        args (argparse.Namespace): Command line arguments containing the config data.
                                 Expected to have a 'config' attribute with proposal
                                 configuration dictionary.

    Returns:
        None

    Raises:
        TypeError: If config_data cannot be unpacked into ProposalConfig
    """
    config_data: dict[str, Any] = args.config
    customers_config: list[CustomerConfig] = []

    for customer_name, chains in config_data.items():
        payload_addresses: list[PayloadAddresses] = []
        
        for chain_name, proposals in chains.items():
            proposal_addresses = proposals.get("Proposals", [])
            payload_addresses.append(
                PayloadAddresses(
                    chain=chain_name,
                    addresses=proposal_addresses
                )
            )
        
        customers_config.append(
            CustomerConfig(
                customer=customer_name,
                payload_addresses=payload_addresses
            )
        )
    
    prop_config = ProposalConfig(customers_config=customers_config)
    run_customer_proposal_validation(prop_config)
