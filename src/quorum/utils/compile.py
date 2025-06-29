import json
import os
import subprocess
from enum import StrEnum
from pathlib import Path

import quorum.utils.pretty_printer as pp
from quorum.utils.change_directory import change_directory


class BytecodeType(StrEnum):
    CREATION = "bytecode"
    RUNTIME = "deployedBytecode"


def get_bytecode_from_artifact(artifact_path: Path, bytecode_type: BytecodeType) -> str:
    """
    Extract contract bytecode from a forge artifact JSON file.

    Args:
        artifact_path (Path): Path to the contract artifact JSON file.
        bytecode_type (BytecodeType): Type of bytecode to extract, either 'CREATION' or 'RUNTIME'.

    Returns:
        str: The contract bytecode as a hex string.

    Raises:
        FileNotFoundError: If the artifact file is not found.
        json.JSONDecodeError: If the JSON file is malformed.
        KeyError: If the expected bytecode field is not found in the artifact.
    """
    if not artifact_path.exists():
        pp.pprint(
            f"Artifact file not found: {artifact_path}",
            status=pp.Colors.FAILURE,
            heading="Artifact File Not Found",
        )
        raise FileNotFoundError(f"Artifact file not found: {artifact_path}")

    try:
        with artifact_path.open() as f:
            artifact = json.load(f)
    except json.JSONDecodeError as e:
        pp.pprint(
            f"Error parsing JSON artifact {artifact_path}: {e}",
            status=pp.Colors.FAILURE,
            heading="JSON Parse Error",
        )
        raise

    # Note: 'bytecode' in JSON is creation, 'deployedBytecode' is runtime
    bytecode_obj = artifact.get(bytecode_type.value, {})
    if not bytecode_obj:
        pp.pprint(
            f"No {bytecode_type.value} found in artifact {artifact_path}",
            status=pp.Colors.WARNING,
            heading="Bytecode Not Found",
        )
        return ""

    return bytecode_obj.get("object", "")


def find_contract_artifact(out_dir: Path, contract_name: str) -> Path:
    """
    Find the artifact JSON file for a specific contract.

    Args:
        out_dir (Path): The forge output directory containing artifacts.
        contract_name (str): Name of the contract to find.

    Returns:
        Path: Path to the contract artifact JSON file.

    Raises:
        FileNotFoundError: If the contract artifact is not found.
    """
    # Check standard paths first (more efficient)
    standard_paths = [
        out_dir / f"{contract_name}.sol" / f"{contract_name}.json",
        out_dir / contract_name / f"{contract_name}.json",
    ]

    for path in standard_paths:
        if path.exists():
            return path

    # Fallback: search recursively for any JSON file with the contract name
    try:
        return next(out_dir.rglob(f"{contract_name}.json"))
    except StopIteration:
        raise FileNotFoundError(
            f"Contract artifact not found for {contract_name} in {out_dir}"
        ) from None


def get_contract_bytecode_from_artifacts(
    out_dir: Path,
    contract_name: str,
    bytecode_type: BytecodeType = BytecodeType.RUNTIME,
) -> str:
    """
    Extract contract bytecode from forge artifacts instead of using forge inspect.

    Args:
        out_dir (Path): The forge output directory containing artifacts.
        contract_name (str): Name of the contract to inspect.
        bytecode_type (BytecodeType): Type of bytecode to extract, either 'CREATION' or 'RUNTIME'.

    Returns:
        str: The contract bytecode as a hex string.

    Raises:
        FileNotFoundError: If the contract artifact is not found.
        json.JSONDecodeError: If the JSON file is malformed.
    """
    artifact_path = find_contract_artifact(out_dir, contract_name)
    return get_bytecode_from_artifact(artifact_path, bytecode_type)


def _execute_forge_build(
    forge_root_path: Path,
    contract_proposal_path: Path,
    out_dir: Path,
    use_default: bool = False,
) -> None:
    """
    Execute forge build command with common error handling.

    Args:
        forge_root_path (Path): Path to the forge root directory.
        contract_proposal_path (Path): Path to the contract proposal file.
        out_dir (Path): Output directory for compilation artifacts.
        use_default (bool): If True, use the default forge build command.

    Raises:
        subprocess.CalledProcessError: If forge build command fails.
        FileNotFoundError: If forge command is not found.
        OSError: If system error occurs while executing forge.
    """
    with change_directory(forge_root_path):
        env = os.environ.copy()
        if use_default:
            env["FOUNDRY_PROFILE"] = "default"

        try:
            subprocess.run(
                [
                    "forge",
                    "build",
                    "--contracts",
                    str(contract_proposal_path),
                    "--out",
                    str(out_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
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


def _extract_source_files(out_dir: Path) -> list[str]:
    """
    Extract source file paths from forge build info.

    Args:
        out_dir (Path): Output directory containing build artifacts.

    Returns:
        list[str]: List of source file paths.

    Raises:
        FileNotFoundError: If no JSON file found in build-info directory.
    """
    build_info_dir = out_dir / "build-info"

    # Get all JSON files in build-info directory
    json_files = list(build_info_dir.glob("*.json"))

    if not json_files:
        pp.pprint(
            "No JSON file found in out/build-info.",
            status=pp.Colors.FAILURE,
            heading="File Not Found",
        )
        raise FileNotFoundError("No JSON file found in out/build-info.")

    # Use the first JSON file (expecting only one)
    json_file_path = json_files[0]

    with json_file_path.open() as json_file:
        json_data: dict = json.load(json_file)

    return list(json_data.get("source_id_to_path", {}).values())


def compile_source_code(
    forge_root_path: Path,
    contract_proposal_path: Path,
    target_dir: str,
    use_default: bool = False,
) -> list[str]:
    """
    Compile the Solidity source code using Forge.

    Args:
        forge_root_path (Path): Path to the forge root directory.
        contract_proposal_path (Path): Path to the contract proposal file.
        target_dir (str): Target directory for the compiled output.
        use_default (bool): If True, use the default forge build command. Defaults to False.

    Returns:
        list[str]: A list of source file paths.

    """
    out_dir = Path(target_dir) / "out"
    _execute_forge_build(forge_root_path, contract_proposal_path, out_dir, use_default)
    return _extract_source_files(out_dir)


def compile_source_code_with_artifacts(
    forge_root_path: Path,
    contract_proposal_path: Path,
    target_dir: str,
    use_default: bool = False,
) -> Path:
    """
    Compile the Solidity source code using Forge and return both source files and output directory.

    This function is optimized for bytecode extraction workflows where access to the output
    directory is needed to read compiled artifacts.

    Args:
        forge_root_path (Path): Path to the forge root directory.
        contract_proposal_path (Path): Path to the contract proposal file.
        target_dir (str): Target directory for the compiled output.
        use_default (bool): If True, use the default forge build command. Defaults to False.

    Returns:
        Path: The output directory path.

    """
    out_dir = Path(target_dir) / "out"
    _execute_forge_build(forge_root_path, contract_proposal_path, out_dir, use_default)
    return out_dir
