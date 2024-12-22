from enum import StrEnum


class Chain(StrEnum):
    """
    Enumeration for supported blockchain networks.
    """
    ETH = 'ETH'
    ARB = 'ARB'
    AVAX = 'AVAX'
    BASE = 'BASE'
    BSC = 'BSC'
    GNO = 'GNO'
    MET = 'MET'
    OPT = 'OPT'
    POLY = 'POLY'
    SCROLL = 'SCROLL'
    ZK = 'ZKSYNC'