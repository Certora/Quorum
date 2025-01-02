import requests
from dataclasses import dataclass

BASE_BGD_CACHE_REPO = 'https://raw.githubusercontent.com/bgd-labs/v3-governance-cache/refs/heads/main/cache'
PROPOSALS_URL = f'{BASE_BGD_CACHE_REPO}/1/0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7/proposals'
BASE_SEATBELT_REPO = 'https://github.com/bgd-labs/seatbelt-gov-v3/blob/main/reports'
SEATBELT_PAYLOADS_URL = f'{BASE_SEATBELT_REPO}/payloads'

@dataclass
class ChainInfo:
    name: str
    block_explorer_link: str


AAVE_CHAIN_MAPPING = {
    '1': ChainInfo('Ethereum', 'https://etherscan.io/address'),
    '137': ChainInfo('Polygon', 'https://polygonscan.com/address'),
    '43114': ChainInfo('Avalanche', 'https://snowtrace.io/address'),
    '8453': ChainInfo('Base', 'https://basescan.org/address'),
    '42161': ChainInfo('Arbitrum One', 'https://arbiscan.io/address'),
    '1088': ChainInfo('Metis', 'https://explorer.metis.io/address'),
    '10': ChainInfo('OP Mainnet', 'https://optimistic.etherscan.io/address'),
    '56': ChainInfo('BNB Smart Chain', 'https://bscscan.com/address'),
    '100': ChainInfo('Gnosis', 'https://gnosisscan.io/address'),
    '534352': ChainInfo('Scroll', 'https://scrollscan.com/address'),
    '324': ChainInfo('zkSync Era', 'https://era.zksync.network/address'),
    '59144': ChainInfo('Linea', 'https://lineascan.build/'),
}


class AaveGovernanceAPI:
    """
    A utility class to interact with the BGD governance cache and retrieve 
    relevant information about Aave proposals and payload addresses.
    """

    def __init__(self) -> None:
        self.session = requests.Session()

    def get_proposal_data(self, proposal_id: int) -> dict:
        """
        Fetches the proposal data from the BGD governance cache.
        """
        proposal_data_link = f'{PROPOSALS_URL}/{proposal_id}.json'
        resp = self.session.get(proposal_data_link)
        resp.raise_for_status()
        return resp.json()

    def get_payload_addresses(self, chain_id: str, controller: str, payload_id: int) -> list[str]:
        """
        Fetches and returns the addresses from a given chain/payload.
        """
        url = f'{BASE_BGD_CACHE_REPO}/{chain_id}/{controller}/payloads/{payload_id}.json'
        resp = self.session.get(url)
        resp.raise_for_status()
        
        payload_data = resp.json()
        return [a['target'] for a in payload_data['payload']['actions']]
