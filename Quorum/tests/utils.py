from Quorum.apis.block_explorers.source_code import SourceCode

from pathlib import Path


RESOURCES_DIR = Path(__file__).parent / 'resources'
EXPECTED_DIR = Path(__file__).parent / 'expected'
SOURCE_CODES_DIR = RESOURCES_DIR / 'source_codes'


def load_source_codes(sources: str) -> list[SourceCode]:
    sources_dir = SOURCE_CODES_DIR / sources
    sources = []
    for s in sources_dir.rglob('*.sol'):
        sources.append(SourceCode(str(s.relative_to(sources_dir)), s.read_text().splitlines()))
    return sources
