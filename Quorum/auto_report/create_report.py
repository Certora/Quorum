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

    args = parser.parse_args()

    if not Path(args.template).exists():
        raise FileNotFoundError(f'could not find template at {args.template}.')

    return parser.parse_args()


def create_report(proposal_id: int, template: Path):
    pprinter.pretty_print(f'Generating a report using template in {template}', pprinter.Colors.INFO)
    env = Environment(loader=FileSystemLoader(template.parent))
    env.globals.update(zip=zip)
    template = env.get_template(template.name)
    
    pprinter.pretty_print(f'Retrieving tag information for proposal {proposal_id}', pprinter.Colors.INFO)
    tags = aave_tags.get_aave_tags(proposal_id)
    pprinter.pretty_print(f'Tag information retrieved', pprinter.Colors.INFO)

    report = template.render(tags)

    with open((report_path:=f'v3-{proposal_id}.md'), 'w') as f:
        f.write(report)

    pprinter.pretty_print(f'Created report at {report_path}.', pprinter.Colors.SUCCESS)


def main():
    args = parse_args()
    create_report(args.proposal_id, args.template)
    

if __name__ == '__main__':
    main()