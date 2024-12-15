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

    def _get_price_feed_info(self, chain: Chain, address: str) -> PriceFeedData | None:
        """
        Get price feed data for a given address on a blockchain network.

        Args:
            chain (Chain): The blockchain network to fetch price feeds for.
            address (str): The contract address of the price feed.

        Returns:
            PriceFeedData: The price feed data for the specified address.
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
                
        return next((feed for feed in chronicle_price_feeds if address == feed.address), None)

        
    def get_name(self) -> PriceFeedProvider:
        return PriceFeedProvider.CHRONICLE
