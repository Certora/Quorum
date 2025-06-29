import argparse
import tempfile

import quorum.utils.pretty_printer as pp
from quorum.apis.block_explorers.chains_api import ChainAPI
from quorum.utils.compile import (
    BytecodeType,
    compile_source_code,
    get_contract_bytecode_from_artifacts,
)


def _calculate_bytecode_diff(expected: str, actual: str) -> tuple[list[int], float]:
    """
    Calculate differences between two bytecode strings efficiently.

    Args:
        expected (str): Expected bytecode
        actual (str): Actual bytecode

    Returns:
        Tuple[List[int], float]: List of differing positions and difference percentage
    """
    if len(expected) != len(actual):
        return [], 100.0

    if not expected:  # Handle empty bytecode
        return [], 0.0

    diff_positions = [
        i for i, (e, a) in enumerate(zip(expected, actual, strict=False)) if e != a
    ]
    diff_percentage = (len(diff_positions) / len(expected)) * 100

    return diff_positions, diff_percentage


def _validate_bytecode(
    expected: str,
    actual: str,
    bytecode_type: BytecodeType,
    payload_address: str,
    chain: str,
) -> bool:
    """
    Validate a single bytecode type and report errors if found.

    Args:
        expected (str): Expected bytecode from analysis
        actual (str): Actual bytecode from compilation
        bytecode_type (BytecodeType): Type of bytecode (Runtime or Creation)
        payload_address (str): Contract address
        chain (str): Blockchain network

    Returns:
        bool: True if validation passed, False otherwise
    """
    if expected != actual:
        diff_positions, diff_percentage = _calculate_bytecode_diff(expected, actual)

        pp.pprint(
            (
                f"{bytecode_type.name} bytecode mismatch for address {payload_address} on chain {chain}.\n"
                f"Expected length: {len(expected)}, Got length: {len(actual)}\n"
                f"Difference at positions: {diff_positions}\n"
                f"Diff percentage: {diff_percentage:.2f}%"
            ),
            status=pp.Colors.FAILURE,
            heading=f"Bytecode {bytecode_type.name} Validation Error",
        )
        return False

    pp.pprint(
        f"{bytecode_type.name} bytecode validation successful for address {payload_address} on chain {chain}.",
        status=pp.Colors.SUCCESS,
    )
    return True


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
    chain, payload_address, forge_root_path, contract_proposal_path = (
        args.chain,
        args.payload_address,
        args.forge_root_path,
        args.contract_proposal_path,
    )

    # Get the bytecode analysis for the given address
    api = ChainAPI(chain)
    analysis = api.get_bytecodes_analysis(payload_address)
    if analysis is None:
        raise ValueError(
            f"Failed to retrieve bytecode analysis for address {payload_address} on chain {chain}."
        )

    with tempfile.TemporaryDirectory(dir=forge_root_path) as tmp:
        _, out_dir = compile_source_code(forge_root_path, contract_proposal_path, tmp)
        # Get the bytecode from the compiled contract artifacts
        runtime_bytecode = get_contract_bytecode_from_artifacts(
            out_dir,
            contract_proposal_path.stem,
            bytecode_type=BytecodeType.RUNTIME,
        )
        creation_bytecode = get_contract_bytecode_from_artifacts(
            out_dir,
            contract_proposal_path.stem,
            bytecode_type=BytecodeType.CREATION,
        )

    validation_results = []

    # Validate the runtime bytecode against the analysis
    if analysis.has_runtime_bytecode():
        result = _validate_bytecode(
            analysis.runtime_bytecode,
            runtime_bytecode,
            BytecodeType.RUNTIME,
            payload_address,
            chain,
        )
        validation_results.append(result)

    # Validate the creation bytecode against the analysis
    if analysis.has_creation_bytecode():
        result = _validate_bytecode(
            analysis.creation_bytecode,
            creation_bytecode,
            BytecodeType.CREATION,
            payload_address,
            chain,
        )
        validation_results.append(result)

    # Report overall success if all validations passed
    if validation_results and all(validation_results):
        pp.pprint(
            f"Bytecode validation successful for address {payload_address} on chain {chain}.",
            status=pp.Colors.SUCCESS,
            heading="Bytecode Validation Complete",
        )
