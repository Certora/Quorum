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
    COINGECKO = 'CoinGecko'

class PriceFeedData(BaseModel):
    name: Optional[str]
    pair: Optional[str | list]
    address: str = Field(..., alias='contractAddress')
    proxy_address: Optional[str] = Field(None, alias='proxyAddress')
    decimals: Optional[float | int]

    class Config:
        populate_by_name = True  # Allows population using field names
        extra = 'ignore'  # Ignores extra fields not defined in the model
    
    def __str__(self) -> str:
        s = ""
        s += f"Address: {self.address}\n"
        if self.name:
            s += f"Name: {self.name}\n"
        if self.pair:
            s += f"Pair: {self.pair}\n"
        if self.proxy_address:
            s += f"Proxy Address: {self.proxy_address}\n"
        if self.decimals:
            s += f"Decimals: {self.decimals}\n"
        return s
        




class PriceFeedProviderBase(ABC):
    """
    PriceFeedProviderBase is an abstract base class for price feed providers.
    It defines the interface for fetching price feed data for different blockchain networks.

    Attributes:
        cache_dir (Path): The directory path to store the fetched price feed data.
    """

    def __init__(self):
        super().__init__()
        self.cache_dir = Path(__file__).parent / "cache" / self.get_name().value
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.memory: dict[str, PriceFeedData] = {}

    def get_price_feed(self, chain: Chain, address: str) -> PriceFeedData | None: 
        """
        Get price feed data for a given blockchain network from the cache.

        Args:
            chain (Chain): The blockchain network to fetch price feed data for.
            address (str): The contract address of the price feed.

        Returns:
            PriceFeedData: The price feed data for the specified address or None if not found.
        """
        cache_file = self.cache_dir / f"{chain.value}" / f"{address}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as file:
                data: dict = json.load(file)
            self.memory[address] = PriceFeedData(**data)
        else:
            if address not in self.memory:
                self.memory[address] = self._get_price_feed_info(chain, address)
                if not self.memory[address]:
                    return None
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(cache_file, 'w') as file:
                    json.dump(self.memory[address].model_dump(mode="json"), file)
        return self.memory[address]
    
    @abstractmethod
    def _get_price_feed_info(self, chain: Chain, address: str) -> PriceFeedData:
        pass

    @abstractmethod
    def get_name(self) -> PriceFeedProvider:
        pass
