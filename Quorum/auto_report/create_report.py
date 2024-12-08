from Quorum.auto_report.report_generator import ReportGenerator
from Quorum.auto_report.tags import AaveTags
import Quorum.utils.pretty_printer as pprinter

import argparse
from pathlib import Path


DEFAULT_TEMPLATE_PATH = Path(__file__).parent / 'AaveReportTemplate.md'


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
    with open(args.template) as f:
        template = f.read()
    
    report = ReportGenerator(template, AaveTags(args.proposal_id).tag_mappings).report

    with open((report_path:=f'v3-{args.proposal_id}.md'), 'w') as f:
        f.write(report)

    pprinter.pretty_print(f'Created report at {report_path}.', pprinter.Colors.SUCCESS)


if __name__ == '__main__':
    main()