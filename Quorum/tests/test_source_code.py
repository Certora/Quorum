import pytest

import Quorum.tests.conftest as conftest

from Quorum.apis.block_explorers.source_code import SourceCode

import json5 as json


EXPECTED_DIR = conftest.EXPECTED_DIR / 'test_source_code'


@pytest.mark.parametrize('source_codes', ['ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'], indirect=True)
def test_get_state_variable(source_codes: list[SourceCode]):
    for s in source_codes:
        with open(EXPECTED_DIR / 'state_variables' / f'{s.file_name}.json') as f:
            expected = json.load(f)
        assert s.get_state_variables() == expected, f'{s.file_name} state variables do not match expected.'


@pytest.mark.parametrize('source_codes', ['ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'], indirect=True)
def test_get_functions(source_codes: list[SourceCode]):
    for s in source_codes:
        with open(EXPECTED_DIR / 'functions' / f'{s.file_name}.json') as f:
            expected = json.load(f)
        assert s.get_functions() == expected, f'{s.file_name} functions do not match expected.'
