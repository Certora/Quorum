import os

from quorum.utils.chain_enum import Chain
from quorum.utils.singleton import singleton

from .price_feed_utils import PriceFeedData, PriceFeedProvider, PriceFeedProviderBase


@singleton
class CoinMarketCapAPI(PriceFeedProviderBase):
    """
    CoinMarketCapAPI is a class designed to interact with the CoinMarketCap API.
    It fetches and stores price feed data for various blockchain networks supported by CoinMarketCap.
    """

    COINMARKETCAP_API_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("COINMARKETCAP_API_KEY")
        if not self.api_key:
            raise ValueError(
                "CoinMarketCap API key not found in environment variables.\n"
                "Please set COINMARKETCAP_API_KEY if you want to use CoinMarketCap API as a price feed provider,\n"
                "or remove CoinMarketCapAPI from the list of price feed providers."
            )

    def _get_price_feed_info(self, chain: Chain, address: str) -> PriceFeedData | None:
        """
        Get price feed data for a given address on a blockchain network.

        Args:
            chain (Chain): The blockchain network to fetch price feeds for.
            address (str): The contract address of the price feed.

        Returns:
            PriceFeedData: The price feed data for the specified address, or None if not found.
        """
        parameters = {
            "CMC_PRO_API_KEY": self.api_key,
            "address": address,
        }
        response = self.session.get(self.COINMARKETCAP_API_URL, params=parameters)
        if response.status_code in (401, 403):
            raise ValueError("Invalid or expired CoinMarketCap API key")
        if not response.ok:
            return None

        raw_data: dict = response.json()
        # Extract the first value from the "data" mapping
        price_data = next(iter(raw_data.get("data", {}).values()))
        if not price_data:
            return None

        # Check if platform data exists and the platform name matches the provided chain (case-insensitive)
        if (
            not price_data.get("platform")
            or not price_data["platform"].get("name")
            or price_data["platform"]["name"].lower() != chain.value.lower()
        ):
            return None

        # Update the data with the token address from the platform info
        token_address = price_data["platform"]["token_address"]
        # Add the proxy address to the price feed data if available
        if token_address:
            price_data.update({"proxy_address": token_address})
        price_data.update({"address": address})
        return PriceFeedData(**price_data)

    def get_name(self) -> PriceFeedProvider:
        """
        Return the provider name for identification.
        """
        return PriceFeedProvider.COINMARKETCAP
