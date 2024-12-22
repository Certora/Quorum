from Quorum.utils.chain_enum import Chain
from Quorum.utils.singleton import singleton
from .price_feed_utils import PriceFeedData, PriceFeedProviderBase, PriceFeedProvider

@singleton
class ChainLinkAPI(PriceFeedProviderBase):
    """
    ChainLinkAPI is a class designed to interact with the Chainlink data feed API.
    It fetches and stores price feed data for various blockchain networks supported by Chainlink.
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
        Chain.SCROLL: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-scroll-1.json",
        Chain.ZK: "https://reference-data-directory.vercel.app/feeds-ethereum-mainnet-zksync-1.json"
    }
    
    def _get_price_feed_info(self, chain: Chain, address: str) -> PriceFeedData | None:
        """
        Get price feed data for a given address on a blockchain network.

        Args:
            chain (Chain): The blockchain network to fetch price feeds for.
            address (str): The contract address of the price feed.

        Returns:
            PriceFeedData: The price feed data for the specified address.
        """
        url = self.chain_mapping.get(chain)
        if not url:
            raise KeyError(f"Chain {chain.name} is not supported.")
        
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        price_feeds = [PriceFeedData(**feed) for feed in data]
        address_feed = next((feed for feed in price_feeds if address in [feed.proxy_address, feed.address]), None)
        return address_feed

    def get_name(self) -> PriceFeedProvider:
        return PriceFeedProvider.CHAINLINK
