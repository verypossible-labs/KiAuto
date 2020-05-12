"""
Tests for 'pcbnew_do run_drc'

For debug information use:
pytest-3 --log-cli-level debug

"""

import os
import sys
import logging
# Look for the 'utils' module from where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(script_dir))
# Utils import
from utils import context

PROG = 'pcbnew_do'
REPORT = 'drc_result.rpt'
OUT_REX = r'(\d+) DRC errors and (\d+) unconnected pads'


def test_drc_ok_1():
    ctx = context.TestContext('DRC_Ok', 'good-project')
    cmd = [PROG, '-vv', 'run_drc']
    ctx.run(cmd)
    ctx.expect_out_file(REPORT)
    ctx.clean_up()


def test_drc_fail():
    ctx = context.TestContext('DRC_Error', 'fail-project')
    # Here we use -v to cover "info" log level
    cmd = [PROG, '-v', 'run_drc']
    ctx.run(cmd, 254)
    ctx.expect_out_file(REPORT)
    m = ctx.search_err(OUT_REX)
    assert m is not None
    assert m.group(1) == '1'
    assert m.group(2) == '1'
    ctx.clean_up()


def test_drc_unco():
    ctx = context.TestContext('DRC_Unconnected', 'warning-project')
    cmd = [PROG, 'run_drc', '--output_name', 'drc.txt']
    ctx.run(cmd, 255)
    ctx.expect_out_file('drc.txt')
    m = ctx.search_err(OUT_REX)
    assert m is not None
    assert m.group(1) == '0'
    assert m.group(2) == '1'
    ctx.clean_up()


def test_drc_unco_ok():
    ctx = context.TestContext('DRC_Unconnected_Ok', 'warning-project')
    cmd = [PROG, 'run_drc', '--output_name', 'drc.txt', '--ignore_unconnected']
    ctx.run(cmd)
    ctx.expect_out_file('drc.txt')
    m = ctx.search_err(OUT_REX)
    assert m is not None
    assert m.group(1) == '0'
    assert m.group(2) == '1'
    ctx.clean_up()


def test_drc_ok_pcbnew_running():
    """ 1) Test to overwrite the .erc file
        2) Test pcbnew already running
        3) Test logger colors on TTYs """
    ctx = context.TestContext('DRC_Ok_pcbnew_running', 'good-project')
    # Create a report to force and overwrite
    with open(ctx.get_out_path(REPORT), 'w') as f:
        f.write('dummy')
    # Run pcbnew in parallel to get 'Dismiss pcbnew already running'
    with ctx.start_kicad('pcbnew'):
        # Enable DEBUG logs
        cmd = [PROG, '-vv', '--wait_start', '5', 'run_drc']
        # Use a TTY to get colors in the DEBUG logs
        ctx.run(cmd, use_a_tty=True)
        ctx.stop_kicad()
    ctx.expect_out_file(REPORT)
    logging.debug('Checking for colors in DEBUG logs')
    assert ctx.search_err(r"\[36;1mDEBUG:") is not None
    assert ctx.search_err(r"Dismiss pcbnew already running") is not None
    ctx.clean_up()
