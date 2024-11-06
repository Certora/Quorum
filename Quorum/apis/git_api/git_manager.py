import json
from pathlib import Path
from git import Repo

import Quorum.config as config
import Quorum.utils.pretty_printer as pp


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
        
        self.customer_modules_path = config.MAIN_PATH / self.customer / "modules"
        self.customer_modules_path.mkdir(parents=True, exist_ok=True)
        
        self.customer_review_module_path = config.MAIN_PATH / self.customer / "review_module"
        self.customer_review_module_path.mkdir(parents=True, exist_ok=True)

        self.repos, self.review_repo = self._load_repos_from_file()

    def _load_repos_from_file(self) -> tuple[dict[str, str], dict[str, str]]:
        """
        Load repository URLs from the JSON file for the given customer.

        Returns:
            tuple[dict[str, str], dict[str, str]]: 2 dictionaries mapping repository names to their URLs.
                The first dictionary contains the repos to diff against. The second dictionary is the verification repo.
        """
        with open(config.REPOS_PATH) as f:
            repos_data = json.load(f)
        
        # Normalize the customer name to handle case differences
        normalized_customer = self.customer.lower()
        customer_repos = next((repos for key, repos in repos_data.items() if key.lower() == normalized_customer), None)
        if customer_repos is None:
            return {}, {}
        
        repos = {Path(r).stem: r for r in customer_repos["dev_repos"]}

        verify_repo = ({Path(customer_repos["review_repo"]).stem: customer_repos["review_repo"]}
                       if "review_repo" in customer_repos else {})
        return repos, verify_repo

    def clone_or_update(self) -> None:
        """
        Clone the repositories for the customer.

        If the repository already exists locally, it will update the repository and its submodules.
        Otherwise, it will clone the repository and initialize submodules.
        """
        def clone_or_update_for_repo(repo_name: str, repo_url: str, to_path: Path):
            repo_path = to_path / repo_name
            if repo_path.exists():
                pp.pretty_print(f"Repository {repo_name} already exists at {repo_path}. Updating repo and submodules.", pp.Colors.INFO)
                repo = Repo(repo_path)
                repo.git.pull()
                repo.git.submodule('update', '--init', '--recursive')
            else:
                pp.pretty_print(f"Cloning {repo_name} from URL: {repo_url} to {repo_path}...", pp.Colors.INFO)
                Repo.clone_from(repo_url, repo_path, multi_options=["--recurse-submodules"])

        for repo_name, repo_url in self.repos.items():
           clone_or_update_for_repo(repo_name, repo_url, self.customer_modules_path)
        
        if len(self.review_repo) > 0:
            clone_or_update_for_repo(*list(self.review_repo.items())[0], self.customer_review_module_path)

