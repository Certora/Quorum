import shutil
import argparse
from pathlib import Path

import Quorum.utils.pretty_printer as pp

def run_setup_quorum(args: argparse.Namespace):
    """
    Sets up a new Quorum working directory with template files and environment configuration.
    This function creates a new directory (if it doesn't exist) and populates it with required
    template files for Quorum operation. It also configures the environment variables.
    Args:
        args (argparse.Namespace): Command line arguments containing:
            - working_dir: Path object specifying target directory for setup
    Template files copied:
        - .env.example -> .env
        - execution.json
        - ground_truth.json  
        - README.md
    The function will:
    1. Create target directory if it doesn't exist
    2. Copy template files, skipping any that already exist
    3. Add QUORUM_PATH export to .env file
    Returns:
        None
    Raises:
        OSError: If there are filesystem permission issues
        shutil.Error: If file copy operations fail
    """
    templates_dir = Path(__file__).parent.parent.parent / 'templates'
    target_dir = args.working_dir.resolve()

    if not target_dir.exists():
        pp.pprint(f"Creating directory: {target_dir}", pp.Colors.INFO)
        target_dir.mkdir(parents=True, exist_ok=True)

    # Collect all file names to copy from the templates directory
    template_files = ['.env.example', 'execution.json', 'ground_truth.json', 'README.md']
    
    for file_name in template_files:
        src = templates_dir / file_name
        dest = target_dir / '.env' if file_name == '.env.example' else target_dir / file_name

        if dest.exists():
            pp.pprint(f"File exists: {dest}. Skipping.", pp.Colors.WARNING)
            continue

        shutil.copy(src, dest)
        pp.pprint(f"Copied {file_name} to {dest}", pp.Colors.SUCCESS)
    
    # Add export QUORUM_PATH="path_to_your_quorum_directory" to the new .env file
    with open(target_dir / '.env', 'a') as f:
        f.write(f'\nexport QUORUM_PATH="{target_dir}"\n')
    
    pp.pprint("Quorum setup completed successfully!", pp.Colors.SUCCESS)
