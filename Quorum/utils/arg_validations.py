import re
from pathlib import Path
from argparse import ArgumentTypeError


def validate_address(address: str) -> str:
    pattern = re.compile(r"^0x[a-fA-F0-9]{40}$")
    if not bool(pattern.match(address)):
        raise ArgumentTypeError(f"{address} is not a valid address.")
    return address


def validate_path(path: Path) -> Path:
    if not path.exists():
        raise ArgumentTypeError(f"Could not find path at {path}.")
    return path
