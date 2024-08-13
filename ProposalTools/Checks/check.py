from abc import ABC
from datetime import datetime

import ProposalTools.config as config
from ProposalTools.Utils.source_code import SourceCode
from ProposalTools.Utils.chain_enum import Chain


class Check(ABC):
    def __init__(self, customer: str, chain: Chain, proposal_address: str, source_codes: list[SourceCode]):
        self.customer = customer
        self.chain = chain
        self.proposal_address = proposal_address
        self.source_codes = source_codes
        self.customer_folder = config.MAIN_PATH / customer
        self.check_folder = self.customer_folder / "checks" / chain / proposal_address / f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.check_folder.mkdir(parents=True, exist_ok=True)
