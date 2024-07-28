import os
from pathlib import Path


main_path = os.getenv("ProposalToolsArtifactsPath")
if not main_path:
    raise ValueError("ProposalToolsArtifactsPath environment variable not set")

MAIN_PATH = Path(os.getenv("ProposalToolsArtifactsPath")).absolute()
REPOS_PATH = (Path(__file__).parent / "GIT" / "repos.json").absolute()