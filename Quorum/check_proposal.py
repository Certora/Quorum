import argparse
import json
from typing import Any, Optional

from Quorum.utils.chain_enum import Chain
from Quorum.apis.git_api.git_manager import GitManager
from Quorum.apis.price_feeds.price_feed_utils import PriceFeedProviderBase
from Quorum.apis.block_explorers.chains_api import ChainAPI
import Quorum.checks as Checks
import Quorum.utils.pretty_printer as pp
import Quorum.utils.config_loader as ConfigLoader
import Quorum.utils.arg_validations as arg_valid


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
    parser.add_argument('--chain', type=Chain, choices=[chain.value for chain in Chain], help="Blockchain chain.")
    parser.add_argument('--proposal_address', type=arg_valid.validate_address, help="Ethereum proposal address.")
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
        pp.pprint(f"Failed to parse given config file {config_path}:\n{e}", pp.Colors.FAILURE)


def proposals_check(customer: str, chain: Chain, proposal_addresses: list[str], providers: list[PriceFeedProviderBase]) -> None:
    """
    Check and compare source code files for given proposals.

    This function handles the main logic of fetching source code from the remote repository.

    Args:
        customer (str): The customer name or identifier.
        chain_name (str): The blockchain chain name.
        proposal_addresses (list[str]): List of proposal addresses.
        providers (list[PriceFeedProviderInterface]): List of price feed providers.
    """
    api = ChainAPI(chain)
    
    for proposal_address in proposal_addresses:
        pp.pprint(f'Analyzing payload {proposal_address}', pp.Colors.INFO)

        try:
            source_codes = api.get_source_code(proposal_address)
        except ValueError as _:
            error_message = (
                f'Payload address {proposal_address} is not verified on {chain.name} explorer.\n'
                'We do not recommend to approve this proposal until the code is approved!\n'
                'Try contacting the proposer and ask them to verify the contract.\n'
                'No further checks are being performed on this payload.'
            )
            pp.pprint(error_message, pp.Colors.FAILURE)
            # Skip further checks for this proposal 
            continue

        # Diff check
        pp.pprint('Check 1 - Comparing payload contract and imports with the source of truth', pp.Colors.INFO)
        missing_files = Checks.DiffCheck(customer, chain, proposal_address, source_codes).find_diffs()
        
        # Review diff check
        pp.pprint(f'Check 2 - Verifying missing files against customer review repo', pp.Colors.INFO)
        Checks.ReviewDiffCheck(customer, chain, proposal_address, missing_files).find_diffs()

        # Global variables check
        pp.pprint('Check 3 - Global variables', pp.Colors.INFO)
        Checks.GlobalVariableCheck(customer, chain, proposal_address, missing_files).check_global_variables()

        # Feed price check
        pp.pprint('Check 4 - Explicit addresses validation', pp.Colors.INFO)
        Checks.PriceFeedCheck(customer, chain, proposal_address, missing_files, providers).verify_price_feed()

        # New listing check
        pp.pprint('Check 5 - First deposit for new listing', pp.Colors.INFO)
        Checks.NewListingCheck(customer, chain, proposal_address, missing_files).new_listing_check()


def main() -> None:
    """
    Main function to execute tasks based on command line arguments or JSON configuration.

    This function determines whether to run in single-task mode using command line arguments
    or multi-task mode using a JSON configuration file.
    """
    config_data, customer, chain, proposal_address = parse_args()

    if config_data:
        # Multi-task mode using JSON configuration
        for customer, chain_info in config_data.items():
            pp.pprint('Run Preparation', pp.Colors.INFO)
            ground_truth_config = ConfigLoader.load_customer_config(customer)
            GitManager(customer, ground_truth_config).clone_or_update()
            price_feed_providers = ground_truth_config.get("price_feed_providers", [])
            pp.pprint('Run Metadata', pp.Colors.INFO)
            pp.pprint(f'Customer: {customer}\nChains and payloads:\n{chain_info}', pp.Colors.INFO)
            for chain, proposals in chain_info.items():
                # Validate chain is supported by cast to Chain enum
                chain = Chain(chain)
                if proposals["Proposals"]: 
                    proposals_check(customer, chain, proposals["Proposals"], price_feed_providers)
    else:
        # Single-task mode using command line arguments
        if not (customer and chain and proposal_address):
            raise ValueError("Customer, chain, and proposal_address must be specified if not using a config file.")
        pp.pprint('Run Preparation', pp.Colors.INFO)
        ground_truth_config = ConfigLoader.load_customer_config(customer)
        GitManager(customer, ground_truth_config).clone_or_update()
        price_feed_providers = ground_truth_config.get("price_feed_providers", [])
        pp.pprint('Run Metadata', pp.Colors.INFO)
        pp.pprint(f'Customer: {customer}\nChains and payloads:\n{chain}: {proposal_address}', pp.Colors.INFO)
        proposals_check(customer, chain, [proposal_address], price_feed_providers)


if __name__ == "__main__":
    main()
