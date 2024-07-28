import argparse
import difflib
from pathlib import Path

from ProposalTools.GIT.GitManager import GitManager
from ProposalTools.APIs.AbsSourceCode import SourceCodeInterface, SourceCode
from ProposalTools.APIs.ETHScan.ETHScanAPI import ETHScanAPI
import ProposalTools.config as config


def parse_args() -> tuple[str, str]:
    """
    Parse command line arguments for customer and proposal address.

    Returns:
        tuple[str, str]: A tuple containing the customer name and proposal address.
    """
    parser = argparse.ArgumentParser(description="Fetch and compare smart contract source code.")
    parser.add_argument('--customer', type=str, required=True, help="Customer name or identifier.")
    parser.add_argument('--proposal_address', type=str, required=True, help="Ethereum proposal address.")
    args = parser.parse_args()
    return args.customer, args.proposal_address

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

def find_diffs(customer: str, source_codes: list[SourceCode]) -> None:
    """
    Find and save differences between local and remote source codes.

    Args:
        customer (str): The customer name or identifier.
        source_codes (list[SourceCode]): List of source code objects from the remote repository.
    """
    target_repo = config.MAIN_PATH / customer
    diffs_folder = target_repo / "diffs"
    diffs_folder.mkdir(parents=True, exist_ok=True)

    for source_code in source_codes:
        local_file = find_most_common_path(Path(source_code.file_name), target_repo)
        if not local_file:
            print(f"No local file found for {source_code.file_name}. Check it!")
            continue

        local_content = local_file.read_text().splitlines()
        remote_content = source_code.file_content

        diff = difflib.unified_diff(local_content, remote_content, fromfile=str(local_file), tofile=source_code.file_name)
        diff_text = '\n'.join(diff)

        if not diff_text:
            continue
        
        diff_file_path = diffs_folder / f"{local_file.stem}.patch"
        with open(diff_file_path, "w") as diff_file:
            diff_file.write(diff_text)

def main() -> None:
    """
    Main function to fetch and compare smart contract source codes.

    This function initializes the Git manager, fetches the source codes
    from the Etherscan API, and finds differences between the local and remote source codes.
    """
    customer, proposal_address = parse_args()

    git_manager = GitManager(customer)
    git_manager.clone_or_update()

    api: SourceCodeInterface = ETHScanAPI()
    source_codes = api.get_source_code(proposal_address)
    print(f"Fetched {len(source_codes)} source files for comparison.")

    find_diffs(customer, source_codes)

if __name__ == "__main__":
    main()
