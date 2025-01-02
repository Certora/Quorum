import pytest

import Quorum.tests.conftest as conftest

from Quorum.utils.chain_enum import Chain
from Quorum.apis.price_feeds import PriceFeedData, ChainLinkAPI, ChronicleAPI, CoinGeckoAPI

import json5 as json


EXPECTED_DIR = conftest.EXPECTED_DIR / 'test_price_feed_providers'


def test_chainlink(tmp_cache):
    api = ChainLinkAPI()
    api.cache_dir = tmp_cache
    for file in (EXPECTED_DIR / 'Chainlink' / 'ETH').iterdir():
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
    for file in (EXPECTED_DIR / 'Coingecko' / 'ETH').iterdir():
        with open(file) as f:
            expected = PriceFeedData(**json.load(f))
        assert api.get_price_feed(Chain.ETH, file.stem) == expected