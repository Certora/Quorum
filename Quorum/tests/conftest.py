import pytest
import shutil
import json5 as json
from pathlib import Path
from typing import Generator

from Quorum.apis.block_explorers.source_code import SourceCode
from Quorum.utils.quorum_configuration import QuorumConfiguration


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
    config = QuorumConfiguration()
    og_path = config.main_path
    config.main_path = Path(__file__).parent / 'tmp'
    yield config.main_path  # Provide the temporary path to the test
    shutil.rmtree(config.main_path)
    config.main_path = og_path


@pytest.fixture
def tmp_cache() -> Generator[Path, None, None]:
    cache = Path(__file__).parent / 'tmp_cache'
    if cache.exists():
        shutil.rmtree(cache)
    cache.mkdir()
    yield cache
    shutil.rmtree(cache)


@pytest.fixture(scope="module")
def load_ipfs_validation_chain_inputs() -> tuple[str, str]:
    llm_resource_dir = RESOURCES_DIR / "llm" / "ipfs_validation_chain"
    ipfs_path = llm_resource_dir / "ipfs.txt"
    source_code_path = llm_resource_dir / "source_code.sol"

    ipfs_content = ipfs_path.read_text(encoding="utf-8")
    source_code = source_code_path.read_text(encoding="utf-8")

    return ipfs_content, source_code

@pytest.fixture
def expected_first_deposit_results():
    expected_path = EXPECTED_DIR / 'test_llm' / 'first_deposit_chain.json'
    with open(expected_path) as f:
        expected = json.load(f)
    return expected

@pytest.fixture
def first_deposit_chain_input():
    llm_resource_dir = RESOURCES_DIR / "llm" / "first_deposit_chain"
    source_code_path = llm_resource_dir / "source_code.sol"

    source_code = source_code_path.read_text(encoding="utf-8")

    return source_code
