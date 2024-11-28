import requests
from collections import defaultdict

from Quorum.utils.chain_enum import Chain
from Quorum.utils.singleton import singleton
from .price_feed_utils import PriceFeedData, PriceFeedProviderBase, PriceFeedProvider


@singleton
class ChronicleAPI(PriceFeedProviderBase):
    """
    ChronicleAPI is a class designed to interact with the Chronicle data feed API.
    It fetches and stores price feed data for various blockchain networks supported by Chronicle.

    Attributes:
        session (requests.Session): A session object to manage HTTP requests.
        memory (dict): A cache to store fetched price feed data for each chain.
    """
    
    def __init__(self):
        super().__init__()
        self.__pairs = self.__process_pairs()

    def __process_pairs(self) -> dict[str, list[str]]:
        response = requests.get(
            "https://chroniclelabs.org/api/pairs?testnet=false"
        )
        response.raise_for_status()
        pairs = response.json()
        pairs = [
            p for p in pairs if p["blockchain"] in Chain.__members__.values()
        ]
        result = defaultdict(list)
        for p in pairs:
            result[p["blockchain"]].append(p["pair"])
        return result

    def _get_price_feeds_info(self, chain: Chain) -> dict[str, PriceFeedData]:
        """
        Get price feed data for a given blockchain network.

        Args:
            chain (Chain): The blockchain network to fetch price feeds for.

        Returns:
            dict[str, PriceFeedData]: A dictionary mapping the contract address of the price feed to the PriceFeedData object.
        """

        pairs = self.__pairs.get(chain)
        if not pairs:
            return {}
        
        chronicle_price_feeds: list[PriceFeedData] = []
        for pair in pairs:
            response = self.session.get(
                f"https://chroniclelabs.org/api/median/info/{pair}/{chain.value}/?testnet=false"
            )
            response.raise_for_status()
            data = response.json()
            
            for pair_info in data:
                chronicle_price_feeds.append(PriceFeedData(**pair_info))
                
        return {feed.address: feed for feed in chronicle_price_feeds}

        
    def get_name(self) -> PriceFeedProvider:
        return PriceFeedProvider.CHRONICLE
