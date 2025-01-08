from pydantic import BaseModel, Field

from quorum.utils.chain_enum import Chain


class IPFSData(BaseModel):
    title: str = "N/A"
    discussions: str = "N/A"


class PayloadData(BaseModel):
    chain: str
    payloads_controller: str = Field(alias="payloadsController")
    payload_id: int = Field(alias="payloadId")

    class Config:
        allow_population_by_alias = True


class ProposalData(BaseModel):
    payloads: list[PayloadData] = Field(default_factory=list)
    voting_portal: str | None = Field(alias="votingPortal")
    ipfs_hash: str | None = Field(alias="ipfsHash")
    access_level: str | int | None = Field(alias="accessLevel")

    class Config:
        allow_population_by_alias = True


class EventArgs(BaseModel):
    creator: str = "N/A"
    access_level: str | int | None = Field(alias="accessLevel", default="N/A")
    ipfs_hash: str = Field(alias="ipfsHash", default="N/A")

    class Config:
        allow_population_by_alias = True


class EventData(BaseModel):
    transaction_hash: str = Field(alias="transactionHash")
    args: EventArgs = Field(default_factory=EventArgs)


class BGDProposalData(BaseModel):
    """
    Represents the entire JSON structure returned by the BGD cache
    for a given proposal.
    """

    ipfs: IPFSData | None = None
    proposal: ProposalData | None = None
    events: list[EventData] = Field(default_factory=list)


class PayloadAddresses(BaseModel):
    chain: Chain
    addresses: list[str]
