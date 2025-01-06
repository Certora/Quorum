import requests

from Quorum.utils.chain_enum import Chain
from Quorum.apis.governance.data_models import BGDProposalData, PayloadAddresses

BASE_BGD_CACHE_REPO = 'https://raw.githubusercontent.com/bgd-labs/v3-governance-cache/refs/heads/main/cache'
PROPOSALS_URL = f'{BASE_BGD_CACHE_REPO}/1/0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7/proposals'

CHAIN_ID_TO_CHAIN = {
    '1': Chain.ETH,
    '42161': Chain.ARB,
    '43114': Chain.AVAX,
    '8453': Chain.BASE,
    '56': Chain.BSC,
    '100': Chain.GNO,
    '10': Chain.OPT,
    '137': Chain.POLY,
    '534352': Chain.SCROLL,
    '324': Chain.ZK,
    '59144': Chain.LINEA,
}

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
        proposal_data_link = f'{PROPOSALS_URL}/{proposal_id}.json'
        resp = self.session.get(proposal_data_link)
        resp.raise_for_status()

        raw_json = resp.json()
        # Parse into our data model
        return BGDProposalData(**raw_json)

    def get_payload_addresses(self, chain_id: str, controller: str, payload_id: int) -> list[str]:
        """
        Retrieves a list of payload addresses for a given payload ID, chain, and controller.

        Args:
            chain_id: The chain ID for the proposal.
            controller: The controller for the proposal.
            payload_id: The ID of the payload to fetch.

        Returns:
            A list of addresses that are part of the payload.
        """
        url = f'{BASE_BGD_CACHE_REPO}/{chain_id}/{controller}/payloads/{payload_id}.json'
        resp = self.session.get(url)
        resp.raise_for_status()
        
        payload_data = resp.json()
        # We only need the 'target' field from each action
        return [a['target'] for a in payload_data['payload']['actions']]

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
            addresses = self.get_payload_addresses(p.chain, p.payloads_controller, p.payload_id)
            results.append(PayloadAddresses(chain=CHAIN_ID_TO_CHAIN[p.chain], addresses=addresses))
        return results
