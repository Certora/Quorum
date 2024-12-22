from Quorum.utils.chain_enum import Chain
from Quorum.utils.singleton import singleton
from .price_feed_utils import PriceFeedData, PriceFeedProviderBase, PriceFeedProvider


@singleton
class CoinGeckoAPI(PriceFeedProviderBase):
    """
        CoinGeckoAPI is a class designed to interact with the CoinGecko API.
        It fetches and stores price feed data for various blockchain networks supported by CoinGecko.
    """

    # Mapping between Quorum Chains and CoinGecko Platforms
    CHAIN_TO_COINGECKO_PLATFORM_MAP = {
        Chain.ETH: 'ethereum',
        Chain.ARB: 'arbitrum-one',
        Chain.AVAX: 'avalanche',
        Chain.BASE: 'base',
        Chain.BSC: 'binance-smart-chain',
        Chain.GNO: 'gnosis',
        Chain.MET: 'metis-andromeda',
        Chain.OPT: 'optimistic-ethereum',
        Chain.POLY: 'polygon-pos',
        Chain.SCROLL: 'scroll',
        Chain.ZK: 'zksync',
    }

    COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/coins/{platform}/contract/{address}'
     
    def _get_price_feed_info(self, chain: Chain, address: str) -> PriceFeedData | None:
        """
        Get price feed data for a given address on a blockchain network.

        Args:
            chain (Chain): The blockchain network to fetch price feeds for.
            address (str): The contract address of the price feed.

        Returns:
            PriceFeedData: The price feed data for the specified address.
        """
        platform = self.CHAIN_TO_COINGECKO_PLATFORM_MAP.get(chain)
        if not platform:
            return None
        
        url = self.COINGECKO_API_URL.format(platform=platform, address=address)
        response = self.session.get(url)
        if response.status_code != 200:
            return None
        data: dict = response.json()
        if not data:
            return None
        network_platform_info: dict = data.get('detail_platforms')
        if not network_platform_info:
            return None
        details = network_platform_info.get(platform)
        if not details:
            return None
        return PriceFeedData(
            name=data.get('name'),
            pair=data.get('symbol'),
            address=details.get('contract_address'),
            decimals=details.get('decimal_place')
        )

    def get_name(self) -> PriceFeedProvider:
        return PriceFeedProvider.COINGECKO