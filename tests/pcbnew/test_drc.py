"""
Tests for pcbnew_run_drc

For debug information use:
pytest-3 --log-cli-level debug

"""

import os
import sys
# import re
# import logging
# Look for the 'utils' module from where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(script_dir))
# Utils import
from utils import context

PROG = 'pcbnew_run_drc'
REPORT = 'drc_result.rpt'
OUT_REX = r'(\d+) DRC errors and (\d+) unconnected pads'


def test_drc_ok(test_dir):
    ctx = context.TestContext('DRC_Ok', 'good-project', test_dir)
    cmd = [PROG]
    ctx.run(cmd)
    ctx.expect_out_file(REPORT)
    ctx.clean_up()


def test_drc_fail(test_dir):
    ctx = context.TestContext('DRC_Error', 'fail-project', test_dir)
    cmd = [PROG]
    ctx.run(cmd, 254)
    ctx.expect_out_file(REPORT)
    m = ctx.search_err(OUT_REX)
    assert m is not None
    assert m.group(1) == '1'
    assert m.group(2) == '1'
    ctx.clean_up()


def test_drc_unco(test_dir):
    ctx = context.TestContext('DRC_Unconnected', 'warning-project', test_dir)
    cmd = [PROG, '--output_name', 'drc.txt']
    ctx.run(cmd, 255)
    ctx.expect_out_file('drc.txt')
    m = ctx.search_err(OUT_REX)
    assert m is not None
    assert m.group(1) == '0'
    assert m.group(2) == '1'
    ctx.clean_up()


def test_drc_unco_ok(test_dir):
    ctx = context.TestContext('DRC_Unconnected_Ok', 'warning-project', test_dir)
    cmd = [PROG, '--output_name', 'drc.txt', '--ignore_unconnected']
    ctx.run(cmd)
    ctx.expect_out_file('drc.txt')
    m = ctx.search_err(OUT_REX)
    assert m is not None
    assert m.group(1) == '0'
    assert m.group(2) == '1'
    ctx.clean_up()
