import os
import shutil
from pathlib import Path

import Quorum.utils.pretty_printer as pp

main_path = os.getenv("QUORUM_PATH")
if not main_path:
    raise ValueError("QUORUM_PATH environment variable not set")

MAIN_PATH = Path(main_path).absolute()

if not MAIN_PATH.exists():
    MAIN_PATH.mkdir(parents=True)

GROUND_TRUTH_PATH = MAIN_PATH / "ground_truth.json"
DEFAULT_REPOS = Path(__file__).parent / "ground_truth.json"

EXECUTION_PATH = MAIN_PATH / "execution.json"
DEFAULT_EXECUTION = Path(__file__).parent / "execution.json"

if not GROUND_TRUTH_PATH.exists():
    shutil.copy(DEFAULT_REPOS, GROUND_TRUTH_PATH)

if not EXECUTION_PATH.exists():
    shutil.copy(DEFAULT_EXECUTION, EXECUTION_PATH)


ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    pp.pretty_print(
        "Warning: ANTHROPIC_API_KEY environment variable is not set. All dependent checks will be skipped.",
        pp.Colors.WARNING
    )

ANTHROPIC_MODEL = os.getenv('ANTROPIC_MDOEL', 'claude-3-5-sonnet-20241022')
