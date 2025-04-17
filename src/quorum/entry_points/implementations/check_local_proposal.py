import argparse
import json
import subprocess
from pathlib import Path

import quorum.utils.pretty_printer as pp
from quorum.apis.block_explorers.source_code import SourceCode
from quorum.checks.proposal_check import run_customer_local_validation
from quorum.utils.change_directory import change_directory


def compile_source_code(
    forge_root_path: Path, contract_proposal_path: Path
) -> list[str]:
    """
    Compile the Solidity source code using Forge.

    Args:
        forge_root_path (Path): Path to the forge root directory.
        contract_proposal_path (Path): Path to the contract proposal file.

    Returns:
        list[str]: A list of source file paths.

    """
    with change_directory(forge_root_path):
        try:
            subprocess.run(
                ["forge", "build", "--contracts", str(contract_proposal_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            pp.pprint(
                f"Error compiling source code: {e.stderr}",
                status=pp.Colors.FAILURE,
                heading="Compilation Error",
            )
            raise
        except FileNotFoundError:
            pp.pprint(
                "Forge command not found. Please make sure Foundry is installed.",
                status=pp.Colors.FAILURE,
                heading="Command Not Found",
            )
            raise
        except OSError as e:
            pp.pprint(
                f"System error while executing forge: {e}",
                status=pp.Colors.FAILURE,
                heading="System Error",
            )
            raise

        # locate the json file in out/build-info (Only one file is expected)
        json_file_path = next(Path("out/build-info").glob("*.json"), None)
        if json_file_path is None:
            pp.pprint(
                "No JSON file found in out/build-info.",
                status=pp.Colors.FAILURE,
                heading="File Not Found",
            )
            raise FileNotFoundError("No JSON file found in out/build-info.")
        with open(json_file_path) as json_file:
            json_data: dict = json.load(json_file)

        return list(json_data.get("source_id_to_path", {}).values())


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
    source_file_paths = compile_source_code(forge_root_path, contract_proposal_path)
    source_codes = get_source_codes(forge_root_path, source_file_paths)
    run_customer_local_validation(
        customer=protocol_name,
        chain=chain,
        source_codes=source_codes,
        payload_contract=str(contract_proposal_path),
    )
