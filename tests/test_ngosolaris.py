#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ngosolaris` package."""
from click.testing import CliRunner

from ngosolaris.cli import cli

# PROTECTED REGION ID(ngosolaris.tests.test_ngosolaris) ENABLED START

def test_ngosolaris():
    # from ngosolaris import ngosolaris
    # assert ngosolaris


    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.output == 'Hello World!\n'
    assert result.exit_code == 0


if __name__ == '__main__':
    # to run test file standalone
    test_ngosolaris()

# PROTECTED REGION END
