from enum import StrEnum


class Chain(StrEnum):
    """
    Enumeration for supported blockchain networks.
    """

    ETH = "Ethereum"
    ARB = "Arbitrum"
    AVAX = "Avalanche"
    BASE = "Base"
    BSC = "BNB"
    GNO = "Gnosis"
    MET = "Metis"
    OPT = "Optimism"
    POLY = "Polygon"
    SCROLL = "Scroll"
    ZK = "ZKsync"
    LINEA = "Linea"
    CELO = "Celo"
    SONIC = "Sonic"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
