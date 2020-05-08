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


def do_test_svg(ctx, svg):
    ctx.expect_out_file(svg)
    ctx.filter_txt(svg, r"date \d+/\d+/\d+ \d+:\d+:\d+", 'DATE')
    ctx.compare_txt(svg, diff=svg+'.diff')


def test_export_all_svg():
    prj = 'good-project'
    ctx = context.TestContextSCH('Export_All_SVG', prj)
    cmd = [PROG, 'export', '--file_format', 'svg', '--all_pages']
    ctx.run(cmd)
    do_test_svg(ctx, 'good-project.svg')
    do_test_svg(ctx, 'logic-logic.svg')
    do_test_svg(ctx, 'power-Power.svg')
    ctx.clean_up()


def test_export_svg():
    prj = 'good-project'
    ctx = context.TestContextSCH('Export_SVG', prj)
    cmd = [PROG, 'export', '--file_format', 'svg']
    ctx.run(cmd)
    do_test_svg(ctx, 'good-project.svg')
    ctx.dont_expect_out_file('logic-logic.svg')
    ctx.dont_expect_out_file('power-Power.svg')
    ctx.clean_up()


def do_test_ps(ctx, ps):
    ctx.expect_out_file(ps)
    ctx.filter_txt(ps, r"%%CreationDate: .*", '%%CreationDate: DATE')
    ctx.filter_txt(ps, r"%%Title: .*", '%%Title: TITLE')
    ctx.compare_txt(ps, diff=ps+'.diff')


def test_export_ps():
    prj = 'good-project'
    ps = prj+'.ps'
    ctx = context.TestContextSCH('Export_PS', prj)
    cmd = [PROG, 'export', '--file_format', 'ps']
    ctx.run(cmd)
    do_test_ps(ctx, ps)
    ctx.dont_expect_out_file('logic-logic.ps')
    ctx.dont_expect_out_file('power-Power.ps')
    ctx.clean_up()


def test_export_all_ps():
    prj = 'good-project'
    ps = prj+'.ps'
    ctx = context.TestContextSCH('Export_All_PS', prj)
    cmd = [PROG, 'export', '--file_format', 'ps', '--all_pages']
    ctx.run(cmd)
    do_test_ps(ctx, ps)
    do_test_ps(ctx, 'logic-logic.ps')
    do_test_ps(ctx, 'power-Power.ps')
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
