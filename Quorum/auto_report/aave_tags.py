import json5 as json
from typing import Any, Dict

# Import the data models and API
from Quorum.apis.governance.aave_governance import (
    AaveGovernanceAPI,
    AAVE_CHAIN_MAPPING,
    BASE_SEATBELT_REPO,
    SEATBELT_PAYLOADS_URL,
    BGDProposalData,
    IPFSData,
    ProposalData,
    EventData,
)


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
    tags['proposal_title'] = ipfs_data.title if ipfs_data.title else 'N/A'
    tags['voting_link'] = f'https://vote.onaave.com/proposal/?proposalId={proposal_id}'
    tags['gov_forum_link'] = ipfs_data.discussions if ipfs_data.discussions else 'N/A'

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
    transaction_hash = create_event.transactionHash or 'N/A'
    tags['transaction_hash'] = transaction_hash
    tags['transaction_link'] = f'https://etherscan.io/tx/{transaction_hash}'

    # Creator + event args
    args = create_event.args
    tags['creator'] = args.creator if args.creator else 'N/A'
    tags['access_level'] = str(args.accessLevel) if args.accessLevel is not None else 'N/A'
    tags['ipfs_hash'] = args.ipfsHash if args.ipfsHash else 'N/A'

    tags['createProposal_parameters_data'] = json.dumps(proposal_data.model_dump(), indent=4)

    # seatbelt link for entire proposal
    tags['seatbelt_link'] = f'{BASE_SEATBELT_REPO}/proposals/{proposal_id}.md'

    return tags
