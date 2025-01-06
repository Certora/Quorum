import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import Quorum.auto_report.aave_tags as aave_tags
import Quorum.utils.pretty_printer as pprinter


def run_create_report(args: argparse.Namespace):
    """
    Creates a report by applying provided tags to a template.
    Args:
        args (argparse.Namespace): Command line arguments containing:
            - template (Path): Path to the template file
            - proposal_id (int): ID of the proposal to generate report for
            - generate_report_path (Path, optional): Output path for the generated report.
                                                   Defaults to 'v3-{proposal_id}.md'
    Raises:
        FileNotFoundError: If the template file does not exist at the specified path
    The function:
    1. Validates template existence
    2. Sets default report path if none provided 
    3. Loads and renders template with proposal tags
    4. Writes rendered report to specified output path
    Returns:
        None
    """
    if not args.template.exists():
        raise FileNotFoundError(f'could not find template at {args.template}.')
    
    if args.generate_report_path is None:
        args.generate_report_path = Path(f'v3-{args.proposal_id}.md')


    pprinter.pretty_print(f'Generating a report using template in {args.template}', pprinter.Colors.INFO)
    env = Environment(loader=FileSystemLoader(args.template.parent))
    env.globals.update(zip=zip)
    template = env.get_template(args.template.name)
    
    pprinter.pretty_print(f'Retrieving tag information for proposal {args.proposal_id}', pprinter.Colors.INFO)
    tags = aave_tags.get_aave_tags(args.proposal_id)
    pprinter.pretty_print(f'Tag information retrieved', pprinter.Colors.INFO)

    report = template.render(tags)

    with open(args.generate_report_path, 'w') as f:
        f.write(report)

    pprinter.pretty_print(f'Created report at {args.generate_report_path}.', pprinter.Colors.SUCCESS)
