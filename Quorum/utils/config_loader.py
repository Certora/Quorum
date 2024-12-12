import json
from typing import Dict
import Quorum.config as config
import Quorum.utils.pretty_printer as pp
import Quorum.apis.price_feeds as price_feeds

SUPPORTED_PROVIDERS = set(price_feeds.PriceFeedProvider.__members__.values())

with open(config.GROUND_TRUTH_PATH) as f:
    config_data = json.load(f)

def load_customer_config(customer: str) -> Dict[str, any]:
    """
    Load the customer ground truth configuration data from the ground truth file,
    and validate the price feed providers.

    Args:
        customer (str): The name or identifier of the customer.

    Returns:
        Dict[str, any]: The customer configuration data.
    """
    customer_config = config_data.get(customer, {})
    providers = customer_config.get("price_feed_providers", [])
    unsupported = set(providers) - SUPPORTED_PROVIDERS
    if unsupported:
        pp.pretty_print(f"Unsupported providers for {customer}: {', '.join(unsupported)}", pp.Colors.FAILURE)
        providers = list(set(providers) & SUPPORTED_PROVIDERS)
        customer_config["price_feed_providers"] = providers
    
    # Replace the provider names with the actual API objects
    for i, provider in enumerate(providers):
        if provider == price_feeds.PriceFeedProvider.CHAINLINK:
            providers[i] = price_feeds.ChainLinkAPI()
        elif provider == price_feeds.PriceFeedProvider.CHRONICLE:
            providers[i] = price_feeds.ChronicleAPI()
        elif provider == price_feeds.PriceFeedProvider.COINGECKO:
            providers[i] = price_feeds.CoinGeckoAPI()
            
    customer_config["price_feed_providers"] = providers
    return customer_config
