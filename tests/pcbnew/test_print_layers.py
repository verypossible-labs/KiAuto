"""
Tests for 'pcbnew_do export'

For debug information use:
pytest-3 --log-cli-level debug

"""

import os
import sys
import logging
# Look for the 'utils' module from where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))
prev_dir = os.path.dirname(script_dir)
sys.path.insert(0, prev_dir)
# Utils import
from utils import context
sys.path.insert(0, os.path.dirname(prev_dir))
from kicad_auto.misc import (WRONG_LAYER_NAME, Config)


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
    layers = ['F.Cu', 'F.SilkS', 'GND.Cu', 'Signal1.Cu', 'Inner.3', 'Power.Cu', 'Edge.Cuts']
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
    cfg = Config(logging)
    # Run pcbnew in parallel to get 'Dismiss pcbnew already running'
    with ctx.start_kicad(cfg.pcbnew, cfg):
        cmd = [PROG, '-v', '--wait_start', '5', 'export', '--output_name', pdf]
        layers = ['F.Cu', 'F.SilkS', 'Dwgs.User', 'Edge.Cuts']
        ctx.run(cmd, extra=layers)
        ctx.stop_kicad()
    ctx.expect_out_file(pdf)
    ctx.compare_image(pdf)
    assert ctx.search_err(r"Dismiss pcbnew already running") is not None
    ctx.clean_up()


def test_wrong_layer_name_kiplot():
    ctx = context.TestContext('Wrong_Inner', 'good-project')
    cmd = [PROG, 'export']
    layers = ['F.Cu', 'Inner_1']
    ctx.run(cmd, WRONG_LAYER_NAME, extra=layers)
    m = ctx.search_err(r'Malformed inner layer name')
    assert m is not None
    ctx.clean_up()


def test_wrong_layer_big():
    ctx = context.TestContext('Wrong_Inner_Big', 'good-project')
    cmd = [PROG, 'export']
    layers = ['F.Cu', 'Inner.8']
    ctx.run(cmd, WRONG_LAYER_NAME, extra=layers)
    m = ctx.search_err(r"Inner.8 isn't a valid layer")
    assert m is not None
    ctx.clean_up()


def test_wrong_layer_bogus():
    ctx = context.TestContext('Wrong_Inner_Name', 'good-project')
    cmd = [PROG, 'export']
    layers = ['F.Cu', 'GND_Cu']
    ctx.run(cmd, WRONG_LAYER_NAME, extra=layers)
    m = ctx.search_err(r"Unknown layer GND_Cu")
    assert m is not None
    ctx.clean_up()


def test_print_pcb_good_wm():
    """ Here we test the window manager """
    ctx = context.TestContext('Print_Good_with_WM', 'good-project')
    pdf = 'good_pcb_with_dwg.pdf'
    cmd = [PROG, '-ms', 'export', '--output_name', pdf]
    layers = ['F.Cu', 'F.SilkS', 'Dwgs.User', 'Edge.Cuts']
    ctx.run(cmd, extra=layers)
    ctx.expect_out_file(pdf)
    ctx.compare_image(pdf)
    ctx.clean_up()


def test_print_pcb_refill():
    ctx = context.TestContext('Print_Refill', 'zone-refill')
    pdf = 'zone-refill.pdf'
    cmd = [PROG, 'export', '-f', '--output_name', pdf]
    layers = ['F.Cu', 'B.Cu', 'Edge.Cuts']
    ctx.run(cmd, extra=layers)
    ctx.expect_out_file(pdf)
    ctx.compare_image(pdf)
    ctx.clean_up()
