import pytest

import Quorum.tests.conftest as conftest

import Quorum.entry_points.create_report as create_report

from pathlib import Path


EXPECTED_DIR = conftest.EXPECTED_DIR / 'test_auto_report'


def test_auto_report():
    with open(EXPECTED_DIR / 'v3-132.md') as f:
        expected = f.read()
    
    create_report.create_report(132, create_report.DEFAULT_TEMPLATE_PATH)
    with open(Path('v3-132.md')) as f:
        actual = f.read()
    
    assert expected == actual

    Path('v3-132.md').unlink()