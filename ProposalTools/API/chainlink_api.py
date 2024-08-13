import requests
from pydantic import BaseModel
from typing import Optional

from ProposalTools.Utils.chain_enum import Chain


class Docs(BaseModel):
    assetClass: Optional[str]
    assetName: Optional[str]
    baseAsset: Optional[str]
    baseAssetClic: Optional[str]
    blockchainName: Optional[str]
    clicProductName: Optional[str]
    deliveryChannelCode: Optional[str]
    feedType: Optional[str]
    hidden: Optional[bool]
    marketHours: Optional[str]
    productSubType: Optional[str]
    productType: Optional[str]
    productTypeCode: Optional[str]
    quoteAsset: Optional[str]
    quoteAssetClic: Optional[str]

    def __str__(self) -> str:
        fields = [
            f"  Asset Class: {self.assetClass}" if self.assetClass else "",
            f"  Asset Name: {self.assetName}" if self.assetName else "",
            f"  Base Asset: {self.baseAsset}" if self.baseAsset else "",
            f"  Base Asset CLIC: {self.baseAssetClic}" if self.baseAssetClic else "",
            f"  Blockchain Name: {self.blockchainName}" if self.blockchainName else "",
            f"  CLIC Product Name: {self.clicProductName}" if self.clicProductName else "",
            f"  Delivery Channel Code: {self.deliveryChannelCode}" if self.deliveryChannelCode else "",
            f"  Feed Type: {self.feedType}" if self.feedType else "",
            f"  Hidden: {self.hidden}" if self.hidden is not None else "",
            f"  Market Hours: {self.marketHours}" if self.marketHours else "",
            f"  Product Sub-Type: {self.productSubType}" if self.productSubType else "",
            f"  Product Type: {self.productType}" if self.productType else "",
            f"  Product Type Code: {self.productTypeCode}" if self.productTypeCode else "",
            f"  Quote Asset: {self.quoteAsset}" if self.quoteAsset else "",
            f"  Quote Asset CLIC: {self.quoteAssetClic}" if self.quoteAssetClic else ""
        ]
        return "\n".join(filter(None, fields))

class PriceFeedData(BaseModel):
    compareOffchain: Optional[str]
    contractAddress: str
    contractType: Optional[str]
    contractVersion: Optional[int]
    decimalPlaces: Optional[int]
    ens: Optional[str]
    formatDecimalPlaces: Optional[int]
    healthPrice: Optional[str]
    heartbeat: Optional[int]
    history: Optional[str]
    multiply: Optional[str]
    name: Optional[str]
    pair: Optional[list[Optional[str]]]
    path: Optional[str]
    proxyAddress: Optional[str]
    threshold: Optional[int]
    valuePrefix: Optional[str]
    assetName: Optional[str]
    feedCategory: Optional[str]
    feedType: Optional[str]
    docs: Optional[Docs]
    decimals: Optional[int]

    def __str__(self) -> str:
        pair_str = ", ".join([str(p) for p in self.pair]) if self.pair else "None"
        fields = [
            f"  Compare Offchain: {self.compareOffchain}" if self.compareOffchain else "",
            f"  Contract Address: {self.contractAddress}",
            f"  Contract Type: {self.contractType}" if self.contractType else "",
            f"  Contract Version: {self.contractVersion}" if self.contractVersion is not None else "",
            f"  Decimal Places: {self.decimalPlaces}" if self.decimalPlaces is not None else "",
            f"  ENS: {self.ens}" if self.ens else "",
            f"  Format Decimal Places: {self.formatDecimalPlaces}" if self.formatDecimalPlaces is not None else "",
            f"  Health Price: {self.healthPrice}" if self.healthPrice else "",
            f"  Heartbeat: {self.heartbeat}" if self.heartbeat is not None else "",
            f"  History: {self.history}" if self.history else "",
            f"  Multiply: {self.multiply}" if self.multiply else "",
            f"  Name: {self.name}" if self.name else "",
            f"  Pair: {pair_str}" if pair_str != ", " else "",
            f"  Path: {self.path}" if self.path else "",
            f"  Proxy Address: {self.proxyAddress}" if self.proxyAddress else "",
            f"  Threshold: {self.threshold}" if self.threshold is not None else "",
            f"  Value Prefix: {self.valuePrefix}" if self.valuePrefix else "",
            f"  Asset Name: {self.assetName}" if self.assetName else "",
            f"  Feed Category: {self.feedCategory}" if self.feedCategory else "",
            f"  Feed Type: {self.feedType}" if self.feedType else "",
            f"  Docs: \n{str(self.docs) if self.docs else 'None'}" if self.docs else "",
            f"  Decimals: {self.decimals}" if self.decimals is not None else ""
        ]
        return "PriceFeedData:\n" + "\n".join(filter(None, fields))


class ChainLinkAPI:
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
