import os
from pathlib import Path


main_path = os.getenv("ProposalsToolArtifactsPath")
if not main_path:
    raise ValueError("ProposalsToolArtifactsPath environment variable not set")

MAIN_PATH = Path(os.getenv("ProposalsToolArtifactsPath")).absolute()
REPOS_PATH = Path(__file__).parent / "GIT" / "repos.json"