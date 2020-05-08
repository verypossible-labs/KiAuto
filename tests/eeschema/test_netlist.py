"""
Tests for eeschema_do netlist

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


def test_netlist():
    prj = 'good-project'
    net = prj+'.net'
    ctx = context.TestContextSCH('Netlist', prj)
    cmd = [PROG, 'netlist']
    ctx.run(cmd)
    ctx.expect_out_file(net)
    ctx.search_in_file(net, [r'\(node \(ref R1\) \(pin 1\)\)',
                             r'\(node \(ref R1\) \(pin 2\)\)',
                             r'\(export \(version D\)'])
    ctx.clean_up()
