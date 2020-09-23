# -*- coding: utf-8 -*-
# Copyright (c) 2020 Salvador E. Tropea
# Copyright (c) 2020 Instituto Nacional de Tecnologïa Industrial
# License: Apache 2.0
# Project: KiAuto (formerly kicad-automation-scripts)
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
    """ 1) Test netlist creation.
        2) Output file already exists. """
    prj = 'good-project'
    net = prj+'.net'
    ctx = context.TestContextSCH('Netlist', prj)
    # Force removing the .net
    ctx.create_dummy_out_file(net)
    cmd = [PROG, 'netlist']
    ctx.run(cmd)
    ctx.expect_out_file(net)
    ctx.search_in_file(net, [r'\(node \(ref "?R1"?\) \(pin "?1"?\)( \(pinfunction "1"\))?\)',
                             r'\(node \(ref "?R1"?\) \(pin "?2"?\)( \(pinfunction "2"\))?\)',
                             r'\(export \(version "?D"?\)'])
    ctx.clean_up()
