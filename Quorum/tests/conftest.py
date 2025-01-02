import pytest

from Quorum.apis.block_explorers.source_code import SourceCode
import Quorum.utils.config as config

from pathlib import Path
import shutil

from typing import Generator


RESOURCES_DIR = Path(__file__).parent / 'resources'
EXPECTED_DIR = Path(__file__).parent / 'expected'
SOURCE_CODES_DIR = RESOURCES_DIR / 'source_codes'


@pytest.fixture
def source_codes(request: pytest.FixtureRequest) -> list[SourceCode]:
    sources_dir: Path = SOURCE_CODES_DIR / request.param
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


@pytest.fixture
def tmp_cache() -> Generator[Path, None, None]:
    cache = Path(__file__).parent / 'tmp_cache'
    if cache.exists():
        shutil.rmtree(cache)
    cache.mkdir()
    yield cache
    shutil.rmtree(cache)


@pytest.fixture
def load_ipfs_and_code() -> tuple[str, str]:
    llm_dir = RESOURCES_DIR / "llm" / "ipfs_validation_chain"
    ipfs_path = llm_dir / "ipfs.txt"
    source_code_path = llm_dir / "source_code.sol"
    
    ipfs_content = ipfs_path.read_text()
    source_code = source_code_path.read_text()
    
    return ipfs_content, source_code