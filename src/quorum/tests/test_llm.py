from quorum.llm.chains.first_deposit_chain import FirstDepositChain, ListingArray
from quorum.llm.chains.ipfs_validation_chain import IPFSValidationChain
from quorum.utils.quorum_configuration import QuorumConfiguration

SKIP = QuorumConfiguration().anthropic_api_key == "SKIP_TEST_KEY"


def test_ipfs_validation_chain(load_ipfs_validation_chain_inputs):
    if SKIP:
        assert True
        return None

    ipfs_content, source_code = load_ipfs_validation_chain_inputs
    chain = IPFSValidationChain()
    prompt_templates = ["ipfs_validation_prompt.j2"]

    result = chain.execute(prompt_templates, ipfs_content, source_code)

    subject = "DAI Reserve Factor"
    subject_in_ipfs = "70.00%"
    subject_in_solidity = "75.00%"

    assert result.incompatibilities
    assert subject in result.incompatibilities[0].subject
    assert subject_in_ipfs in result.incompatibilities[0].subject_in_ipfs
    assert subject_in_solidity in result.incompatibilities[0].subject_in_solidity


def test_first_deposit_chain(first_deposit_chain_input, expected_first_deposit_results):
    if SKIP:
        assert True
        return None

    source_code = first_deposit_chain_input

    chain = FirstDepositChain()

    result = chain.execute(source_code)

    assert ListingArray(**expected_first_deposit_results) == result
