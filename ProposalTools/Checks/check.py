from abc import ABC, abstractmethod
from datetime import datetime

import ProposalTools.config as config
from ProposalTools.API.api_manager import SourceCode


class Check(ABC):
    def __init__(self, customer: str, proposal_address: str, source_codes: list[SourceCode]):
        self.customer = customer
        self.proposal_address = proposal_address
        self.source_codes = source_codes

        self.customer_folder = config.MAIN_PATH / customer
        self.check_folder = self.customer_folder / "checks" / proposal_address / f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.check_folder.mkdir(parents=True, exist_ok=True)
