from abc import ABC, abstractmethod
from datetime import datetime
import ProposalTools.config as config


class Check(ABC):
    def __init__(self, customer: str, proposal_address: str):
        self.customer = customer
        self.proposal_address = proposal_address
        self.customer_folder = config.MAIN_PATH / customer
        self.check_folder = self.customer_folder / "checks" / proposal_address / f"{self.get_check_name()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.check_folder.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def execute_check(self):
        """
        Abstract method to execute the specific check.
        Must be overridden by subclasses.
        """
        pass
    
    @abstractmethod
    def get_check_name(self) -> str:
        """
        Returns the name of the check to be used in folder creation.
        Should be overridden by subclasses to provide specific check name.
        """
        pass
