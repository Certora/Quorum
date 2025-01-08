from enum import StrEnum


class Chain(StrEnum):
    """
    Enumeration for supported blockchain networks.
    """
    ETH = 'Ethereum'
    ARB = 'Arbitrum'
    AVAX = 'Avalanche'
    BASE = 'Base'
    BSC = 'BNBChain'
    GNO = 'Gnosis'
    MET = 'Metis'
    OPT = 'Optimism'
    POLY = 'Polygon'
    SCROLL = 'Scroll'
    ZK = 'zkSync'
    LINEA= 'LINEA'
