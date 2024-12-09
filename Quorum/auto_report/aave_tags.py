import requests
from dataclasses import dataclass
import json


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
    '324': ChainInfo('zkSync Era', 'https://era.zksync.network/address')
}


def __extract_payload_address(chain_id: str, controller: str, payload_id: int) -> str:
    resp = requests.get(f'{BASE_BGD_CACHE_REPO}/{chain_id}/{controller}/payloads/{payload_id}.json')
    resp.raise_for_status()

    payload_data = resp.json()

    return payload_data['payload']['actions'][0]['target']


def get_aave_tags(proposal_id: int) -> dict:
    proposal_data_link = f'{PROPOSALS_URL}/{proposal_id}.json'
    resp = requests.get(proposal_data_link)
    resp.raise_for_status()

    proposal_data = resp.json()

    tags = {}
    tags['proposal_id'] = str(proposal_id)
    tags['proposal_title'] = proposal_data['ipfs']['title']
    tags['voting_link'] = f'https://vote.onaave.com/proposal/?proposalId={proposal_id}'
    tags['gov_forum_link'] = proposal_data['ipfs']['discussions']

    tags['chain'] = []
    tags['payload_link'] = []
    tags['payload_seatbelt_link'] = []
    for p in proposal_data['proposal']['payloads']:
        address = __extract_payload_address(p['chain'], p['payloadsController'], p['payloadId'])
        tags['chain'].append(AAVE_CHAIN_MAPPING[p['chain']].name)
        tags['payload_link'].append(f'{AAVE_CHAIN_MAPPING[p["chain"]].block_explorer_link}/{address}')
        tags['payload_seatbelt_link'].append(
            f'{SEATBELT_PAYLOADS_URL}/{p["chain"]}/{p["payloadsController"]}/{p["payloadId"]}.md'
        )
    
    tags['transaction_hash'] = proposal_data['events'][0]['transactionHash']
    tags['transaction_link'] = f'https://etherscan.io/tx/{tags["transaction_hash"]}'

    tags['creator'] = proposal_data['events'][0]['args']['creator']
    tags['access_level'] = str(proposal_data['events'][0]['args']['accessLevel'])
    tags['ipfs_hash'] = proposal_data['events'][0]['args']['ipfsHash']
    
    tags['createProposal_parameters_data'] = json.dumps({k: proposal_data['proposal'][k] for k 
                                                         in ['payloads', 'votingPortal', 'ipfsHash']}, indent=4)

    tags['seatbelt_link'] = f'{BASE_SEATBELT_REPO}/proposals/{proposal_id}.md'

    return tags
