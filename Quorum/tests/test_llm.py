import pytest

from Quorum.llm.chains.ipfs_validation_chain import IPFSValidationChain
from Quorum.llm.chains.first_deposit_chain import FirstDepositChain, ListingArray
from Quorum.apis.block_explorers.source_code import SourceCode

def test_ipfs_validation_chain(load_ipfs_validation_chain_inputs):
    ipfs_content, source_code = load_ipfs_validation_chain_inputs
    chain = IPFSValidationChain()
    prompt_templates = ['ipfs_validation_prompt_part1.j2', "ipfs_validation_prompt_part2.j2"]
    
    result = chain.execute(prompt_templates, ipfs_content, source_code)

    subject = "DAI Reserve Factor"
    subject_in_ipfs = '70.00%'
    subject_in_solidity = '75.00%'

    assert result.incompatibilities
    assert subject in result.incompatibilities[0].subject
    assert subject_in_ipfs in result.incompatibilities[0].subject_in_ipfs
    assert subject_in_solidity in result.incompatibilities[0].subject_in_solidity


def test_first_deposit_chain(first_deposit_chain_input, expected_first_deposit_results):
    source_code = first_deposit_chain_input
    
    chain = FirstDepositChain()

    result = chain.execute(source_code)
    
    assert ListingArray(**expected_first_deposit_results) == result
