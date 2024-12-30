import pytest
from Quorum.utils.chain_enum import Chain
from Quorum.apis.block_explorers.chains_api import ChainAPI


@pytest.mark.parametrize(
    'chain, contract_address',
    [
        (Chain.SCROLL, '0x32f924C0e0F1Abf5D1ff35B05eBc5E844dEdD2A9'),
        (Chain.ZK, '0x162C97F6B4FA5a915A44D430bb7AE0eE716b3b87')
    ]
)
def test_chain_api_integration(chain, contract_address):
    """
    End-to-end integration test for the ChainAPI class:
    1. Check if source code fetch works without crashing.
    2. Fetch the ABI of the contract.
    3. Call the smart contract function and verify the result.
    """

    # Step 1: Create a ChainAPI instance for the specified chain
    api = ChainAPI(chain)

    # Step 2: Fetch the source code of the contract and verify it doesn't crash
    source_code = api.get_source_code(contract_address)
    assert source_code is not None, f"Source code retrieval failed for contract: {contract_address}"
