import requests
from typing import Optional, List
from pydantic import BaseModel, Field
import json5 as json

# ==============================
#  Constants / Endpoints
# ==============================
BASE_BGD_CACHE_REPO = 'https://raw.githubusercontent.com/bgd-labs/v3-governance-cache/refs/heads/main/cache'
PROPOSALS_URL = f'{BASE_BGD_CACHE_REPO}/1/0x9AEE0B04504CeF83A65AC3f0e838D0593BCb2BC7/proposals'
BASE_SEATBELT_REPO = 'https://github.com/bgd-labs/seatbelt-gov-v3/blob/main/reports'
SEATBELT_PAYLOADS_URL = f'{BASE_SEATBELT_REPO}/payloads'


# ==============================
#  Chain Info Model
# ==============================
class ChainInfo(BaseModel):
    name: str
    block_explorer_link: str


# ==============================
#  Data Models for BGD JSON
# ==============================
class IPFSData(BaseModel):
    title: Optional[str] = None
    discussions: Optional[str] = None


class PayloadData(BaseModel):
    chain: str
    payloads_controller: str = Field(alias='payloadsController')
    payload_id: int = Field(alias='payloadId')

    class Config:
        allow_population_by_alias = True


class ProposalData(BaseModel):
    payloads: list[PayloadData] = Field(default_factory=list)
    votingPortal: Optional[str] = None
    ipfsHash: Optional[str] = None


class EventArgs(BaseModel):
    creator: Optional[str] = None
    accessLevel: Optional[int] = None
    ipfsHash: Optional[str] = None


class EventData(BaseModel):
    transactionHash: Optional[str] = None
    args: EventArgs = Field(default_factory=EventArgs)


class BGDProposalData(BaseModel):
    """
    Represents the entire JSON structure returned by the BGD cache
    for a given proposal.
    """
    ipfs: Optional[IPFSData] = None
    proposal: Optional[ProposalData] = None
    events: List[EventData] = Field(default_factory=list)


# ==============================
#  Mapping for Chains
# ==============================
AAVE_CHAIN_MAPPING = {
    '1':     ChainInfo(name='Ethereum',       block_explorer_link='https://etherscan.io/address'),
    '137':   ChainInfo(name='Polygon',        block_explorer_link='https://polygonscan.com/address'),
    '43114': ChainInfo(name='Avalanche',      block_explorer_link='https://snowtrace.io/address'),
    '8453':  ChainInfo(name='Base',           block_explorer_link='https://basescan.org/address'),
    '42161': ChainInfo(name='Arbitrum One',   block_explorer_link='https://arbiscan.io/address'),
    '1088':  ChainInfo(name='Metis',          block_explorer_link='https://explorer.metis.io/address'),
    '10':    ChainInfo(name='OP Mainnet',     block_explorer_link='https://optimistic.etherscan.io/address'),
    '56':    ChainInfo(name='BNB Smart Chain',block_explorer_link='https://bscscan.com/address'),
    '100':   ChainInfo(name='Gnosis',         block_explorer_link='https://gnosisscan.io/address'),
    '534352':ChainInfo(name='Scroll',         block_explorer_link='https://scrollscan.com/address'),
    '324':   ChainInfo(name='zkSync Era',     block_explorer_link='https://era.zksync.network/address'),
    '59144': ChainInfo(name='Linea',          block_explorer_link='https://lineascan.build/')
}


# ==============================
#  AaveGovernanceAPI
# ==============================
class AaveGovernanceAPI:
    """
    A utility class to interact with the BGD governance cache and retrieve 
    relevant information about Aave proposals and payload addresses.
    """

    def __init__(self) -> None:
        self.session = requests.Session()

    def get_proposal_data(self, proposal_id: int) -> BGDProposalData:
        """
        Fetches the proposal data from the BGD governance cache and 
        returns a pydantic-validated object.
        """
        proposal_data_link = f'{PROPOSALS_URL}/{proposal_id}.json'
        resp = self.session.get(proposal_data_link)
        resp.raise_for_status()

        raw_json = resp.json()
        # Parse into our data model
        return BGDProposalData(**raw_json)

    def get_payload_addresses(self, chain_id: str, controller: str, payload_id: int) -> List[str]:
        """
        Fetches and returns the addresses from a given chain/payload.
        """
        url = f'{BASE_BGD_CACHE_REPO}/{chain_id}/{controller}/payloads/{payload_id}.json'
        resp = self.session.get(url)
        resp.raise_for_status()
        
        payload_data = resp.json()
        # We only need the 'target' field from each action
        return [a['target'] for a in payload_data['payload']['actions']]
