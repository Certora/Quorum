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


def main():
    args = parse_args()

    pprinter.pretty_print(f'Generating a report using template in {args.template}', pprinter.Colors.INFO)
    env = Environment(loader=FileSystemLoader(args.template.parent))
    env.globals.update(zip=zip)
    template = env.get_template(args.template.name)
    
    pprinter.pretty_print(f'Retrieving tag information for proposal {args.proposal_id}', pprinter.Colors.INFO)
    tags = aave_tags.get_aave_tags(args.proposal_id)
    pprinter.pretty_print(f'Tag information retrieved', pprinter.Colors.INFO)

    report = template.render(tags)

    with open((report_path:=f'v3-{args.proposal_id}.md'), 'w') as f:
        f.write(report)

    pprinter.pretty_print(f'Created report at {report_path}.', pprinter.Colors.SUCCESS)


if __name__ == '__main__':
    main()