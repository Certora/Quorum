import os
import shutil
from pathlib import Path


main_path = os.getenv("PRP_TOOL_PATH")
if not main_path:
    raise ValueError("PRP_TOOL_PATH environment variable not set")

MAIN_PATH = Path(main_path).absolute()

if not MAIN_PATH.exists():
    MAIN_PATH.mkdir(parents=True)

REPOS_PATH = MAIN_PATH / "repos.json"
DEFAULT_REPOS = Path(__file__).parent / "repos.json"

if not REPOS_PATH.exists():
    shutil.copy(DEFAULT_REPOS, REPOS_PATH)