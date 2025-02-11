import json5 as json

import quorum.tests.conftest as conftest
from quorum.apis.price_feeds import (
    ChainLinkAPI,
    CoinGeckoAPI,
    CoinMarketCapAPI,
    PriceFeedData,
)
from quorum.utils.chain_enum import Chain

EXPECTED_DIR = conftest.EXPECTED_DIR / "test_price_feed_providers"


def test_chainlink(tmp_cache):
    api = ChainLinkAPI()
    api.cache_dir = tmp_cache
    for file in (EXPECTED_DIR / "Chainlink" / "ETH").iterdir():
        with open(file) as f:
            expected = PriceFeedData(**json.load(f))
        assert api.get_price_feed(Chain.ETH, file.stem) == expected


# TODO: Find chronicle price feeds...
# def test_chronicle(tmp_cache):
#     api = ChronicleAPI()
#     api.cache_dir = tmp_cache
#     for file in (EXPECTED_DIR / 'Chronicle' / 'ETH').iterdir():
#         with open(file) as f:
#             expected = PriceFeedData(**json.load(f))
#         api.get_price_feed(Chain.ETH, file.stem) == expected


def test_coingecko(tmp_cache):
    api = CoinGeckoAPI()
    api.cache_dir = tmp_cache
    for file in (EXPECTED_DIR / "Coingecko" / "ETH").iterdir():
        with open(file) as f:
            expected = PriceFeedData(**json.load(f))
        assert api.get_price_feed(Chain.ETH, file.stem) == expected


def test_coinmarketcap():
    api = CoinMarketCapAPI()
    address = "0xc1Fa6E2E8667d9bE0Ca938a54c7E0285E9Df924a"
    data = api.get_price_feed(Chain.ETH, address)
    assert data.address.lower() == address.lower()
    assert (
        data.proxy_address.lower()
        == "0xCd5fE23C85820F7B72D0926FC9b05b43E359b7ee".lower()
    )
    assert data.name == "Wrapped eETH"
    assert data.pair == "weETH"
