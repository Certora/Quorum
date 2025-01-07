import json5 as json
from typing import Dict
import Quorum.utils.config as config
import Quorum.utils.pretty_printer as pp
import Quorum.apis.price_feeds as price_feeds


SUPPORTED_PROVIDERS = set(price_feeds.PriceFeedProvider.__members__.values())


def load_customer_config(customer: str) -> Dict[str, any]:
    """
    Load the customer ground truth configuration data from the ground truth file,
    and validate the price feed providers.

    Args:
        customer (str): The name or identifier of the customer.

    Returns:
        Dict[str, any]: The customer configuration data.
    """
    if not config.GROUND_TRUTH_PATH.exists():
        raise FileNotFoundError(f"Ground truth file not found at {config.GROUND_TRUTH_PATH}")

    with open(config.GROUND_TRUTH_PATH) as f:
        config_data = json.load(f)

    customer_config = config_data.get(customer)
    if not customer_config:
        pp.pprint(f"Customer {customer} not found in ground truth data.", pp.Colors.FAILURE)
        raise ValueError(f"Customer {customer} not found in ground truth data.")
    price_feed_providers = customer_config.get("price_feed_providers", [])
    token_providers = customer_config.get("token_validation_providers", [])
    unsupported = set(price_feed_providers).union(token_providers) - SUPPORTED_PROVIDERS
    if unsupported:
        pp.pprint(f"Unsupported providers for {customer}: {', '.join(unsupported)}", pp.Colors.FAILURE)
        price_feed_providers = list(set(price_feed_providers) & SUPPORTED_PROVIDERS)
        token_providers = list(set(token_providers) & SUPPORTED_PROVIDERS)
    
    # Replace the provider names with the actual API objects
    for i, provider in enumerate(price_feed_providers):
        if provider == price_feeds.PriceFeedProvider.CHAINLINK:
            price_feed_providers[i] = price_feeds.ChainLinkAPI()
        elif provider == price_feeds.PriceFeedProvider.CHRONICLE:
            price_feed_providers[i] = price_feeds.ChronicleAPI()

    for i, provider in enumerate(token_providers):
        if provider == price_feeds.PriceFeedProvider.COINGECKO:
            token_providers[i] = price_feeds.CoinGeckoAPI()
            
    customer_config["price_feed_providers"] = price_feed_providers
    customer_config["token_validation_providers"] = token_providers
    return customer_config
