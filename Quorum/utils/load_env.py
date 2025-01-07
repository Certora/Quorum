import os
from pathlib import Path
from dotenv import load_dotenv

import Quorum.utils.pretty_printer as pp

def load_env_variables():
    # Capture the environment variables before loading .env
    env_before = dict(os.environ)

    # Load .env with override=True
    load_dotenv(dotenv_path = Path.cwd() / '.env', override=True)

    # Capture the environment variables after loading .env
    env_after = dict(os.environ)

    # Identify overridden variables
    overridden_vars = {
        key: {'before': env_before[key], 'after': env_after[key]}
        for key in env_before
        if key in env_after and env_before[key] != env_after[key]
    }

    # Print the user if any environment variables were overridden
    if overridden_vars:
        pp.pprint("The following environment variables were overridden:", pp.Colors.WARNING)
        for key, values in overridden_vars.items():
            pp.pprint(f"{key}: {values['before']} -> {values['after']}", pp.Colors.WARNING)
