import argparse
import tempfile

from quorum.utils.compile import compile_source_code


def run_bytecode_validation(args: argparse.Namespace) -> None:
    """
    Run a bytecode validation check.

    Args:
        args (argparse.Namespace): Command line arguments containing:
            - chain (str): The blockchain network identifier
            - payload_address (str): The address of the payload contract to validate
            - forge_root_path (str): Path to the forge root directory
            - contract_proposal_path (str): Path to the contract proposal file
    """
    _, _, forge_root_path, contract_proposal_path = (
        args.chain,
        args.payload_address,
        args.forge_root_path,
        args.contract_proposal_path,
    )

    with tempfile.TemporaryDirectory(prefix="quorum-forge-") as tmp:
        compile_source_code(forge_root_path, contract_proposal_path, tmp)
