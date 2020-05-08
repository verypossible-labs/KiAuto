"""
Tests for eeschema_do miscellaneous stuff

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
from kicad_auto.misc import (EESCHEMA_CFG_PRESENT, KICAD_CFG_PRESENT)

PROG = 'eeschema_do'


def test_eeschema_config_backup():
    """ Here we test the extreme situation that a previous run left a config
        back-up and the user must take action. """
    prj = 'good-project'
    ctx = context.TestContextSCH('Eeschema_config_bkp', prj)

    # Create a fake back-up
    kicad_cfg_dir = os.path.join(os.environ['HOME'], '.config/kicad')
    if not os.path.isdir(kicad_cfg_dir):
        logging.debug('Creating KiCad config dir')
        os.makedirs(kicad_cfg_dir, exist_ok=True)
    config_file = os.path.join(kicad_cfg_dir, 'eeschema')
    old_config_file = config_file + '.pre_script'
    logging.debug('Eeschema old config: '+old_config_file)
    with open(old_config_file, 'w') as f:
        f.write('Dummy back-up\n')

    # Run the command
    cmd = [PROG, 'run_erc']
    ctx.run(cmd, EESCHEMA_CFG_PRESENT)
    os.remove(old_config_file)
    m = ctx.search_err('Eeschema config back-up found')
    assert m is not None
    ctx.clean_up()


def test_kicad_common_config_backup():
    """ Here we test the extreme situation that a previous run left a config
        back-up and the user must take action. """
    prj = 'good-project'
    ctx = context.TestContextSCH('Eeschema_common_config_bkp', prj)

    # Create a fake back-up
    kicad_cfg_dir = os.path.join(os.environ['HOME'], '.config/kicad')
    if not os.path.isdir(kicad_cfg_dir):
        logging.debug('Creating KiCad config dir')
        os.makedirs(kicad_cfg_dir, exist_ok=True)
    config_file = os.path.join(kicad_cfg_dir, 'kicad_common')
    old_config_file = config_file + '.pre_script'
    logging.debug('KiCad common old config: '+old_config_file)
    with open(old_config_file, 'w') as f:
        f.write('Dummy back-up\n')

    # Run the command
    cmd = [PROG, 'run_erc']
    ctx.run(cmd, KICAD_CFG_PRESENT)
    os.remove(old_config_file)
    m = ctx.search_err('KiCad common config back-up found')
    assert m is not None
    ctx.clean_up()
