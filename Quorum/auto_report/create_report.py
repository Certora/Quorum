import Quorum.auto_report.aave_tags as aave_tags
import Quorum.utils.pretty_printer as pprinter

import argparse
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


DEFAULT_TEMPLATE_PATH = Path(__file__).parent / 'AaveReportTemplate.md.j2'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='This tool generates automatic proposal reports.')
    parser.add_argument('--proposal_id', required=True, type=int, help='The proposal id to generate report to.')
    parser.add_argument('--template', default=DEFAULT_TEMPLATE_PATH, help='The report template to use.')
    parser.add_argument('--generate_report_path', type=Path, help='Specify where to save the report.')

    args = parser.parse_args()

    if not Path(args.template).exists():
        raise FileNotFoundError(f'could not find template at {args.template}.')
    
    if args.generate_report_path is None:
        args.generate_report_path = Path(f'v3-{args.proposal_id}.md')

    return args


def create_report(proposal_id: int, template: Path, generate_report_path: Path):
    pprinter.pprint(f'Generating a report using template in {template}', pprinter.Colors.INFO)
    env = Environment(loader=FileSystemLoader(template.parent))
    env.globals.update(zip=zip)
    template = env.get_template(template.name)
    
    pprinter.pprint(f'Retrieving tag information for proposal {proposal_id}', pprinter.Colors.INFO)
    tags = aave_tags.get_aave_tags(proposal_id)
    pprinter.pprint(f'Tag information retrieved', pprinter.Colors.INFO)

    report = template.render(tags)

    with open(generate_report_path, 'w') as f:
        f.write(report)

    pprinter.pprint(f'Created report at {generate_report_path}.', pprinter.Colors.SUCCESS)


def main():
    args = parse_args()
    create_report(args.proposal_id, args.template, args.generate_report_path)
    

if __name__ == '__main__':
    main()