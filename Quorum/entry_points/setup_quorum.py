import shutil
import argparse
from pathlib import Path
import Quorum.utils.pretty_printer as pp


def get_working_directory() -> Path:
    parser = argparse.ArgumentParser(description="Setup Quorum project.")
    parser.add_argument(
        '--working_dir',
        default=Path.cwd(),
        type=Path,
        help="Directory to set up the Quorum project."
    )
    args = parser.parse_args()
    return args.working_dir


def setup_quorum(working_dir: Path):
    """
    Initializes a Quorum environment by copying template files to the specified directory.

    Args:
        working_dir (Path): Target directory for setting up Quorum.

    Raises:
        shutil.Error: If copying files fails.
        OSError: If directory creation fails.
    """
    templates_dir = Path(__file__).parent.parent / 'templates'
    target_dir = working_dir.resolve()

    if not target_dir.exists():
        pp.pretty_print(f"Creating directory: {target_dir}", pp.Colors.INFO)
        target_dir.mkdir(parents=True, exist_ok=True)

    template_files = ['ground_truth.json', 'execution.json', '.env.example', 'Readme.md']

    for file_name in template_files:
        src = templates_dir / file_name
        dest = target_dir / '.env' if file_name == '.env.example' else target_dir / file_name

        if dest.exists():
            pp.pretty_print(f"File exists: {dest}. Skipping.", pp.Colors.WARNING)
            continue

        shutil.copy(src, dest)
        pp.pretty_print(f"Copied {file_name} to {dest}", pp.Colors.SUCCESS)

    pp.pretty_print("Quorum setup completed successfully!", pp.Colors.SUCCESS)


def main():
    working_dir = get_working_directory()
    try:
        setup_quorum(working_dir)
    except Exception as e:
        pp.pretty_print(f"Setup failed: {e}", pp.Colors.FAILURE)
        exit(1)


if __name__ == "__main__":
    main()
