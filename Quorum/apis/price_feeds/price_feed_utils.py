from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field

class PriceFeedProvider(StrEnum):
    """
    Enumeration for supported price feed providers.
    """
    CHAINLINK = 'Chainlink'
    CHRONICLE = 'Chronicle'


class PriceFeedData(BaseModel):
    name: Optional[str]
    pair: Optional[str | list]
    address: str = Field(..., alias='contractAddress')
    proxy_address: Optional[str] = Field(None, alias='proxyAddress')

    class Config:
        allow_population_by_field_name = True  # Allows population using field names
        extra = 'ignore'  # Ignores extra fields not defined in the model
