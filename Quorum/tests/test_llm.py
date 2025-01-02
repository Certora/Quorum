import pytest

from Quorum.llm.chains.ipfs_validation_chain import IPFSValidationChain
from Quorum.llm.chains.first_deposit_chain import FirstDepositChain, ListingArray
from Quorum.apis.block_explorers.source_code import SourceCode

def test_ipfs_validation_chain(load_ipfs_and_code):
    ipfs_content, source_code = load_ipfs_and_code
    chain = IPFSValidationChain()
    prompt_templates = ['ipfs_validation_prompt_part1.j2', "ipfs_validation_prompt_part2.j2"]
    
    result = chain.execute(prompt_templates, ipfs_content, source_code)
    
    assert result is not None
    assert isinstance(result.incompatibilities, list)
    assert result.incompatibilities == []


@pytest.mark.parametrize('source_codes', ['ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'], indirect=True)
def test_first_deposit_chain(source_codes: list[SourceCode], expected_first_deposit_results):
    chain = FirstDepositChain()
    source_code = "\n".join(source_codes[1].file_content)
    
    result = chain.execute(source_code)
    
    assert ListingArray(**expected_first_deposit_results) == result
