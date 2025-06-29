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


def get_contract_bytecode(
    forge_root_path: Path,
    contract_name: str,
    bytecode_type: BytecodeType = BytecodeType.RUNTIME,
) -> str:
    """
    Extract contract bytecode using forge inspect.

    Args:
        forge_root_path (Path): Path to the forge root directory.
        contract_name (str): Name of the contract to inspect.
        bytecode_type (BytecodeType): Type of bytecode to extract, either 'CREATION' or 'RUNTIME'.

    Returns:
        str: The contract bytecode as a hex string.

    Raises:
        ValueError: If bytecode_type is not supported.
        subprocess.CalledProcessError: If forge inspect command fails.
        FileNotFoundError: If forge command is not found.
    """
    with change_directory(forge_root_path):
        try:
            result = subprocess.run(
                [
                    "forge",
                    "inspect",
                    contract_name,
                    bytecode_type,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            pp.pprint(
                f"Error extracting {bytecode_type}: {e.stderr}",
                status=pp.Colors.FAILURE,
                heading="Bytecode Extraction Error",
            )
            raise
        except FileNotFoundError:
            pp.pprint(
                "Forge command not found. Please make sure Foundry is installed.",
                status=pp.Colors.FAILURE,
                heading="Command Not Found",
            )
            raise


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
    with change_directory(forge_root_path):
        if use_default:
            os.environ["FOUNDRY_PROFILE"] = "default"

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
        build_info_dir = out_dir / "build-info"
        json_file_path = next(build_info_dir.glob("*.json"), None)
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
