import pytest
import argparse

import Quorum.tests.conftest as conftest

import Quorum.entry_points.implementations.create_report as create_report

from pathlib import Path


EXPECTED_DIR = conftest.EXPECTED_DIR / 'test_auto_report'


def test_auto_report():
    with open(EXPECTED_DIR / 'v3-132.md') as f:
        expected = f.read()

    args = argparse.Namespace(
        proposal_id=132,
        template=Path('Quorum') / 'auto_report' / 'AaveReportTemplate.md.j2',
        generate_report_path=None
    )
    
    create_report.run_create_report(args)
    with open(Path('v3-132.md')) as f:
        actual = f.read()
    
    assert expected == actual

    Path('v3-132.md').unlink()