import requests
from pydantic import BaseModel
from typing import Optional

from ProposalTools.Utils.chain_enum import Chain
from ProposalTools.Utils.singleton import Singleton

class Docs(BaseModel):
    assetClass: Optional[str] = None 
    assetName: Optional[str] = None
    baseAsset: Optional[str] = None
    baseAssetClic: Optional[str] = None
    blockchainName: Optional[str] = None
    clicProductName: Optional[str] = None
    deliveryChannelCode: Optional[str] = None
    feedType: Optional[str] = None
    hidden: Optional[bool] = None
    marketHours: Optional[str] = None
    productSubType: Optional[str] = None
    productType: Optional[str] = None
    productTypeCode: Optional[str] = None
    quoteAsset: Optional[str] = None
    quoteAssetClic: Optional[str] = None


class PriceFeedData(BaseModel):
    compareOffchain: Optional[str] = None
    contractAddress: str
    contractType: Optional[str] = None
    contractVersion: Optional[int] = None
    decimalPlaces: Optional[int] = None
    ens: Optional[str] = None
    formatDecimalPlaces: Optional[int] = None
    healthPrice: Optional[str] = None
    heartbeat: Optional[int] = None
    history: Optional[str | bool] = None
    multiply: Optional[str] = None
    name: Optional[str] = None
    pair: Optional[list[Optional[str]]] = None
    path: Optional[str] = None
    proxyAddress: Optional[str] = None
    threshold: Optional[float] = None
    valuePrefix: Optional[str] = None
    assetName: Optional[str] = None
    feedCategory: Optional[str] = None
    feedType: Optional[str] = None
    docs: Optional[Docs] = None
    decimals: Optional[int] = None


class ChainLinkAPI(metaclass=Singleton):
    """
    ChainLinkAPI is a class designed to interact with the Chainlink data feed API.
    It fetches and stores price feed data for various blockchain networks supported by Chainlink.

    Attributes:
        chain_mapping (dict): A mapping of supported blockchain networks (Chain enum) to their corresponding Chainlink API URLs.
        session (requests.Session): A session object to manage HTTP requests.
        memory (dict): A cache to store fetched price feed data for each chain.
    """
    
    chain_mapping = {
        Chain.ARB: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-arbitrum-1.json",
        Chain.AVAX: "https://reference-data-directory.vercel.app/feeds-avalanche-mainnet.json",
        Chain.BSC: "https://reference-data-directory.vercel.app/feeds-bsc-mainnet.json",
        Chain.ETH: "https://reference-data-directory.vercel.app/feeds-mainnet.json",
        Chain.BASE: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-base-1.json",
        Chain.GNO: "https://reference-data-directory.vercel.app/feeds-xdai-mainnet.json",
        Chain.MET: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-andromeda-1.json",
        Chain.OPT: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-optimism-1.json",
        Chain.POLY: "https://reference-data-directory.vercel.app/feeds-matic-mainnet.json",
        Chain.SCR: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-scroll-1.json"
    }

    def __init__(self) -> None:
        """
        Initialize the ChainLinkAPI instance.
        
        Creates an HTTP session for managing requests and initializes an in-memory cache to store
        price feed data for different blockchain networks.
        """
        self.session = requests.Session()
        self.memory: dict[Chain, list[PriceFeedData]] = {}
    
    def get_price_feeds_info(self, chain: Chain) -> list[PriceFeedData]:
        """
        Fetches the price feeds information from the Chainlink API for a specified blockchain network.
        
        This method first checks if the data for the given chain is already cached in memory. If not, it makes an HTTP 
        request to the Chainlink API to fetch the data, parses the JSON response into a list of PriceFeedData objects, 
        and stores it in the cache.

        Args:
            chain (Chain): The blockchain network to fetch price feeds for.

        Returns:
            list[PriceFeedData]: A list of PriceFeedData objects containing the price feeds information.
        
        Raises:
            requests.HTTPError: If the HTTP request to the Chainlink API fails.
            KeyError: If the specified chain is not supported.
        """
        if chain not in self.memory:
            url = self.chain_mapping.get(chain)
            if not url:
                raise KeyError(f"Chain {chain.name} is not supported.")
            
            response = self.session.get(url)
            response.raise_for_status()
            self.memory[chain] = [PriceFeedData(**feed) for feed in response.json()]
        
        return self.memory[chain]
