import os
from pathlib import Path


main_path = os.getenv("PRP_TOOL_PATH")
if not main_path:
    raise ValueError("PRP_TOOL_PATH environment variable not set")

MAIN_PATH = Path(main_path).absolute()
REPOS_PATH = MAIN_PATH / "repos.json"