import json
from pathlib import Path
from git import Repo

import ProposalTools.config as config
import ProposalTools.Utils.PrettyPrinter as pp


class GitManager:
    """
    A class to manage Git repositories for a specific customer.

    Attributes:
        customer (str): The name or identifier of the customer.
        repos (dict): A dictionary mapping repository names to their URLs.
    """

    def __init__(self, customer: str) -> None:
        """
        Initialize the GitManager with the given customer name and load the repository URLs.

        Args:
            customer (str): The name or identifier of the customer.
        """
        self.customer = customer
        
        self.customer_path = config.MAIN_PATH / self.customer / "modules"
        self.customer_path.mkdir(parents=True, exist_ok=True)
        
        self.repos = self._load_repos()

    def _load_repos(self) -> dict:
        """
        Load repository URLs from the JSON file for the given customer.

        Returns:
            dict: A dictionary mapping repository names to their URLs.
        """
        with open(config.REPOS_PATH) as f:
            repos = json.load(f).get(self.customer, [])
        return {Path(r).stem: r for r in repos}

    def clone_or_update(self) -> None:
        """
        Clone the repositories for the customer.

        If the repository already exists locally, it will update the repository and its submodules.
        Otherwise, it will clone the repository and initialize submodules.
        """
        for repo_name, repo_url in self.repos.items():
            repo_path: Path = self.customer_path / repo_name
            if repo_path.exists():
                pp.pretty_print(f"Repository {repo_name} already exists at {repo_path}. Updating repo and submodules.", pp.Colors.INFO)
                repo = Repo(repo_path)
                repo.git.pull()
                repo.git.submodule('update', '--init', '--recursive')
            else:
                pp.pretty_print(f"Cloning {repo_name} from URL: {repo_url} to {repo_path}...", pp.Colors.INFO)
                Repo.clone_from(repo_url, repo_path, multi_options=["--recurse-submodules"])

