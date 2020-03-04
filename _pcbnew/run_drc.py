#!/usr/bin/env python
"""Run DRC

This program runs pcbnew and then runs the Distance Rules Check (DRC).
The process is graphical and very delicated.
Exits with the number of errors reported by pcbnew.
"""

__author__   ='Salvador E. Tropea'
__copyright__='Copyright 2019-2020, INTI/Productize SPRL'
__credits__  =['Salvador E. Tropea','Scott Bezek']
__license__  ='Apache 2.0'
__version__  ='1.0.0'
__email__    ='salvador@inti.gob.ar'
__status__   ='beta'

import sys
import os
import logging
import argparse
from xvfbwrapper import Xvfb
import atexit

config_file = ''
old_config_file = ''

# Look for the 'util' module from where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(script_dir))
# Utils import
from util import file_util
from util.ui_automation import (
    PopenContext,
    xdotool,
    wait_for_window,
    recorded_xvfb,
    clipboard_store)

def parse_drc(drc_file):
    from re import search as regex_search

    with open(drc_file, 'r') as f:
        lines = f.read().splitlines()

    drc_errors = None
    unconnected_pads = None

    for line in lines:
        if drc_errors != None and unconnected_pads != None:
            break;
        m = regex_search(
            '^\*\* Found ([0-9]+) DRC errors \*\*$', line)
        if m != None:
            drc_errors = m.group(1);
            continue
        m = regex_search(
            '^\*\* Found ([0-9]+) unconnected pads \*\*$', line)
        if m != None:
            unconnected_pads = m.group(1);
            continue

    return {
        'drc_errors': int(drc_errors),
        'unconnected_pads': int(unconnected_pads)
    }

def dismiss_already_running():
    # The "Confirmation" modal pops up if pcbnew is already running
    try:
        nf_title = 'Confirmation'
        wait_for_window(nf_title, nf_title, 1)

        logger.info('Dismiss pcbnew already running')
        xdotool(['search', '--onlyvisible', '--name', nf_title, 'windowfocus'])
        xdotool(['key', 'Return'])
    except RuntimeError:
        pass

def dismiss_warning():
    try:
        nf_title = 'Warning'
        wait_for_window(nf_title, nf_title, 1)

        logger.error('Dismiss pcbnew warning, will fail')
        xdotool(['search', '--onlyvisible', '--name', nf_title, 'windowfocus'])
        xdotool(['key', 'Return'])
    except RuntimeError:
        pass


def run_drc(pcb_file, output_dir, record=True):

    file_util.mkdir_p(output_dir)

    drc_output_file = os.path.join(os.path.abspath(output_dir), 'drc_result.rpt')
    if os.path.exists(drc_output_file):
        os.remove(drc_output_file)

    xvfb_kwargs = {
	    'width': 800,
	    'height': 600,
	    'colordepth': 24,
    }

    with recorded_xvfb(output_dir, **xvfb_kwargs) if record else Xvfb(**xvfb_kwargs):
        with PopenContext(['pcbnew', pcb_file], close_fds=True) as pcbnew_proc:
            clipboard_store(drc_output_file)

            logger.info('Focus main pcbnew window')
            failed_focuse = False
            try:
               wait_for_window('pcbnew', 'Pcbnew', 5)
            except RuntimeError:
               failed_focuse = True
               pass
            if failed_focuse:
               dismiss_already_running()
               dismiss_warning()
               wait_for_window('pcbnew', 'Pcbnew', 5)

            logger.info('Open Inspect->DRC')
            xdotool(['key', 'alt+i'])
            xdotool(['key', 'd'])

            logger.info('Focus DRC modal window')
            wait_for_window('DRC modal window', 'DRC Control')
            xdotool(['key', 'Tab'])
            xdotool(['key', 'Tab'])
            xdotool(['key', 'Tab'])
            # Refill zones on DRC gets saved in /root/.config/kicad/pcbnew as RefillZonesBeforeDrc
            xdotool(['key', 'Tab'])
            logger.info('Enable reporting all errors for tracks')
            xdotool(['key', 'space'])
            xdotool(['key', 'Tab'])
            xdotool(['key', 'Tab'])
            xdotool(['key', 'Tab'])
            xdotool(['key', 'Tab'])
            logger.info('Pasting output dir')
            xdotool(['key', 'ctrl+v'])
            xdotool(['key', 'Return'])

            wait_for_window('Report completed dialog', 'Disk File Report Completed')
            xdotool(['key', 'Return'])
            pcbnew_proc.terminate()

    return drc_output_file

# Restore the pcbnew configuration
def restore_config():
    if os.path.exists(old_config_file):
       os.remove(config_file)
       os.rename(old_config_file,config_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KiCad automated DRC runner',
                                     epilog='Runs `pcbnew` and the the DRC, the result is stored in drc_result.rpt')

    parser.add_argument('kicad_pcb_file', help='KiCad PCB file')
    parser.add_argument('output_dir', help='Output directory (for drc_result.rpt)')
    parser.add_argument('--ignore_unconnected', '-i', help='Ignore unconnected paths',
                        action='store_true')
    parser.add_argument('--record', help='Record the UI automation',
                        action='store_true')
    parser.add_argument('--verbose','-v',action='count',default=0)
    parser.add_argument('--version','-V',action='version', version='%(prog)s '+__version__+' - '+
                        __copyright__+' - License: '+__license__)

    args = parser.parse_args()

    # Create a logger with the specified verbosity
    if args.verbose>=2:
       log_level=logging.DEBUG
       verb='-vv'
    elif args.verbose==1:
       log_level=logging.INFO
       verb='-v'
    else:
       verb=None
       log_level=logging.WARNING
    logging.basicConfig(level=log_level)
    logger=logging.getLogger(os.path.basename(__file__))

    # Force english + UTF-8
    os.environ['LANG'] = 'C.UTF-8'

    # Back-up the current pcbnew configuration
    config_file = os.environ['HOME'] + '/.config/kicad/pcbnew'
    old_config_file = config_file + '.pre_run_drc'
    os.rename(config_file,old_config_file)
    atexit.register(restore_config)

    # Create a suitable configuration
    text_file = open(config_file,"w")
    text_file.write('canvas_type=2\n')
    text_file.write('RefillZonesBeforeDrc=1\n')
    text_file.write('PcbFrameFirstRunShown=1\n')
    text_file.close()

    drc_result = parse_drc(run_drc(args.kicad_pcb_file, args.output_dir, args.record))

    logger.info(drc_result);
    if drc_result['drc_errors'] == 0 and drc_result['unconnected_pads'] == 0:
        exit(0)
    else:
        logger.error('Found {} DRC errors and {} unconnected pads'.format(
            drc_result['drc_errors'],
            drc_result['unconnected_pads']
        ))
        exit(drc_result['drc_errors']+drc_result['unconnected_pads'])
    
