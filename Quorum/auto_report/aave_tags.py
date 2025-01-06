import json5 as json
from pydantic import BaseModel
from typing import Any, Dict

from Quorum.apis.governance.aave_governance import AaveGovernanceAPI
from Quorum.apis.governance.data_models import BGDProposalData, IPFSData, ProposalData, EventData


BASE_SEATBELT_REPO = 'https://github.com/bgd-labs/seatbelt-gov-v3/blob/main/reports'
SEATBELT_PAYLOADS_URL = f'{BASE_SEATBELT_REPO}/payloads'


class ChainInfo(BaseModel):
    name: str
    block_explorer_link: str


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


def get_aave_tags(proposal_id: int) -> Dict[str, Any]:
    """
    Utility function that orchestrates calls to AaveGovernanceAPI
    and compiles the final dictionary of tags for a given proposal.

    Returns:
        A dictionary that can be directly rendered by your Jinja2 template.
    """
    api = AaveGovernanceAPI()
    bgd_data: BGDProposalData = api.get_proposal_data(proposal_id)

    # Safely unwrap fields (some might be None).
    ipfs_data: IPFSData = bgd_data.ipfs or IPFSData()
    proposal_data: ProposalData = bgd_data.proposal or ProposalData()
    create_event: EventData = bgd_data.events[0] if bgd_data.events else EventData()

    # Construct an empty dictionary for the Jinja2 context
    tags: Dict[str, Any] = {}

    # Basic info
    tags['proposal_id'] = str(proposal_id)
    tags['proposal_title'] = ipfs_data.title
    tags['voting_link'] = f'https://vote.onaave.com/proposal/?proposalId={proposal_id}'
    tags['gov_forum_link'] = ipfs_data.discussions

    # Multi-chain references
    tags['chain'] = []
    tags['payload_link'] = []
    tags['payload_seatbelt_link'] = []

    # Go through each payload in the proposal
    for p in proposal_data.payloads:
        # For each payload, retrieve the addresses from the API
        addresses = api.get_payload_addresses(
            chain_id = p.chain, 
            controller = p.payloads_controller,
            payload_id = p.payload_id
        )

        # For each address, build up the chain/payload references
        for i, address in enumerate(addresses, 1):
            chain_info = AAVE_CHAIN_MAPPING.get(p.chain)
            if not chain_info:
                # If chain info is missing, skip
                continue

            chain_display = chain_info.name + (f' {i}' if i != 1 else '')
            tags['chain'].append(chain_display)

            block_explorer_link = f'{chain_info.block_explorer_link}/{address}'
            tags['payload_link'].append(block_explorer_link)

            seatbelt_link = f'{SEATBELT_PAYLOADS_URL}/{p.chain}/{p.payloads_controller}/{p.payload_id}.md'
            tags['payload_seatbelt_link'].append(seatbelt_link)

    # Transaction info
    transaction_hash = create_event.transaction_hash
    tags['transaction_hash'] = transaction_hash
    tags['transaction_link'] = f'https://etherscan.io/tx/{transaction_hash}'

    # Creator + event args
    args = create_event.args
    tags['creator'] = args.creator 
    tags['access_level'] = args.access_level
    tags['ipfs_hash'] = args.ipfs_hash

    tags['createProposal_parameters_data'] = json.dumps(proposal_data.model_dump(), indent=4)

    # seatbelt link for entire proposal
    tags['seatbelt_link'] = f'{BASE_SEATBELT_REPO}/proposals/{proposal_id}.md'

    return tags
