from abc import ABC
from datetime import datetime
import json5 as json
from pathlib import Path

from Quorum.utils.quorum_configuration import QuorumConfiguration
from Quorum.apis.block_explorers.source_code import SourceCode
from Quorum.utils.chain_enum import Chain


class Check(ABC):
    def __init__(self, customer: str, chain: Chain, proposal_address: str, source_codes: list[SourceCode]):
        self.customer = customer
        self.chain = chain
        self.proposal_address = proposal_address
        self.source_codes = source_codes
        self.customer_folder = QuorumConfiguration().main_path / customer
        self.check_folder = self.customer_folder / "checks" / chain / proposal_address / f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.check_folder.mkdir(parents=True, exist_ok=True)

    
    def _write_to_file(self, path: str | Path, data: dict | str | list) -> None:
        """
        Writes data to a specified file, creating the file and its parent directories if they do not exist.

        Args:
            path (str | Path): The relative path to the file where the data will be written.
            data (Any): The data to be written to the file. This can be a dictionary for JSON files or a string for text files.
        """
        full_file_path = self.check_folder / path

        # Ensure the directory exists; if not, create it
        if not full_file_path.exists():
            full_file_path.parent.mkdir(parents=True, exist_ok=True)
            full_file_path.touch()

        with open(full_file_path, "a") as f:
             json.dump(data, f, indent=4) if isinstance(data, dict) or isinstance(data, list) else f.write(data)
             f.write("\n")