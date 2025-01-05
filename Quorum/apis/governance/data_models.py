from typing import List, Optional
from pydantic import BaseModel, Field

from Quorum.utils.chain_enum import Chain

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


class PayloadAddresses(BaseModel):
    chain: Chain
    addresses: List[str]
