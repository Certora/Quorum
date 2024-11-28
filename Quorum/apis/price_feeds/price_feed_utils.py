from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field
from pathlib import Path
import json
import requests

from Quorum.utils.chain_enum import Chain

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


class PriceFeedProviderBase(ABC):
    """
    PriceFeedProviderBase is an abstract base class for price feed providers.
    It defines the interface for fetching price feed data for different blockchain networks.

    Attributes:
        cache_dir (Path): The directory path to store the fetched price feed data.
    """

    def __init__(self):
        super().__init__()
        self.cache_dir = Path(f"{__file__.removesuffix('.py')}/cache/{self.get_name()}")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.memory: dict[Chain, dict[str, PriceFeedData]] = {}

    def get_feeds(self, chain: Chain) -> dict[str, PriceFeedData]:
        """
        Get price feed data for a given blockchain network from the cache.

        Args:
            chain (Chain): The blockchain network to fetch price feed data for.

        Returns:
            dict[str, PriceFeedData]: A dictionary mapping the contract address of the price feed to the price feed data.
        """
        cache_file = self.cache_dir / f"{chain.value}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as file:
                data: dict = json.load(file)
            self.memory[chain] = {addr: PriceFeedData(**feed) for addr, feed in data.items()}
        else:
            if chain not in self.memory:
                self.memory[chain] = self._get_price_feeds_info(chain)
                with open(cache_file, 'w') as file:
                    json.dump({addr: feed.dict() for addr, feed in self.memory[chain].items()}, file)
        return self.memory[chain]
    
    @abstractmethod
    def _get_price_feeds_info(self, chain: Chain) -> dict[str, PriceFeedData]:
        pass

    @abstractmethod
    def get_name(self) -> PriceFeedProvider:
        pass
