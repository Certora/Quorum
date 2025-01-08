import os
from pathlib import Path
import json5 as json
from typing import Dict, Any

from Quorum.utils.load_env import load_env_variables
import Quorum.utils.pretty_printer as pp
from Quorum.utils.singleton import singleton
import Quorum.apis.price_feeds as price_feeds


@singleton
class QuorumConfiguration:
    def __init__(self):
        """
        Initialize the QuorumConfiguration instance. This constructor should do the
        minimal amount of work to prepare for lazy loading. For instance:
         - Environment variables are loaded immediately
         - Other data (like ground truth configs) is loaded only on demand
        """
        self.__env_loaded = False
        self.__main_path: Path | None = None
        self.__ground_truth_path: Path | None = None
        self.__anthropic_api_key: str | None = None
        self.__anthropic_model: str | None = None

        # This dictionary will cache customer configs after loading them from ground_truth.json
        self.__customer_configs: Dict[str, Any] = {}

        # Price feed providers must be validated on-the-fly
        self.__supported_providers = set(price_feeds.PriceFeedProvider.__members__.values())
        
        # We only load environment variables once
        self.__load_env()

    def __load_env(self) -> None:
        """
        Load environment variables and set up main paths. 
        This is called once in __init__ to ensure we have a minimal environment loaded.
        """
        if not self.__env_loaded:
            # 1. Load .env variables
            load_env_variables()

            # 2. Main path
            main_path = os.getenv("QUORUM_PATH")
            if not main_path:
                raise ValueError("QUORUM_PATH environment variable not set")

            self.__main_path = Path(main_path).absolute()
            if not self.__main_path.exists():
                self.__main_path.mkdir(parents=True)
            self.__ground_truth_path = self.__main_path / "ground_truth.json"

            # 3. Anthropic Key
            self.__anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if not self.__anthropic_api_key:
                pp.pprint(
                    "Warning: ANTHROPIC_API_KEY environment variable is not set. "
                    "All dependent checks will be skipped.",
                    pp.Colors.WARNING
                )

            # 4. Anthropic Model
            self.__anthropic_model = os.getenv('ANTROPIC_MODEL', 'claude-3-5-sonnet-20241022')

            self.__env_loaded = True

    @property
    def main_path(self) -> Path:
        """
        Returns the main path for Quorum, as determined by QUORUM_PATH.
        """
        return self.__main_path

    @main_path.setter
    def main_path(self, value: Path) -> None:
        self.__main_path = value

    @property
    def ground_truth_path(self) -> Path:
        """
        Returns the ground truth JSON path.
        """
        return self.__ground_truth_path

    @property
    def anthropic_api_key(self) -> str | None:
        """
        Returns the Anthropic API key, or None if not set.
        """
        return self.__anthropic_api_key

    @property
    def anthropic_model(self) -> str:
        """
        Returns the Anthropic Model or the default one if not set.
        """
        return self.__anthropic_model

    def load_customer_config(self, customer: str) -> Dict[str, Any]:
        """
        Load and validate the configuration data for a given customer.

        If the config for this customer has already been loaded, 
        return it from the cache (self._customer_configs).
        Otherwise, read from ground_truth.json, validate the price feed providers, 
        and store it in the cache.

        Args:
            customer (str): The name or identifier of the customer.

        Returns:
            dict[str, any]: The customer configuration data.

        Raises:
            FileNotFoundError: If the ground truth file does not exist.
            ValueError: If the requested customer is not found or invalid.
        """
        # 1. Check if we already loaded this config
        if customer in self.__customer_configs:
            return self.__customer_configs[customer]

        # 2. Check that ground_truth.json exists
        if not self.ground_truth_path.exists():
            raise FileNotFoundError(f"Ground truth file not found at {self.ground_truth_path}")

        # 3. Load the entire ground truth
        with open(self.ground_truth_path, 'r') as f:
            all_customers_config = json.load(f)

        # 4. Retrieve the config for the specific customer
        customer_config = all_customers_config.get(customer)
        if not customer_config:
            pp.pprint(f"Customer {customer} not found in ground truth data.", pp.Colors.FAILURE)
            raise ValueError(f"Customer {customer} not found in ground truth data.")

        # 5. Validate and transform the providers
        price_feed_providers = customer_config.get("price_feed_providers", [])
        token_providers = customer_config.get("token_validation_providers", [])

        unsupported = set(price_feed_providers).union(token_providers) - self.__supported_providers
        if unsupported:
            pp.pprint(f"Unsupported providers for {customer}: {', '.join(unsupported)}", pp.Colors.FAILURE)
            # Filter out unsupported ones
            price_feed_providers = list(set(price_feed_providers) & self.__supported_providers)
            token_providers = list(set(token_providers) & self.__supported_providers)

        # 6. Replace provider strings with actual API objects
        self._replace_providers_with_objects(price_feed_providers, token_providers)

        customer_config["price_feed_providers"] = price_feed_providers
        customer_config["token_validation_providers"] = token_providers

        # 7. Cache it
        self.__customer_configs[customer] = customer_config
        return customer_config

    def _replace_providers_with_objects(self, price_feed_providers: list, token_providers: list) -> None:
        """
        Helper method to replace string provider references with actual API objects.
        """
        for i, provider in enumerate(price_feed_providers):
            if provider == price_feeds.PriceFeedProvider.CHAINLINK:
                price_feed_providers[i] = price_feeds.ChainLinkAPI()
            elif provider == price_feeds.PriceFeedProvider.CHRONICLE:
                price_feed_providers[i] = price_feeds.ChronicleAPI()

        for i, provider in enumerate(token_providers):
            if provider == price_feeds.PriceFeedProvider.COINGECKO:
                token_providers[i] = price_feeds.CoinGeckoAPI()

