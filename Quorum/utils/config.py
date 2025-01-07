import os
from pathlib import Path

import Quorum.utils.pretty_printer as pp
from Quorum.utils.load_env import load_env_variables

load_env_variables()

main_path = os.getenv("QUORUM_PATH")
if not main_path:
    raise ValueError("QUORUM_PATH environment variable not set")

MAIN_PATH = Path(main_path).absolute()

if not MAIN_PATH.exists():
    MAIN_PATH.mkdir(parents=True)

GROUND_TRUTH_PATH = MAIN_PATH / "ground_truth.json"

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    pp.pprint(
        "Warning: ANTHROPIC_API_KEY environment variable is not set. All dependent checks will be skipped.",
        pp.Colors.WARNING
    )

ANTHROPIC_MODEL = os.getenv('ANTROPIC_MDOEL', 'claude-3-5-sonnet-20241022')
