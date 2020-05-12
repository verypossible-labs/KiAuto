"""
Tests for eeschema_do run_erc

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

PROG = 'eeschema_do'
OUT_ERR_REX = r'(\d+) ERC errors'
OUT_WAR_REX = r'(\d+) ERC warnings'


def test_erc_ok():
    """ 1) Test a project with 0 ERC errors/warnings.
        2) Test the --record option.
        3) Test the case when the .erc report aready exists. """
    prj = 'good-project'
    erc = prj+'.erc'
    ctx = context.TestContextSCH('ERC_Ok', prj)
    # Force removing the .erc
    ctx.create_dummy_out_file(erc)
    cmd = [PROG, '-vv', '--record', 'run_erc']
    ctx.run(cmd)
    ctx.expect_out_file(erc)
    ctx.expect_out_file('run_erc_eeschema_screencast.ogv')
    ctx.clean_up()


def test_erc_fail():
    """ Test a project with 1 ERC error and 2 ERC warnings """
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


def test_erc_ok_eeschema_running():
    """ 1) Test to overwrite the .erc file
        2) Test eeschema already running
        3) Test logger colors on TTYs """
    prj = 'good-project'
    rep = prj+'.erc'
    ctx = context.TestContextSCH('ERC_Ok_eeschema_running', prj)
    # Create a report to force and overwrite
    with open(ctx.get_out_path(rep), 'w') as f:
        f.write('dummy')
    # Run eeschema in parallel to get 'Dismiss eeschema already running'
    with ctx.start_kicad('eeschema'):
        # Enable DEBUG logs
        cmd = [PROG, '-vv', '--wait_start', '5', 'run_erc']
        # Use a TTY to get colors in the DEBUG logs
        ctx.run(cmd, use_a_tty=True)
        ctx.stop_kicad()
    ctx.expect_out_file(rep)
    logging.debug('Checking for colors in DEBUG logs')
    assert ctx.search_err(r"\[36;1mDEBUG:") is not None
    assert ctx.search_err(r"Dismiss eeschema already running") is not None
    ctx.clean_up()
