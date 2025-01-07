import re
from pathlib import Path
from argparse import ArgumentTypeError
from json import JSONDecodeError
import json5 as json
from typing import Any

import Quorum.utils.pretty_printer as pp


def validate_address(address: str) -> str:
    pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')
    if not bool(pattern.match(address)):
        raise ArgumentTypeError(f'{address} is not a valid address.')
    return address


def validate_path(path: Path) -> Path:
    if not path.exists():
        raise ArgumentTypeError(f'Could not find path at {path}.')
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
        with open(config_path, 'r') as file:
            config_data = json.load(file)
        return config_data
    except (FileNotFoundError, JSONDecodeError) as e:
        pp.pprint(f"Failed to parse given config file {config_path}:\n{e}", pp.Colors.FAILURE)
