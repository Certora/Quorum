from pathlib import Path

from git import Repo

import quorum.utils.pretty_printer as pp
from quorum.utils.quorum_configuration import QuorumConfiguration


class GitManager:
    """
    A class to manage Git repositories for a specific customer.

    Attributes:
        customer (str): The name or identifier of the customer.
        repos (dict): A dictionary mapping repository names to their URLs.
    """

    def __init__(self, customer: str, gt_config: dict[str, any]) -> None:
        """
        Initialize the GitManager with the given customer name and load the repository URLs.

        Args:
            customer (str): The name or identifier of the customer.
            gt_config (dict[str, any]): The ground truth configuration data.
        """
        self.customer = customer
        self.config = QuorumConfiguration()

        self.modules_path = self.config.main_path / self.customer / "modules"
        self.modules_path.mkdir(parents=True, exist_ok=True)

        self.review_module_path = (
            self.config.main_path / self.customer / "review_module"
        )
        self.review_module_path.mkdir(parents=True, exist_ok=True)

        self.repos, self.review_repo = self._load_repos_from_file(gt_config)

    def _load_repos_from_file(
        self, gt_config: dict[str, any]
    ) -> tuple[dict[str, str], dict[str, str]]:
        """
        Load repository URLs from the JSON file for the given customer.

        Args:
            gt_config (dict[str, any]): The ground truth configuration data for the customer.

        Returns:
            tuple[dict[str, str], dict[str, str]]: 2 dictionaries mapping repository names to their URLs.
                The first dictionary contains the repos to diff against. The second dictionary is the verification repo.
        """
        repos = {Path(r).stem: r for r in gt_config["dev_repos"]}

        verify_repo = (
            {Path(gt_config["review_repo"]).stem: gt_config["review_repo"]}
            if "review_repo" in gt_config
            else {}
        )
        return repos, verify_repo

    @staticmethod
    def __clone_or_update_for_repo(repo_name: str, repo_url: str, to_path: Path):
        repo_path = to_path / repo_name
        branch = None
        if "@" in repo_url:
            repo_url, branch = repo_url.split("@")
        if repo_path.exists():
            pp.pprint(
                f"Repository {repo_name} already exists at {repo_path}. Updating repo.",
                pp.Colors.INFO,
            )
            repo = Repo(repo_path)
            if branch:
                repo.git.checkout(branch)
            repo.git.pull()
        else:
            pp.pprint(
                f"Cloning {repo_name} from URL: {repo_url} to {repo_path}...",
                pp.Colors.INFO,
            )
            if branch:
                Repo.clone_from(repo_url, repo_path, branch=branch)
            else:
                Repo.clone_from(repo_url, repo_path)

    def clone_or_update(self) -> None:
        """
        Clone the repositories for the customer.

        If the repository already exists locally, it will update the repository and its submodules.
        Otherwise, it will clone the repository and initialize submodules.
        """
        pp.pprint(
            "Cloning and updating preliminaries", pp.Colors.INFO, pp.Heading.HEADING_2
        )
        for repo_name, repo_url in self.repos.items():
            GitManager.__clone_or_update_for_repo(
                repo_name, repo_url, self.modules_path
            )

        if self.review_repo:
            repo_name, repo_url = next(iter(self.review_repo.items()))
            GitManager.__clone_or_update_for_repo(
                repo_name, repo_url, self.review_module_path
            )
