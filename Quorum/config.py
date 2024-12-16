import os
import shutil
from pathlib import Path


main_path = os.getenv("QUORUM_PATH")
if not main_path:
    raise ValueError("QUORUM_PATH environment variable not set")

MAIN_PATH = Path(main_path).absolute()

if not MAIN_PATH.exists():
    MAIN_PATH.mkdir(parents=True)

GROUND_TRUTH_PATH = MAIN_PATH / "ground_truth.json"
DEFAULT_REPOS = Path(__file__).parent / "ground_truth.json"

if not GROUND_TRUTH_PATH.exists():
    shutil.copy(DEFAULT_REPOS, GROUND_TRUTH_PATH)

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.getenv('ANTROPIC_MDOEL', 'claude-3-5-sonnet-20241022')
