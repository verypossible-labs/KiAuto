"""
Tests for eeschema_do export

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


def test_export_all_pdf():
    prj = 'good-project'
    pdf = prj+'.pdf'
    ctx = context.TestContext('Export_All_PDF', prj, context.MODE_SCH)
    cmd = [PROG, 'export', '--file_format', 'pdf', '--all_pages']
    ctx.run(cmd)
    ctx.expect_out_file(pdf)
    ctx.compare_pdf(pdf, 'good_sch_all.pdf')
    ctx.clean_up()


def test_export_pdf():
    prj = 'good-project'
    pdf = prj+'.pdf'
    ctx = context.TestContext('Export_All_PDF', prj, context.MODE_SCH)
    cmd = [PROG, 'export', '--file_format', 'pdf']
    ctx.run(cmd)
    ctx.expect_out_file(pdf)
    ctx.compare_image(pdf, 'good_sch_top.pdf')
    ctx.clean_up()


def do_test_svg(ctx, svg):
    ctx.expect_out_file(svg)
    ctx.filter_txt(svg, r"date \d+/\d+/\d+ \d+:\d+:\d+", 'DATE')
    ctx.compare_txt(svg, diff=svg+'.diff')


def test_export_all_svg():
    prj = 'good-project'
    ctx = context.TestContext('Export_All_SVG', prj, context.MODE_SCH)
    cmd = [PROG, 'export', '--file_format', 'svg', '--all_pages']
    ctx.run(cmd)
    do_test_svg(ctx, 'good-project.svg')
    do_test_svg(ctx, 'logic-logic.svg')
    do_test_svg(ctx, 'power-Power.svg')
    ctx.clean_up()


def test_export_svg():
    prj = 'good-project'
    ctx = context.TestContext('Export_SVG', prj, context.MODE_SCH)
    cmd = [PROG, 'export', '--file_format', 'svg']
    ctx.run(cmd)
    do_test_svg(ctx, 'good-project.svg')
    ctx.dont_expect_out_file('logic-logic.svg')
    ctx.dont_expect_out_file('power-Power.svg')
    ctx.clean_up()
