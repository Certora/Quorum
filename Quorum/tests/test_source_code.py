import pytest

import Quorum.tests.utils as utils

import json


def test_get_state_variable():
    source_codes = utils.load_source_codes('ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637')
    for s in source_codes:
        with open(utils.EXPECTED_DIR / 'test_source_code' / 'state_variables' / f'{s.file_name}.json') as f:
            expected = json.load(f)
        assert s.get_state_variables() == expected, f'{s.file_name} state variables do not match expected.'


def test_get_functions():
    source_codes = utils.load_source_codes('ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637')
    for s in source_codes:
        with open(utils.EXPECTED_DIR / 'test_source_code' / 'functions' / f'{s.file_name}.json') as f:
            expected = json.load(f)
        assert s.get_functions() == expected, f'{s.file_name} functions do not match expected.'
