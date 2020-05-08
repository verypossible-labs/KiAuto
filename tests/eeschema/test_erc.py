"""
Tests for eeschema_do run_erc

For debug information use:
pytest-3 --log-cli-level debug

"""

import os
import sys
# Look for the 'utils' module from where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(script_dir))
# Utils import
from utils import context

PROG = 'eeschema_do'
OUT_ERR_REX = r'(\d+) ERC errors'
OUT_WAR_REX = r'(\d+) ERC warnings'


def test_erc_ok():
    prj = 'good-project'
    ctx = context.TestContextSCH('ERC_Ok', prj)
    cmd = [PROG, '-vv', '--record', 'run_erc']
    ctx.run(cmd)
    ctx.expect_out_file(prj+'.erc')
    ctx.expect_out_file('run_erc_eeschema_screencast.ogv')
    ctx.clean_up()


def test_erc_fail():
    prj = 'fail-project'
    ctx = context.TestContextSCH('ERC_Error', prj)
    cmd = [PROG, 'run_erc']
    ctx.run(cmd, 255)
    ctx.expect_out_file(prj+'.erc')
    m = ctx.search_err(OUT_ERR_REX)
    assert m is not None
    assert m.group(1) == '1'
    m = ctx.search_err(OUT_WAR_REX)
    assert m is not None
    assert m.group(1) == '2'
    ctx.clean_up()


def test_erc_warning():
    prj = 'warning-project'
    ctx = context.TestContextSCH('ERC_Warning', prj)
    cmd = [PROG, 'run_erc']
    ctx.run(cmd, 0)
    ctx.expect_out_file(prj+'.erc')
    m = ctx.search_err(OUT_WAR_REX)
    assert m is not None
    assert m.group(1) == '1'
    ctx.clean_up()


def test_erc_warning_fail():
    prj = 'warning-project'
    ctx = context.TestContextSCH('ERC_Warning_as_Error', prj)
    cmd = [PROG, 'run_erc', '--warnings_as_errors']
    ctx.run(cmd, 255)
    ctx.expect_out_file(prj+'.erc')
    m = ctx.search_err(OUT_ERR_REX)
    assert m is not None
    assert m.group(1) == '1'
    ctx.clean_up()
