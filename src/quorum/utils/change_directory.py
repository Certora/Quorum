import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def change_directory(path: Path):
    """
    Context manager to temporarily change the working directory.

    Args:
        path (Path): The directory to switch to.
    """
    original_dir = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)
