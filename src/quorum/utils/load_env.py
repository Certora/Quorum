import os
from pathlib import Path

from dotenv import load_dotenv

import quorum.utils.pretty_printer as pp


def load_env_variables(dotenv_path: Path | None = None) -> None:
    """
    Load environment variables from a .env file and print any overridden variables.
    If no path is provided, it defaults to the current working directory.
    Args:
        dotenv_path (Path | None): The path to the directory containing the .env file.
            If None, defaults to the current working directory.
    """
    if dotenv_path is None:
        # Load the .env file from the current working directory
        dotenv_path = Path.cwd()

    # Capture the environment variables before loading .env
    env_before = dict(os.environ)

    # Load .env with override=True
    load_dotenv(dotenv_path=dotenv_path / ".env", override=True)

    # Capture the environment variables after loading .env
    env_after = dict(os.environ)

    # Identify overridden variables
    overridden_vars = {
        key: {"before": env_before[key], "after": env_after[key]}
        for key in env_before
        if key in env_after and env_before[key] != env_after[key]
    }

    # Print the user if any environment variables were overridden
    if overridden_vars:
        pp.pprint(
            "The following environment variables were overridden:", pp.Colors.WARNING
        )
        for key, values in overridden_vars.items():
            pp.pprint(
                f"{key}: {values['before']} -> {values['after']}", pp.Colors.WARNING
            )
