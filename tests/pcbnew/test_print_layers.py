"""
Tests for 'pcbnew_do export'

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

PROG = 'pcbnew_do'
DEFAULT = 'printed.pdf'
CMD_OUT = 'output.txt'


def test_print_pcb_good_dwg():
    ctx = context.TestContext('Print_Good_with_Dwg', 'good-project')
    pdf = 'good_pcb_with_dwg.pdf'
    cmd = [PROG, 'export', '--output_name', pdf]
    layers = ['F.Cu', 'F.SilkS', 'Dwgs.User', 'Edge.Cuts']
    ctx.run(cmd, extra=layers)
    ctx.expect_out_file(pdf)
    ctx.compare_image(pdf)
    ctx.clean_up()


def test_print_pcb_good_inner():
    ctx = context.TestContext('Print_Good_Inner', 'good-project')
    cmd = [PROG, 'export']
    layers = ['F.Cu', 'F.SilkS', 'GND.Cu', 'Signal1.Cu', 'Signal2.Cu', 'Power.Cu', 'Edge.Cuts']
    ctx.run(cmd, extra=layers)
    ctx.expect_out_file(DEFAULT)
    ctx.compare_image(DEFAULT, 'good_pcb_inners.pdf')
    ctx.clean_up()


def test_print_pcb_layers():
    ctx = context.TestContext('Print_Layers', 'good-project')
    cmd = [PROG, 'export', '--list']
    ctx.run(cmd)
    ctx.compare_txt(CMD_OUT, 'good_pcb_layers.txt')
    ctx.clean_up()


def test_print_pcb_good_dwg_dism():
    ctx = context.TestContext('Print_Good_with_Dwg_Dism', 'good-project')
    pdf = 'good_pcb_with_dwg.pdf'
    # Create the output to force and overwrite
    with open(ctx.get_out_path(pdf), 'w') as f:
        f.write('dummy')
    # Run pcbnew in parallel to get 'Dismiss pcbnew already running'
    with ctx.start_kicad('pcbnew'):
        cmd = [PROG, '-v', '--wait_start', '5', 'export', '--output_name', pdf]
        layers = ['F.Cu', 'F.SilkS', 'Dwgs.User', 'Edge.Cuts']
        ctx.run(cmd, extra=layers)
        ctx.stop_kicad()
    ctx.expect_out_file(pdf)
    ctx.compare_image(pdf)
    assert ctx.search_err(r"Dismiss pcbnew already running") is not None
    ctx.clean_up()
