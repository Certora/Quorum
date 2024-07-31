import argparse
import difflib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass


from ProposalTools.GIT.GitManager import GitManager
from ProposalTools.API.APIManager import APIManager, Chain, SourceCode
import ProposalTools.config as config
import ProposalTools.Utils.PrettyPrinter as pp

@dataclass
class Compared:
    local_file: str
    proposal_file: str
    diff: str

def parse_args() -> tuple[str, Chain, str]:
    """
    Parse command line arguments for customer and proposal address.

    Returns:
        tuple[str, Chain, str]: A tuple containing the customer name, blockchain chain and proposal address.
    """
    parser = argparse.ArgumentParser(description="Fetch and compare smart contract source code.")
    parser.add_argument('--customer', type=str, required=True, help="Customer name or identifier.")
    parser.add_argument('--chain', type=Chain, choices=[chain.value for chain in Chain], default=Chain.ETH.value, help="Blockchain chain.")
    parser.add_argument('--proposal_address', type=str, required=True, help="Ethereum proposal address.")
    args = parser.parse_args()
    return args.customer, args.chain, args.proposal_address

def find_most_common_path(source_path: Path, repo: Path) -> Path | None:
    """
    Find the most common file path between a source path and a repository.

    Args:
        source_path (Path): The source file path from the remote repository.
        repo (Path): The local repository path.

    Returns:
        Path | None: The most common file path if found, otherwise None.
    """
    for i in range(len(source_path.parts)):
        current_source_path = Path(*source_path.parts[i:])
        local_files = list(repo.rglob(str(current_source_path)))
        if len(local_files) == 1:
            return local_files[0]
    return None

def find_diffs(customer: str, source_codes: list[SourceCode]) -> tuple[list[str], list[Compared]]:
    """
    Find and save differences between local and remote source codes.

    Args:
        customer (str): The customer name or identifier.
        source_codes (list[SourceCode]): List of source code objects from the remote repository.

    Returns:
        tuple[list[str], list[Compared]]: A tuple containing lists of missing files and files with differences.
    """
    missing_files = []
    files_with_diffs = []
    
    customer_folder = config.MAIN_PATH / customer
    target_repo = customer_folder / "modules"
    diffs_folder = customer_folder / "checks" / f"diffs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

def main() -> None:
    """
    Main function to fetch and compare smart contract source codes.

    This function initializes the Git manager, fetches the source codes
    from the Etherscan API, and finds differences between the local and remote source codes.
    """
    customer, chain, proposal_address = parse_args()

    git_manager = GitManager(customer)
    git_manager.clone_or_update()

    api = APIManager(chain)
    source_codes = api.get_source_code(proposal_address)

    missing_files, files_with_diffs = find_diffs(customer, source_codes)

    total_number_of_files = len(source_codes)
    number_of_missing_files = len(missing_files)
    number_of_files_with_diffs = len(files_with_diffs)

    msg = f"Compared {total_number_of_files - number_of_missing_files}/{total_number_of_files} files"
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

if __name__ == "__main__":
    main()
