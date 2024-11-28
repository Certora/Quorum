from enum import StrEnum


class PriceFeedProvider(StrEnum):
    """
    Enumeration for supported price feed providers.
    """
    CHAINLINK = 'Chainlink'
    CHRONICLE = 'Chronicle'
