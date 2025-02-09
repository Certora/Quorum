import requests
from pydantic import BaseModel

from quorum.utils.singleton import singleton


class MultisigData(BaseModel):
    """
    MultisigData is a Pydantic model for Safe Multisig data.
    """

    address: str
    owners: list[str]
    threshold: int


@singleton
class SafeAPI:
    """
    SafeAPI is a class designed to interact with the Safe Multisig API.
    It fetches and stores data for various Safe Multisig contracts.
    """

    SAFE_API_URL = "https://safe-transaction-mainnet.safe.global/api/v1/safes"

    def __init__(self):
        self.session = requests.Session()

    def get_multisig_info(self, address: str) -> MultisigData | None:
        """
        Get Safe Multisig data for a given address.

        Args:
            address (str): The contract address of the Safe Multisig.

        Returns:
            MultisigData: The Safe Multisig data for the specified address, or None if not found.
        """
        response = self.session.get(f"{self.SAFE_API_URL}/{address}")
        if not response.ok:
            return None
        data = response.json()
        return MultisigData(**data)
