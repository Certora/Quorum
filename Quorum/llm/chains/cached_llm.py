from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache

from Quorum.utils.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL


class CachedLLM:
    """
    A class to manage the Anthropic LLM with caching enabled.

    Attributes:
        llm (ChatAnthropic): The Anthropic LLM instance with caching enabled.
    """

    def __init__(self):
        cache_dir = Path(__file__).parent.parent / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        set_llm_cache(SQLiteCache(database_path=cache_dir / f"{Path(__file__).stem}_cache.db"))

        self.llm = ChatAnthropic(
            model=ANTHROPIC_MODEL,
            cache=True,
            max_retries=3,
            temperature=0.0,
            api_key=ANTHROPIC_API_KEY,
        )
