import argparse
import tempfile
from pathlib import Path

import quorum.utils.pretty_printer as pp
from quorum.apis.block_explorers.source_code import SourceCode
from quorum.checks.proposal_check import run_customer_local_validation
from quorum.utils.change_directory import change_directory
from quorum.utils.compile import compile_source_code


def get_source_codes(
    forge_root_path: Path, source_file_paths: list[str]
) -> list[SourceCode]:
    """
    Retrieve the source code from the specified file paths.

    Args:
        forge_root_path (Path): Path to the forge root directory.
        source_file_paths (list[str]): List of source file paths.

    Returns:
        list[SourceCode]: A list of SourceCode objects containing the file names and content.

    """
    source_codes = []
    with change_directory(forge_root_path):
        for source_file_path in source_file_paths:
            try:
                with open(source_file_path) as file:
                    content = file.read().splitlines()
                    source_codes.append(
                        SourceCode(file_name=source_file_path, file_content=content)
                    )
            except Exception as e:
                pp.pprint(
                    f"Error reading source file {source_file_path} the file wont be checked!!: {e}",
                    status=pp.Colors.FAILURE,
                    heading="File Read Error",
                )
                continue

    return source_codes


def run_local_proposal(args: argparse.Namespace) -> None:
    """
    Run a single proposal check in a local mode.

    Args:
        args (argparse.Namespace): Command line arguments containing:
            - customer (str): The customer identifier
            - chain (str): The blockchain network identifier
            - forge_root_path (str): Path to the forge root directory
            - contract_proposal_path (str): Path to the contract proposal file
    """
    protocol_name, chain, forge_root_path, contract_proposal_path = (
        args.protocol_name,
        args.chain,
        args.forge_root_path,
        args.contract_proposal_path,
    )

    with tempfile.TemporaryDirectory(prefix="quorum-forge-") as tmp:
        source_file_paths, _ = compile_source_code(
            forge_root_path, contract_proposal_path, tmp
        )
        source_codes = get_source_codes(forge_root_path, source_file_paths)

    run_customer_local_validation(
        customer=protocol_name,
        chain=chain,
        source_codes=source_codes,
        payload_contract=str(contract_proposal_path),
    )
