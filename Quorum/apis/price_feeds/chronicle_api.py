import requests
from collections import defaultdict

from Quorum.utils.chain_enum import Chain
from Quorum.utils.singleton import Singleton

class ChronicleAPI(metaclass=Singleton):
    """
    ChronicleAPI is a class designed to interact with the Chronicle data feed API.
    It fetches and stores price feed data for various blockchain networks supported by Chronicle.

    Attributes:
        session (requests.Session): A session object to manage HTTP requests.
        memory (dict): A cache to store fetched price feed data for each chain.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.memory = defaultdict(list)
        self.info_url = "https://chroniclelabs.org/api/median/info/{}/{}/?testnet=false"
        self.__pairs = self.__process_pairs()

    def __process_pairs(self) -> dict[str, list[str]]:
        pairs = requests.get(
            "https://chroniclelabs.org/api/pairs?testnet=false"
        ).json()
        pairs = [
            p for p in pairs if p["blockchain"] in Chain.__members__.values()
        ]
        result = defaultdict(list)
        for p in pairs:
            result[p["blockchain"]].append(p["pair"])
        return result

    def get_price_feeds_info(self, chain: Chain) -> list[dict]:
        """
        Get price feed data for a given blockchain network.

        This method retrieves price feed data from the cache if it has been fetched previously.

        Args:
            chain (Chain): The blockchain network to fetch price feed data for.

        Returns:
            dict: The price feed data for the specified chain.
        """
        if chain not in self.memory:
            pairs = self.__pairs.get(chain)
            if not pairs:
                return []
            
            for pair in pairs:
                url = self.info_url.format(pair, chain.value)
                response = self.session.get(url)
                response.raise_for_status()
                data = response.json()
                
                for pair_info in data:
                    self.memory[chain].append(pair_info)
        
        return self.memory[chain]
