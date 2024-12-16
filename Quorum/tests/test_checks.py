import pytest

from Quorum.apis.block_explorers.source_code import SourceCode
import Quorum.checks as Checks
from Quorum.utils.chain_enum import Chain
from Quorum.apis.price_feeds import ChainLinkAPI
import Quorum.config as config

from pathlib import Path
import shutil

from typing import Generator


@pytest.fixture
def source_codes() -> list[SourceCode]:
    sources_dir = Path(__file__).parent / 'resources/source_codes/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'
    sources = []
    for s in sources_dir.rglob('*.sol'):
        sources.append(SourceCode(str(s.relative_to(sources_dir)), s.read_text().splitlines()))
    return sources


def get_source_codes() -> list[SourceCode]:
    sources_dir = Path(__file__).parent / 'resources/source_codes/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'
    sources = []
    for s in sources_dir.rglob('*.sol'):
        sources.append(SourceCode(str(s.relative_to(sources_dir)), s.read_text().splitlines()))
    return sources


@pytest.fixture
def tmp_output_path() -> Generator[Path, None, None]:
    og_path = config.MAIN_PATH
    config.MAIN_PATH = Path(__file__).parent / 'tmp'
    yield config.MAIN_PATH  # Provide the temporary path to the test
    shutil.rmtree(config.MAIN_PATH)
    config.MAIN_PATH = og_path


def test_diff(source_codes: list[SourceCode], tmp_output_path: Path):
    diff_check = Checks.DiffCheck('Aave', Chain.ETH, '', source_codes)
    diff_check.target_repo = Path(__file__).parent / 'resources/clones/Aave/modules'

    missing_files = diff_check.find_diffs()

    assert len(missing_files) == 1
    assert len(list(tmp_output_path.rglob('*.patch'))) == 3


def test_global_variables(source_codes: list[SourceCode], tmp_output_path: Path):
    global_variables_check = Checks.GlobalVariableCheck('Aave', Chain.ETH, '', source_codes)
    global_variables_check.check_global_variables()

    assert next(global_variables_check.check_folder.iterdir(), None) is None


def test_price_feed(source_codes: list[SourceCode], tmp_output_path: Path):
    price_feed_check = Checks.PriceFeedCheck('Aave', Chain.ETH, '', source_codes, [ChainLinkAPI()])
    price_feed_check.verify_price_feed()

    assert len(list(tmp_output_path.rglob('*.json'))) == 1


def test_new_listing(source_codes: list[SourceCode], tmp_output_path: Path):
    new_listing_check = Checks.GlobalVariableCheck('Aave', Chain.ETH, '', source_codes)
    new_listing_check.check_global_variables()

    assert next(new_listing_check.check_folder.iterdir(), None) is None