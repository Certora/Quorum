import re
from argparse import ArgumentTypeError
from json import JSONDecodeError
from pathlib import Path
from typing import Any

import json5 as json

import quorum.utils.pretty_printer as pp


def make_dict_lowercase(obj: Any) -> Any:
    """Convert all string elements to lowercase recursively in any nested structure."""
    if isinstance(obj, dict):
        return {
            k.lower() if isinstance(k, str) else k: make_dict_lowercase(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [make_dict_lowercase(item) for item in obj]
    elif isinstance(obj, str):
        return obj.lower()
    else:
        return obj


def validate_address(address: str) -> str:
    pattern = re.compile(r"^0x[a-fA-F0-9]{40}$")
    if not bool(pattern.match(address)):
        raise ArgumentTypeError(f"{address} is not a valid address.")
    return address


def validate_path(path: Path) -> Path:
    if not path.exists():
        raise ArgumentTypeError(f"Could not find path at {path}.")
    return path


def load_config(config_path: str) -> dict[str, Any] | None:
    """
    Load and parse the JSON configuration file.

    Args:
        config_path (str): Path to the JSON configuration file.

    Returns:
        dict[str, Any]: Parsed JSON data.
    """
    try:
        with open(config_path) as file:
            config_data = json.load(file)
            config_data = make_dict_lowercase(config_data)
        return config_data
    except (FileNotFoundError, JSONDecodeError) as e:
        pp.pprint(
            f"Failed to parse given config file {config_path}:\n{e}", pp.Colors.FAILURE
        )
        return None
