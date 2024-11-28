import requests

from Quorum.utils.chain_enum import Chain
from Quorum.utils.singleton import Singleton
from .price_feed_utils import PriceFeedData


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
        Chain.SCR: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-scroll-1.json",
        Chain.ZK: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-zksync-1.json"
    }

    def __init__(self) -> None:
        """
        Initialize the ChainLinkAPI instance.
        
        Creates an HTTP session for managing requests and initializes an in-memory cache to store
        price feed data for different blockchain networks.
        """
        self.session = requests.Session()
        self.memory: dict[Chain, dict[str, PriceFeedData]] = {}
    
    def get_price_feeds_info(self, chain: Chain) -> dict[str, PriceFeedData]:
        """
        Fetches the price feeds information from the Chainlink API for a specified blockchain network.

        The method fetches the price feed data from the Chainlink API and stores it in the memory cache.
        Args:
            chain (Chain): The blockchain network to fetch price feeds for.

        Returns:
            dict[str, PriceFeedData]: A dictionary mapping the contract address of the price feed to the PriceFeedData object.
        
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
            chain_link_price_feeds = [PriceFeedData(**feed) for feed in response.json()]
            chain_link_price_feeds = {feed.address: feed for feed in chain_link_price_feeds}
            chain_link_price_feeds.update({feed.proxy_address: feed for feed in chain_link_price_feeds.values() if feed.proxy_address})
            self.memory[chain] = chain_link_price_feeds
        
        return self.memory[chain]
