#!/usr/bin/env python
#
#   UI automation script to run DRC on a KiCad PCBNew layout
#   Sadly it is not possible to run DRC with the PCBNew Python API since the
#   code is to tied in to the UI. Might change in the future.
#
#   Copyright 2019 Productize SPRL
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys
import os
import logging
import argparse
from xvfbwrapper import Xvfb
import atexit
import time
import re

import subprocess
import gettext

config_file = ''
old_config_file = ''

pcbnew_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(pcbnew_dir)

sys.path.append(repo_root)

from util import file_util
from util.ui_automation import (
    PopenContext,
    xdotool,
    wait_focused,
    wait_not_focused,
    wait_for_window,
    recorded_xvfb,
    clipboard_store
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

def dismiss_pcbNew_Error():
    try:
        nf_title = 'pcbnew Error'
        wait_for_window(nf_title, nf_title, 3)

        logger.error('Dismiss pcbnew error')
        xdotool(['search', '--onlyvisible', '--name', nf_title, 'windowfocus'])
        logger.error('Found, sending Return')
        xdotool(['key', 'Return'])
    except RuntimeError:
        pass

def print_layers(pcb_file, output_dir, record=True):

    file_util.mkdir_p(output_dir)

    print_output_file = os.path.join(os.path.abspath(output_dir), 'printed.pdf')
    if os.path.exists(print_output_file):
        os.remove(print_output_file)

    xvfb_kwargs = { 'width': 1024, 'height': 1080, 'colordepth': 24, }

    with recorded_xvfb(output_dir, 'print_layers_pcbnew_screencast.ogv', **xvfb_kwargs) if record else Xvfb(**xvfb_kwargs):
        with PopenContext(['pcbnew', pcb_file], close_fds=True) as pcbnew_proc:
            clipboard_store(print_output_file)

            #dismiss_pcbNew_Error()

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

            logger.info('Open File->Print')
            xdotool(['key', 'alt+f'])
            xdotool(['key', 'p'])

            logger.info('Focus Print modal window')
            id=wait_for_window('Print modal window', 'Print')
            # The color option is selected (not with a WM)
            xdotool(['key', 'Tab',  'Tab',  'Tab',  'Tab',  'Tab',  'Tab',  'Tab',  'Tab', 'Return'])

            logger.info('Focus 2nd Print modal window (skip=%s)',id[0])
            id2 = wait_for_window('Printer modal window', '^(Print|%s)$' % print_dlg_name, skip_id=id[0])
            # List of printers
            xdotool(['key', 'Tab'])
            # Go up to the top
            xdotool(['key', 'Home'])
            # Output file name
            xdotool(['key', 'Tab'])
            # Open dialog
            xdotool(['key', 'Return'])
            id_sel_f = wait_for_window('Select a filename', '(Select a filename|%s)' % select_a_filename, 2)
            # Select all
            xdotool(['key', 'ctrl+a'])
            logger.info('Pasting output dir')
            xdotool(['key', 'ctrl+v'])
            # Select this name
            xdotool(['key', 'Return'])
            # Back to print
            wait_not_focused(id_sel_f[0])
            logger.info('Focus 2nd Print modal window (skip=%s)',id[0])
            wait_for_window('Printer modal window', '^(Print|%s)$' % print_dlg_name, skip_id=id[0])
            # Format options
            xdotool(['key', 'Tab'])
            # Be sure we are at left (PDF)
            xdotool(['key', 'Left','Left','Left' ])
            # Print it
            xdotool(['key', 'Return'])

            file_util.wait_for_file_created_by_process(pcbnew_proc.pid, print_output_file)

            wait_not_focused(id2[1])
            logger.info('Focus Print modal window')
            id=wait_for_window('Print modal window', 'Print')
            # Close button
            xdotool(['key', 'Tab',  'Tab',  'Tab',  'Tab',  'Tab',  'Tab',  'Tab',  'Tab', 'Tab', 'Tab', 'Return'])

            wait_not_focused(id2[0])
            wait_for_window('pcbnew', 'Pcbnew')
            pcbnew_proc.terminate()

    return print_output_file

# Restore the pcbnew configuration
def restore_config():
    if os.path.exists(old_config_file):
       os.remove(config_file)
       os.rename(old_config_file,config_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KiCad automated PCB printer')

    parser.add_argument('kicad_pcb_file', help='KiCad schematic file')
    parser.add_argument('output_dir', help='Output directory')
    parser.add_argument('layers', nargs='+', help='Which layers to include')
    parser.add_argument('--record', help='Record the UI automation',action='store_true')

    args = parser.parse_args()

    gettext.textdomain('gtk30')
    select_a_filename=gettext.gettext('Select a filename')
    print_dlg_name=gettext.gettext('Print')
    logger.debug('Select a filename -> '+select_a_filename)
    logger.debug('Print -> '+print_dlg_name)

    #cmd=['gettext','gtk30','Select a filename']
#     cmd='gettext gtk30 "Select a filename"'
#     logger.debug(cmd)
#     p=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
#     (output, err)=p.communicate()
#     p_status=p.wait()
#     logger.debug(output)
#     sys.exit(0)

    # Force english + UTF-8
    os.environ['LANG'] = 'C.UTF-8'

    # Read the layer names from the PCB
    layer_names=['-']*50
    pcb_file = open(args.kicad_pcb_file,"r")
    collect_layers=False
    for line in pcb_file:
        if collect_layers:
           z=re.match('\s+\((\d+)\s+(\S+)',line)
           if z:
              res=z.groups()
              #print(res[1]+'->'+res[0])
              layer_names[int(res[0])]=res[1]
           else:
              if re.search('^\s+\)$',line):
                 collect_layers=False
                 break
        else:
           if re.search('\s+\(layers',line):
              collect_layers=True
    pcb_file.close()

    # Back-up the current pcbnew documentation
    config_file = os.environ['HOME'] + '/.config/kicad/pcbnew'
    old_config_file = config_file + '.pre_print_layers'
    os.rename(config_file,old_config_file)
    atexit.register(restore_config)

    # Create a suitable configuration
    text_file = open(config_file,"w")
    text_file.write('canvas_type=2\n')
    text_file.write('RefillZonesBeforeDrc=1\n')
    text_file.write('PcbFrameFirstRunShown=1\n')
    # Color
    text_file.write('PrintMonochrome=0\n')
    # Include frame
    text_file.write('PrintPageFrame=1\n')
    # Real drill marks
    text_file.write('PrintPadsDrillOpt=2\n')
    # Only one file
    text_file.write('PrintSinglePage=1\n')
    # Mark which layers are requested
    used_layers=[0]*50
    for layer in args.layers:
        try:
            used_layers[layer_names.index(layer)]=1
        except:
            print('Unknown layer %s' % layer)
    # List all posible layers, indicating which ones are requested
    for x in range(0,50):
        text_file.write('PlotLayer_%d=%d\n' % (x,used_layers[x]))
    text_file.close()

    print_layers(args.kicad_pcb_file, args.output_dir, args.record)

    
