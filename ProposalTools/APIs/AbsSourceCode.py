from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class SourceCode:
    file_name: str
    file_content: list[str]

class SourceCodeInterface(ABC):
    @abstractmethod
    def get_source_code(self, proposal_address: str) -> list[SourceCode]:
        pass