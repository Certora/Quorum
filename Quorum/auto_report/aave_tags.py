import json5 as json

from Quorum.apis.governance.aave_governance import (
    AaveGovernanceAPI,
    AAVE_CHAIN_MAPPING,
    BASE_SEATBELT_REPO,
    SEATBELT_PAYLOADS_URL,
)

def get_aave_tags(proposal_id: int) -> dict:
    """
    Utility function that orchestrates calls to AaveGovernanceAPI
    and compiles the final dictionary of tags for a given proposal.
    """
    api = AaveGovernanceAPI()
    proposal_data = api.get_proposal_data(proposal_id)

    ipfs: dict = proposal_data.get('ipfs', {})
    proposal: dict = proposal_data.get('proposal', {})
    create_event: dict = proposal_data.get('events', [{}])[0]  # The create event is always the first.

    tags = {}
    tags['proposal_id'] = str(proposal_id)
    tags['proposal_title'] = ipfs.get('title', 'N/A')
    tags['voting_link'] = f'https://vote.onaave.com/proposal/?proposalId={proposal_id}'
    tags['gov_forum_link'] = ipfs.get('discussions', 'N/A')

    # Prepare lists for multi-chain payload references
    tags['chain'], tags['payload_link'], tags['payload_seatbelt_link'] = [], [], []

    for p in proposal.get('payloads', []):
        if not all(k in p for k in ['chain', 'payloadsController', 'payloadId']):
            # Skip incomplete payload definitions
            continue

        chain_id = p['chain']
        controller = p['payloadsController']
        pid = p['payloadId']

        # Extract addresses from the payload
        addresses = api.get_payload_addresses(chain_id, controller, pid)

        # For each address, add chain name, block explorer link, seatbelt link, etc.
        for i, address in enumerate(addresses, 1):
            chain_info = AAVE_CHAIN_MAPPING.get(chain_id)
            if not chain_info:
                # If chain info is missing, skip
                continue

            chain_display = chain_info.name + (f' {i}' if i != 1 else '')
            tags['chain'].append(chain_display)
            
            block_explorer_link = f'{chain_info.block_explorer_link}/{address}'
            tags['payload_link'].append(block_explorer_link)
            
            seatbelt_link = f'{SEATBELT_PAYLOADS_URL}/{chain_id}/{controller}/{pid}.md'
            tags['payload_seatbelt_link'].append(seatbelt_link)

    tags['transaction_hash'] = create_event.get('transactionHash', 'N/A')
    tags['transaction_link'] = f'https://etherscan.io/tx/{tags["transaction_hash"]}'

    args: dict = create_event.get('args', {})
    tags['creator'] = args.get('creator', 'N/A')
    tags['access_level'] = str(args.get('accessLevel', 'N/A'))
    tags['ipfs_hash'] = args.get('ipfsHash', 'N/A')

    tags['createProposal_parameters_data'] = json.dumps(
        {k: proposal.get(k, 'N/A') for k in ['payloads', 'votingPortal', 'ipfsHash']},
        indent=4
    )

    tags['seatbelt_link'] = f'{BASE_SEATBELT_REPO}/proposals/{proposal_id}.md'

    return tags
