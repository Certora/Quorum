import argparse
import json
from typing import Any, Optional

from Quorum.utils.chain_enum import Chain
import Quorum.utils.pretty_printer as pp
from Quorum.apis.git_api.git_manager import GitManager
from Quorum.apis.block_explorers.chains_api import ChainAPI
import Quorum.checks as Checks


def parse_args() -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Parse command line arguments for JSON configuration file or individual task parameters.

    Returns:
        tuple[Optional[str], Optional[str], Optional[str], Optional[str]]: 
        A tuple containing the path to the JSON configuration file, customer name, chain name, and proposal address.
    """
    parser = argparse.ArgumentParser(description="Fetch and compare smart contract source code.")
    parser.add_argument('--config', type=load_config, help="Path to JSON configuration file.")
    parser.add_argument('--customer', type=str, help="Customer name or identifier.")
    parser.add_argument('--chain', type=str, choices=[chain.value for chain in Chain], help="Blockchain chain.")
    parser.add_argument('--proposal_address', type=str, help="Ethereum proposal address.")
    args = parser.parse_args()

    return args.config, args.customer, args.chain, args.proposal_address


def load_config(config_path: str) -> dict[str, Any] | None:
    """
    Load and parse the JSON configuration file.

    Args:
        config_path (str): Path to the JSON configuration file.

    Returns:
        dict[str, Any]: Parsed JSON data.
    """
    try:
        with open(config_path, 'r') as file:
            config_data = json.load(file)
        return config_data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        pp.pretty_print(f"Failed to parse given config file {config_path}:\n{e}", pp.Colors.FAILURE)


def proposals_check(customer: str, chain_name: str, proposal_addresses: list[str]) -> None:
    """
    Check and compare source code files for given proposals.

    This function handles the main logic of fetching source code from the remote repository.

    Args:
        customer (str): The customer name or identifier.
        chain_name (str): The blockchain chain name.
        proposal_addresses (list[str]): List of proposal addresses.
    """
    chain = Chain[chain_name.upper()]
    api = ChainAPI(chain)
    
    pp.pretty_print(f"Processing customer {customer}, for chain: {chain}", pp.Colors.INFO)
    for proposal_address in proposal_addresses:
        pp.pretty_print(f"Processing proposal {proposal_address}", pp.Colors.INFO)
        source_codes = api.get_source_code(proposal_address)

        # Diff check
        missing_files = Checks.DiffCheck(customer, chain, proposal_address, source_codes).find_diffs()

        # Review diff check
        Checks.ReviewDiffCheck(customer, chain, proposal_address, missing_files).find_diffs()

        # Global variables check
        Checks.GlobalVariableCheck(customer, chain, proposal_address, missing_files).check_global_variables()

        # Feed price check
        Checks.FeedPriceCheck(customer, chain, proposal_address, missing_files).verify_price_feed()

        # New listing check
        Checks.NewListingCheck(customer, chain, proposal_address, missing_files).new_listing_check()

def main() -> None:
    """
    Main function to execute tasks based on command line arguments or JSON configuration.

    This function determines whether to run in single-task mode using command line arguments
    or multi-task mode using a JSON configuration file.
    """
    config_data, customer, chain_name, proposal_address = parse_args()

    if config_data:
        # Multi-task mode using JSON configuration
        for customer, chain_info in config_data.items():
            GitManager(customer).clone_or_update()
            for chain_name, proposals in chain_info.items():
                if proposals["Proposals"]: 
                    proposals_check(customer, chain_name, proposals["Proposals"])
    else:
        # Single-task mode using command line arguments
        if not (customer and chain_name and proposal_address):
            raise ValueError("Customer, chain, and proposal_address must be specified if not using a config file.")
        
        GitManager(customer).clone_or_update()    
        proposals_check(customer, chain_name, [proposal_address])


if __name__ == "__main__":
    main()
