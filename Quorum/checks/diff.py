import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import Quorum.utils.pretty_printer as pp
from Quorum.apis.block_explorers.source_code import SourceCode
from Quorum.checks.check import Check
from Quorum.utils.chain_enum import Chain


@dataclass
class Compared:
    """
    A dataclass representing the result of comparing a local file with a proposal file.

    Attributes:
        local_file (str): The path to the local file.
        proposal_file (str): The name of the file from the proposal.
        diff (str): The path to the file containing the diff result.
    """

    local_file: str
    proposal_file: str
    diff: str


class DiffCheck(Check):
    """
    A class that performs a diff check between local and remote (proposal) source codes.

    This class compares source files from a local repository with those from a remote proposal,
    identifying differences and generating patch files.
    """

    def __init__(
        self,
        customer: str,
        chain: Chain,
        proposal_address: str,
        source_codes: list[SourceCode],
    ):
        super().__init__(customer, chain, proposal_address, source_codes)
        self.target_repo = self.customer_folder / "modules"

    def __find_most_common_path(self, source_path: Path, repo: Path) -> Optional[Path]:
        """
        Find the most common file path between a source path and a repository.

        This method attempts to locate the corresponding local file for a given source path from the proposal.

        Args:
            source_path (Path): The source file path from the remote repository.
            repo (Path): The local repository path.

        Returns:
            Optional[Path]: The most common file path if found, otherwise None.
        """
        for i in range(len(source_path.parts)):
            # Create a path suffix starting from the i-th part
            current_source_path = Path(*source_path.parts[i:])

            # Search for matching files in the repository
            local_files = list(repo.rglob(str(current_source_path)))

            if local_files:
                # Compute similarity ratios between source_path and each local_file
                similarities = []
                source_str = current_source_path.as_posix()
                for local_file in local_files:
                    local_str = local_file.as_posix()
                    ratio = difflib.SequenceMatcher(None, source_str, local_str).ratio()
                    similarities.append((local_file, ratio))

                # Find the local_file with the highest similarity ratio
                most_similar_file, _ = max(similarities, key=lambda x: x[1])

                return most_similar_file

        # Return None if no matching files are found
        return None

    def find_diffs(self) -> list[SourceCode]:
        """
        Find and save differences between local and remote source codes.

        This method compares the contents of local files with those from the proposal, generating patch files
        for any differences found.

        Returns:
            list[Compared]: list of missing files.
        """
        missing_files = []
        files_with_diffs = []

        for source_code in self.source_codes:
            local_file = self.__find_most_common_path(Path(source_code.file_name), self.target_repo)
            if not local_file:
                missing_files.append(source_code)
                continue

            local_content = local_file.read_text().splitlines()
            remote_content = source_code.file_content

            diff = difflib.unified_diff(
                local_content,
                remote_content,
                fromfile=str(local_file),
                tofile=source_code.file_name,
            )
            diff_text = "\n".join(diff)

            if diff_text:
                diff_file = f"{local_file.stem}.patch"
                files_with_diffs.append(
                    Compared(
                        str(local_file),
                        source_code.file_name,
                        str(self.check_folder / diff_file),
                    )
                )
                self._write_to_file(diff_file, diff_text)

        self.__print_diffs_results(missing_files, files_with_diffs)
        return missing_files

    def __print_diffs_results(self, missing_files: list[SourceCode], files_with_diffs: list[Compared]):
        """
        Print the results of the diff check.

        This method outputs a summary of the comparison, including the number of files compared,
        the number of missing files, and the number of files with differences.

        Args:
            missing_files (list[SourceCode]): A list of SourceCode objects representing missing files.
            files_with_diffs (list[Compared]): A list of Compared objects representing files with differences.
        """
        total_number_of_files = len(self.source_codes)
        number_of_missing_files = len(missing_files)
        number_of_files_with_diffs = len(files_with_diffs)

        msg = f"Compared {total_number_of_files - number_of_missing_files}/{total_number_of_files} files for proposal {self.proposal_address}"
        if number_of_missing_files == 0:
            pp.pretty_print(msg, pp.Colors.SUCCESS)
        else:
            pp.pretty_print(msg, pp.Colors.WARNING)
            for source_code in missing_files:
                pp.pretty_print(
                    f"Missing file: {source_code.file_name} in local repo",
                    pp.Colors.WARNING,
                )

        if number_of_files_with_diffs == 0:
            pp.pretty_print("No differences found.", pp.Colors.SUCCESS)
        else:
            pp.pretty_print(
                f"Found differences in {number_of_files_with_diffs} files",
                pp.Colors.FAILURE,
            )
            for compared_pair in files_with_diffs:
                pp.pretty_print(
                    f"Local: {compared_pair.local_file}\nProposal: {compared_pair.proposal_file}\nDiff: {compared_pair.diff}",
                    pp.Colors.FAILURE,
                )
