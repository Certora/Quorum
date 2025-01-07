import pytest

import Quorum.tests.conftest as conftest

from Quorum.apis.block_explorers.source_code import SourceCode
import Quorum.checks as Checks
from Quorum.utils.chain_enum import Chain
from Quorum.apis.price_feeds import ChainLinkAPI

from pathlib import Path


@pytest.mark.parametrize('source_codes', ['ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'], indirect=True)
def test_diff(source_codes: list[SourceCode], tmp_output_path: Path):
    diff_check = Checks.DiffCheck('Aave', Chain.ETH, '', source_codes)
    diff_check.target_repo = conftest.RESOURCES_DIR / 'clones/Aave/modules'

    missing_files = diff_check.find_diffs()

    assert len(missing_files) == 1
    assert (missing_files[0].file_name == 
            'src/20240711_Multi_ReserveFactorUpdatesMidJuly/AaveV2Ethereum_ReserveFactorUpdatesMidJuly_20240711.sol')
    
    diffs = [p.stem for p in diff_check.check_folder.rglob('*.patch')]
    assert sorted(diffs) == sorted(['AggregatorInterface', 'AaveV2Ethereum', 'AaveV2'])


@pytest.mark.parametrize('source_codes', ['bad_global_variables'], indirect=True)
def test_global_variables(source_codes: list[SourceCode], tmp_output_path: Path):
    global_variables_check = Checks.GlobalVariableCheck('Aave', Chain.ETH, '', source_codes)
    global_variables_check.check_global_variables()

    bad_files = [p.stem for p in global_variables_check.check_folder.iterdir()]
    assert len(bad_files) == 2
    assert sorted(bad_files) == sorted(['AaveV2Ethereum', 'AaveV2Ethereum_ReserveFactorUpdatesMidJuly_20240711'])


@pytest.mark.parametrize('source_codes', ['ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'], indirect=True)
def test_price_feed_check(source_codes: list[SourceCode], tmp_output_path: Path):
    price_feed_check = Checks.PriceFeedCheck('Aave', Chain.ETH, '', source_codes, [
        ChainLinkAPI()], [])
    price_feed_check.verify_price_feed()

    assert sorted([p.name for p in price_feed_check.check_folder.iterdir()]) == ['AaveV2Ethereum']


@pytest.mark.parametrize('source_codes', ['ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'], indirect=True)
def test_new_listing(source_codes: list[SourceCode], tmp_output_path: Path):
    new_listing_check = Checks.NewListingCheck('Aave', Chain.ETH, '', source_codes)
    new_listing_check.new_listing_check()

    assert next(new_listing_check.check_folder.iterdir(), None) is None
