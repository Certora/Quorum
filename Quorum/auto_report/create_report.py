from Quorum.auto_report.report_generator import ReportGenerator
from Quorum.auto_report.tags import AaveTags

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

    with open(args.template) as f:
        template = f.read()
    
    report = ReportGenerator(template, AaveTags(args.proposal_id).tag_mappings).report

    with open(f'v3-{args.proposal_id}-<title>.md', 'w') as f:
        f.write(report)


if __name__ == '__main__':
    main()