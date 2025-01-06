import argparse
from typing import Dict, Any

from Quorum.checks.proposal_check import run_customer_proposal_validation, ProposalConfig


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
    config_data: Dict[str, Any] = args.config
    prop_config = ProposalConfig(**config_data)
    run_customer_proposal_validation(prop_config)
