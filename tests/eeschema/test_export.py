"""
Tests for eeschema_do export

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


def test_export_all_pdf():
    prj = 'good-project'
    pdf = prj+'.pdf'
    ctx = context.TestContextSCH('Export_All_PDF', prj)
    cmd = [PROG, 'export', '--file_format', 'pdf', '--all_pages']
    ctx.run(cmd)
    ctx.expect_out_file(pdf)
    ctx.compare_pdf(pdf, 'good_sch_all.pdf')
    ctx.clean_up()


def test_export_pdf():
    prj = 'good-project'
    pdf = prj+'.pdf'
    ctx = context.TestContextSCH('Export_PDF', prj)
    mtime = ctx.get_pro_mtime()
    cmd = [PROG, 'export', '--file_format', 'pdf']
    ctx.run(cmd)
    ctx.expect_out_file(pdf)
    ctx.compare_image(pdf, 'good_sch_top.pdf')
    # Check the .pro wasn't altered
    logging.debug("Checking .pro wasn't altered")
    assert mtime == ctx.get_pro_mtime()
    ctx.clean_up()


def test_export_all_svg():
    """ 1) Test multiple SVG export.
        2) One of the outputs already exists. """
    prj = 'good-project'
    ctx = context.TestContextSCH('Export_All_SVG', prj)
    cmd = [PROG, 'export', '--file_format', 'svg', '--all_pages']
    if ctx.kicad_version < context.KICAD_VERSION_5_99:
        logic = 'logic-logic.svg'
        power = 'power-Power.svg'
    else:
        logic = prj+'-logic.svg'
        power = prj+'-Power.svg'
    ctx.create_dummy_out_file(logic)
    ctx.run(cmd)
    ctx.compare_svg('good-project.svg')
    ctx.compare_svg(logic)
    ctx.compare_svg(power)
    ctx.clean_up()


def test_export_svg():
    """ 1) Test single SVG export.
        2) Output already exists. """
    prj = 'good-project'
    svg = prj+'.svg'
    ctx = context.TestContextSCH('Export_SVG', prj)
    ctx.create_dummy_out_file(svg)
    cmd = [PROG, 'export', '--file_format', 'svg']
    ctx.run(cmd)
    ctx.compare_svg(svg)
    ctx.dont_expect_out_file('logic-logic.svg')
    ctx.dont_expect_out_file('power-Power.svg')
    ctx.clean_up()


def test_export_ps():
    prj = 'good-project'
    ps = prj+'.ps'
    ctx = context.TestContextSCH('Export_PS', prj)
    cmd = [PROG, 'export', '--file_format', 'ps']
    ctx.run(cmd)
    ctx.compare_ps(ps)
    ctx.dont_expect_out_file('logic-logic.ps')
    ctx.dont_expect_out_file('power-Power.ps')
    ctx.clean_up()


def test_export_all_ps():
    prj = 'good-project'
    ps = prj+'.ps'
    ctx = context.TestContextSCH('Export_All_PS', prj)
    cmd = [PROG, 'export', '--file_format', 'ps', '--all_pages']
    ctx.run(cmd)
    ctx.compare_ps(ps)
    ctx.compare_ps('logic-logic.ps')
    ctx.compare_ps('power-Power.ps')
    ctx.clean_up()


def test_export_dxf():
    prj = 'good-project'
    dxf = prj+'.dxf'
    ctx = context.TestContextSCH('Export_DXF', prj)
    cmd = [PROG, 'export', '--file_format', 'dxf']
    ctx.run(cmd)
    ctx.expect_out_file(dxf)
    ctx.dont_expect_out_file('logic-logic.dxf')
    ctx.dont_expect_out_file('power-Power.dxf')
    ctx.clean_up()


def test_export_all_dxf():
    prj = 'good-project'
    dxf = prj+'.dxf'
    ctx = context.TestContextSCH('Export_All_DXF', prj)
    cmd = [PROG, 'export', '--file_format', 'dxf', '--all_pages']
    ctx.run(cmd)
    ctx.expect_out_file(dxf)
    ctx.expect_out_file('logic-logic.dxf')
    ctx.expect_out_file('power-Power.dxf')
    ctx.clean_up()


def test_export_hpgl():
    prj = 'good-project'
    hpgl = prj+'.plt'
    ctx = context.TestContextSCH('Export_HPGL', prj)
    cmd = [PROG, 'export', '--file_format', 'hpgl']
    ctx.run(cmd)
    ctx.expect_out_file(hpgl)
    ctx.dont_expect_out_file('logic-logic.plt')
    ctx.dont_expect_out_file('power-Power.plt')
    ctx.clean_up()


def test_export_all_hpgl():
    prj = 'good-project'
    hpgl = prj+'.plt'
    ctx = context.TestContextSCH('Export_All_HPGL', prj)
    cmd = [PROG, 'export', '--file_format', 'hpgl', '--all_pages']
    ctx.run(cmd)
    ctx.expect_out_file(hpgl)
    ctx.expect_out_file('logic-logic.plt')
    ctx.expect_out_file('power-Power.plt')
    ctx.clean_up()
