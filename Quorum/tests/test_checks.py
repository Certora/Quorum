import pytest

import Quorum.tests.utils as utils

import Quorum.checks as Checks
from Quorum.utils.chain_enum import Chain
from Quorum.apis.price_feeds import ChainLinkAPI
import Quorum.config as config

from pathlib import Path
import shutil
import json

from typing import Generator


@pytest.fixture
def tmp_output_path() -> Generator[Path, None, None]:
    og_path = config.MAIN_PATH
    config.MAIN_PATH = Path(__file__).parent / 'tmp'
    yield config.MAIN_PATH  # Provide the temporary path to the test
    shutil.rmtree(config.MAIN_PATH)
    config.MAIN_PATH = og_path


def test_diff(tmp_output_path: Path):
    diff_check = Checks.DiffCheck('Aave', Chain.ETH, '',
                                  utils.load_source_codes('ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'))
    diff_check.target_repo = Path(__file__).parent / 'resources/clones/Aave/modules'

    missing_files = diff_check.find_diffs()

    assert len(missing_files) == 1
    assert (missing_files[0].file_name == 
            'src/20240711_Multi_ReserveFactorUpdatesMidJuly/AaveV2Ethereum_ReserveFactorUpdatesMidJuly_20240711.sol')
    
    diffs = [p.stem for p in diff_check.check_folder.rglob('*.patch')]
    assert sorted(diffs) == sorted(['AggregatorInterface', 'AaveV2Ethereum', 'AaveV2'])


def test_global_variables(tmp_output_path: Path):
    global_variables_check = Checks.GlobalVariableCheck('Aave', Chain.ETH, '',
                                                        utils.load_source_codes('bad_global_variables'))
    global_variables_check.check_global_variables()

    bad_files = [p.stem for p in global_variables_check.check_folder.iterdir()]
    assert len(bad_files) == 2
    assert sorted(bad_files) == sorted(['AaveV2Ethereum', 'AaveV2Ethereum_ReserveFactorUpdatesMidJuly_20240711'])


def test_price_feed(tmp_output_path: Path):
    price_feed_check = Checks.PriceFeedCheck('Aave', Chain.ETH, '',
                                             utils.load_source_codes('ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'),
                                             [ChainLinkAPI()])
    price_feed_check.verify_price_feed()

    assert sorted([p.name for p in price_feed_check.check_folder.iterdir()]) == ['AaveV2Ethereum']

