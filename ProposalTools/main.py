import argparse
import difflib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Optional
import json

from ProposalTools.GIT.GitManager import GitManager
from ProposalTools.API.APIManager import APIManager, Chain, SourceCode
import ProposalTools.config as config
import ProposalTools.Utils.PrettyPrinter as pp

@dataclass
class Compared:
    local_file: str
    proposal_file: str
    diff: str

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
        pp.pretty_print(f"No execution config supplied, will execute in single Task mode", pp.Colors.INFO)
        return None

def find_most_common_path(source_path: Path, repo: Path) -> Optional[Path]:
    """
    Find the most common file path between a source path and a repository.

    Args:
        source_path (Path): The source file path from the remote repository.
        repo (Path): The local repository path.

    Returns:
        Optional[Path]: The most common file path if found, otherwise None.
    """
    for i in range(len(source_path.parts)):
        current_source_path = Path(*source_path.parts[i:])
        local_files = list(repo.rglob(str(current_source_path)))
        if len(local_files) == 1:
            return local_files[0]
    return None

def find_diffs(customer: str, source_codes: list[SourceCode], proposal_address: str) -> tuple[list[str], list[Compared]]:
    """
    Find and save differences between local and remote source codes.

    Args:
        customer (str): The customer name or identifier.
        source_codes (list[SourceCode]): List of source code objects from the remote repository.
        proposal_address (str): The Ethereum proposal address (for diff path structure).

    Returns:
        tuple[list[str], list[Compared]]: A tuple containing lists of missing files and files with differences.
    """
    missing_files = []
    files_with_diffs = []
    
    customer_folder = config.MAIN_PATH / customer
    target_repo = customer_folder / "modules"
    diffs_folder = customer_folder / "checks" / proposal_address / f"diffs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    diffs_folder.mkdir(parents=True, exist_ok=True)
    pp.pretty_print(f"Created differences folder:\n{diffs_folder}", pp.Colors.INFO)
    
    for source_code in source_codes:
        local_file = find_most_common_path(Path(source_code.file_name), target_repo)
        if not local_file:
            missing_files.append(source_code.file_name)
            continue

        local_content = local_file.read_text().splitlines()
        remote_content = source_code.file_content

        diff = difflib.unified_diff(local_content, remote_content, fromfile=str(local_file), tofile=source_code.file_name)
        diff_text = '\n'.join(diff)

        if diff_text:
            diff_file_path = diffs_folder / f"{local_file.stem}.patch"
            files_with_diffs.append(Compared(str(local_file), source_code.file_name, str(diff_file_path)))
            with open(diff_file_path, "w") as diff_file:
                diff_file.write(diff_text)
    
    return missing_files, files_with_diffs

def process_task(customer: str, chain_name: str, proposal_addresses: list[str]) -> None:
    """
    Process the task for a given customer, chain, and list of proposal addresses.

    Args:
        customer (str): The customer name or identifier.
        chain_name (str): The blockchain chain name.
        proposal_addresses (list[str]): List of proposal addresses.
    """
    chain = Chain[chain_name.upper()]
    git_manager = GitManager(customer)
    git_manager.clone_or_update()

    api = APIManager(chain)
    for proposal_address in proposal_addresses:
        pp.pretty_print(f"Processing proposal {proposal_address}", pp.Colors.INFO)
        source_codes = api.get_source_code(proposal_address)
        missing_files, files_with_diffs = find_diffs(customer, source_codes, proposal_address)

        total_number_of_files = len(source_codes)
        number_of_missing_files = len(missing_files)
        number_of_files_with_diffs = len(files_with_diffs)

        msg = f"Compared {total_number_of_files - number_of_missing_files}/{total_number_of_files} files for proposal {proposal_address}"
        if number_of_missing_files == 0:
            pp.pretty_print(msg, pp.Colors.SUCCESS)
        else:
            pp.pretty_print(msg, pp.Colors.WARNING)
            for file_name in missing_files:
                pp.pretty_print(f"Missing file: {file_name} in local repo", pp.Colors.WARNING)
        
        if number_of_files_with_diffs == 0:
            pp.pretty_print("No differences found.", pp.Colors.SUCCESS)
        else:
            pp.pretty_print(f"Found differences in {number_of_files_with_diffs} files", pp.Colors.FAILURE)
            for compared_pair in files_with_diffs:
                pp.pretty_print(f"Local: {compared_pair.local_file}\nProposal: {compared_pair.proposal_file}\nDiff: {compared_pair.diff}", pp.Colors.FAILURE)

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
            for chain_name, proposals in chain_info.items():
                if proposals["Proposals"]: 
                    process_task(customer, chain_name, proposals["Proposals"])
    else:
        # Single-task mode using command line arguments
        if not (customer and chain_name and proposal_address):
            raise ValueError("Customer, chain, and proposal_address must be specified if not using a config file.")
        process_task(customer, chain_name, [proposal_address])

if __name__ == "__main__":
    main()
