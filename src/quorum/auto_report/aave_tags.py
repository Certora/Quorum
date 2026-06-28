import logging
from typing import Any

import json5 as json
from pydantic import BaseModel

from quorum.apis.governance.aave_governance import (
    AaveGovernanceAPI,
    ChainNotFoundException,
)
from quorum.apis.governance.data_models import (
    BGDProposalData,
    EventData,
    IPFSData,
    ProposalData,
)

BASE_SEATBELT_REPO = "https://github.com/bgd-labs/seatbelt-gov-v3/blob/main/reports"
SEATBELT_PAYLOADS_URL = f"{BASE_SEATBELT_REPO}/payloads"


class ChainInfo(BaseModel):
    name: str
    block_explorer_link: str


AAVE_CHAIN_MAPPING = {
    "1": ChainInfo(name="Ethereum", block_explorer_link="https://etherscan.io/address"),
    "137": ChainInfo(
        name="Polygon", block_explorer_link="https://polygonscan.com/address"
    ),
    "43114": ChainInfo(
        name="Avalanche", block_explorer_link="https://snowtrace.io/address"
    ),
    "8453": ChainInfo(name="Base", block_explorer_link="https://basescan.org/address"),
    "42161": ChainInfo(
        name="Arbitrum One", block_explorer_link="https://arbiscan.io/address"
    ),
    "1088": ChainInfo(
        name="Metis", block_explorer_link="https://explorer.metis.io/address"
    ),
    "10": ChainInfo(
        name="OP Mainnet", block_explorer_link="https://optimistic.etherscan.io/address"
    ),
    "56": ChainInfo(
        name="BNB Smart Chain", block_explorer_link="https://bscscan.com/address"
    ),
    "100": ChainInfo(
        name="Gnosis", block_explorer_link="https://gnosisscan.io/address"
    ),
    "534352": ChainInfo(
        name="Scroll", block_explorer_link="https://scrollscan.com/address"
    ),
    "324": ChainInfo(
        name="zkSync Era", block_explorer_link="https://era.zksync.network/address"
    ),
    "59144": ChainInfo(
        name="Linea", block_explorer_link="https://lineascan.build/address"
    ),
    "42220": ChainInfo(
        name="Celo", block_explorer_link="https://celo.blockscout.com/address"
    ),
    "146": ChainInfo(name="Sonic", block_explorer_link="https://sonicscan.org/address"),
    "143": ChainInfo(name="Monad", block_explorer_link="https://monadscan.com/address"),
}


def get_aave_tags(proposal_id: int) -> dict[str, Any]:
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
    tags: dict[str, Any] = {}

    # Basic info
    tags["proposal_id"] = str(proposal_id)
    tags["proposal_title"] = ipfs_data.title
    tags["voting_link"] = f"https://app.aave.com/governance/v3/proposal/?proposalId={proposal_id}"
    tags["gov_forum_link"] = ipfs_data.discussions

    # Multi-chain references
    tags["chain"] = []
    tags["payload_link"] = []
    tags["payload_seatbelt_link"] = []

    # Go through each payload in the proposal
    for p in proposal_data.payloads:
        chain_info = AAVE_CHAIN_MAPPING.get(p.chain)
        if not chain_info:
            # Unknown chain — can't build explorer links; skip.
            continue

        seatbelt_link = (
            f"{SEATBELT_PAYLOADS_URL}/{p.chain}/{p.payloads_controller}/{p.payload_id}.md"
        )

        # Retrieve the payload action addresses. Newly activated networks (e.g.
        # Monad) may not be indexed in BGD's per-payload cache yet even though the
        # proposal and its seatbelt report already exist — in that case degrade to
        # the payloads controller + seatbelt link rather than aborting the report.
        try:
            addresses = api.get_payload_addresses(
                chain_id=p.chain,
                controller=p.payloads_controller,
                payload_id=p.payload_id,
            )
        except ChainNotFoundException:
            logging.warning(
                "BGD payload cache miss for chain %s payload %s (%s); "
                "emitting controller + seatbelt link only.",
                p.chain,
                p.payload_id,
                p.payloads_controller,
            )
            addresses = []

        if addresses:
            # Build chain/payload references per resolved action address.
            for i, address in enumerate(addresses, 1):
                chain_display = chain_info.name + (f" {i}" if i != 1 else "")
                tags["chain"].append(chain_display)
                tags["payload_link"].append(f"{chain_info.block_explorer_link}/{address}")
                tags["payload_seatbelt_link"].append(seatbelt_link)
        else:
            # No resolved addresses (cache gap) — still surface the chain, the
            # payloads controller, and the seatbelt report.
            tags["chain"].append(chain_info.name)
            tags["payload_link"].append(
                f"{chain_info.block_explorer_link}/{p.payloads_controller}"
            )
            tags["payload_seatbelt_link"].append(seatbelt_link)

    # Transaction info
    transaction_hash = create_event.transaction_hash
    tags["transaction_hash"] = transaction_hash
    tags["transaction_link"] = f"https://etherscan.io/tx/{transaction_hash}"

    # Creator + event args
    args = create_event.args
    tags["creator"] = args.creator
    tags["access_level"] = args.access_level
    tags["ipfs_hash"] = args.ipfs_hash

    tags["createProposal_parameters_data"] = json.dumps(
        proposal_data.model_dump(), indent=4
    )

    # seatbelt link for entire proposal
    tags["seatbelt_link"] = f"{BASE_SEATBELT_REPO}/proposals/{proposal_id}.md"

    return tags
