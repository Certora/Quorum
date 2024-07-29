import json
from pathlib import Path
from git import Repo

import ProposalTools.config as config


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
        self.customer_path = config.MAIN_PATH / self.customer
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

        If the repository already exists locally, it will be skipped.
        """
        for repo_name, repo_url in self.repos.items():
            repo_path = self.customer_path / repo_name
            if repo_path.exists():
                print(f"Repository {repo_name} already exists at {repo_path}. Update repo instead of cloning.")
                repo = Repo(repo_path)
                repo.git.pull()
            else:
                print(f"Cloning {repo_name} from URL: {repo_url} to {repo_path}...")
                Repo.clone_from(repo_url, repo_path, multi_options=["--recurse-submodule"])