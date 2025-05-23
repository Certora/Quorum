import requests

from quorum.apis.governance.data_models import BGDProposalData, PayloadAddresses
from quorum.utils.chain_enum import Chain

BASE_BGD_CACHE_REPO = "https://raw.githubusercontent.com/bgd-labs/v3-governance-cache/refs/heads/main/cache"
PROPOSALS_URL = (
    f"{BASE_BGD_CACHE_REPO}/1/0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7/proposals"
)

NOT_FOUND_STATUS_CODE = 404

CHAIN_ID_TO_CHAIN = {
    "1": Chain.ETH,
    "42161": Chain.ARB,
    "43114": Chain.AVAX,
    "8453": Chain.BASE,
    "56": Chain.BSC,
    "100": Chain.GNO,
    "10": Chain.OPT,
    "137": Chain.POLY,
    "534352": Chain.SCROLL,
    "324": Chain.ZK,
    "59144": Chain.LINEA,
    "42220": Chain.CELO,
    "146": Chain.SONIC,
    "1088": Chain.MET,
}


class ProposalNotFoundException(Exception):
    def __init__(
        self, proposal_id: int, project_name: str, response: requests.Response
    ):
        super().__init__()
        self.proposal_id = proposal_id
        self.project_name = project_name
        self.response = response

    def __str__(self):
        return (
            f"Proposal id {self.proposal_id} for {self.project_name} could not be found "
            f"at url {self.response.url} (error code {self.response.status_code}). "
            "Most likely Aave's cache repo is not updated."
        )


class ChainNotFoundException(Exception):
    def __init__(self, chain_id: int, project_name: str, response: requests.Response):
        super().__init__()
        self.chain_id = chain_id
        self.project_name = project_name
        self.response = response

    def __str__(self):
        return (
            f"Chain {CHAIN_ID_TO_CHAIN[str(self.chain_id)]} (id {self.chain_id}) info for {self.project_name} could not be found "
            f"at url {self.response.url} (error code {self.response.status_code}) "
            "Most likely Aave's cache repo is not updated."
        )


class AaveGovernanceAPI:
    """
    A utility class to interact with the BGD governance cache and retrieve
    relevant information about Aave proposals and payload addresses.
    """

    def __init__(self) -> None:
        self.session = requests.Session()

    def get_proposal_data(self, proposal_id: int) -> BGDProposalData:
        """
        Fetches and returns the data for a given proposal.

        Args:
            proposal_id: The ID of the proposal to fetch.

        Returns:
            A BGDProposalData object.
        """
        proposal_data_link = f"{PROPOSALS_URL}/{proposal_id}.json"
        resp = self.session.get(proposal_data_link)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            if resp.status_code == NOT_FOUND_STATUS_CODE:
                raise ProposalNotFoundException(proposal_id, "Aave", e.response) from e
            raise

        raw_json = resp.json()
        # Parse into our data model
        return BGDProposalData(**raw_json)

    def get_payload_addresses(
        self, chain_id: str, controller: str, payload_id: int
    ) -> list[str]:
        """
        Retrieves a list of payload addresses for a given payload ID, chain, and controller.

        Args:
            chain_id: The chain ID for the proposal.
            controller: The controller for the proposal.
            payload_id: The ID of the payload to fetch.

        Returns:
            A list of addresses that are part of the payload.
        """
        url = (
            f"{BASE_BGD_CACHE_REPO}/{chain_id}/{controller}/payloads/{payload_id}.json"
        )
        resp = self.session.get(url)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            if resp.status_code == NOT_FOUND_STATUS_CODE:
                raise ChainNotFoundException(chain_id, "Aave", e.response) from e
            raise

        payload_data = resp.json()
        # We only need the 'target' field from each action
        return [a["target"] for a in payload_data["payload"]["actions"]]

    def get_all_payloads_addresses(self, proposal_id: int) -> list[PayloadAddresses]:
        """
        Retrieves all payload addresses for a given proposal.

        Args:
            proposal_id: The ID of the proposal to fetch.

        Returns:
            A list of PayloadAddresses objects, each containing a chain ID and a list of addresses.
        """
        data = self.get_proposal_data(proposal_id)
        results = []
        for p in data.proposal.payloads:
            addresses = self.get_payload_addresses(
                p.chain, p.payloads_controller, p.payload_id
            )
            results.append(
                PayloadAddresses(chain=CHAIN_ID_TO_CHAIN[p.chain], addresses=addresses)
            )
        return results
