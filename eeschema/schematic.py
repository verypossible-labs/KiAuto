#!/usr/bin/env python

#   Copyright 2019 Productize SPRL
#   Copyright 2015-2016 Scott Bezek and the splitflap contributors
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

__author__   ='Scott Bezek, Salvador E. Tropea'
__copyright__='Copyright 2015-2020, INTI/Productize SPRL/Scott Bezek'
__credits__  =['Salvador E. Tropea','Scott Bezek']
__license__  ='Apache 2.0'
__email__    ='salvador@inti.gob.ar'
__status__   ='beta'

import logging
import os
import subprocess
import sys
import time
import re
import argparse
import atexit

# Look for the 'util' module from where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(script_dir))
# Utils import
# Log functionality first
from util import log
log.set_domain(os.path.splitext(os.path.basename(__file__))[0])
from util import file_util
from util.misc import (REC_W,REC_H,__version__)
from util.ui_automation import (
    PopenContext,
    xdotool,
    wait_for_window,
    recorded_xvfb,
    clipboard_store,
    clipboard_retrieve
)

def dismiss_library_error():
    # The "Error" modal pops up if libraries required by the schematic have
    # not been found. This can be ignored as all symbols are placed inside the
    # *-cache.lib file:
    # There -should- be a way to disable it, but I haven't the magic to drop in the config file yet
    try:
        nf_title = 'Error'
        wait_for_window(nf_title, nf_title, 3)

        logger.info('Dismiss eeschema library warning modal')
        xdotool(['search', '--onlyvisible', '--name', nf_title, 'windowfocus'])
        xdotool(['key', 'Escape'])
    except RuntimeError:
        pass


def dismiss_library_warning():
    # The "Not Found" window pops up if libraries required by the schematic have
    # not been found. This can be ignored as all symbols are placed inside the
    # *-cache.lib file:
    try:
        nf_title = 'Not Found'
        wait_for_window(nf_title, nf_title, 3)

        logger.info('Dismiss eeschema library warning window')
        xdotool(['search', '--onlyvisible', '--name', nf_title, 'windowfocus'])
        xdotool(['key', 'Return'])
    except RuntimeError:
        pass

def dismiss_newer_version():
    # The "Not Found" window pops up if libraries required by the schematic have
    # not been found. This can be ignored as all symbols are placed inside the
    # *-cache.lib file:
    try:
        logger.info('Dismiss schematic version notification')
        wait_for_window('Newer schematic version notification', 'Info', 3)

        xdotool(['key', 'Return'])
    except RuntimeError:
        pass


def dismiss_remap_helper():
    # The "Remap Symbols" windows pop up if the uses the project symbol library 
    # the older list look up method for loading library symbols.
    # This can be ignored as we're just trying to output data and don't 
    # want to mess with the actual project.
    try:
        logger.info('Dismiss schematic symbol remapping')
        wait_for_window('Remap Symbols', 'Remap', 3)

        xdotool(['key', 'Escape'])
    except RuntimeError:
        pass


def eeschema_skip_errors():
    #dismiss_newer_version()
    #dismiss_remap_helper();
    #dismiss_library_warning()
    #dismiss_library_error()
    return 0

def eeschema_plot_schematic(output_dir, file_format, all_pages):
    if file_format not in ('pdf', 'svg'):
        raise ValueError("file_format should be 'pdf' or 'svg'")

    clipboard_store(output_dir)

    logger.info('Focus main eeschema window')
    wait_for_window('Eeschema', 'Eeschema.*\.sch')

    xdotool(['search', '--onlyvisible', '--name', 'Eeschema.*\.sch', 'windowfocus'])

    logger.info('Open File->pLot')
    xdotool(['key', 'alt+f',
        'l'
    ])

    wait_for_window('plot', 'Plot')

    logger.info('Paste output directory')
    xdotool(['key', 'ctrl+v'])

    logger.info('Move to the "plot" button')

    command_list = ['key',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
        'Tab',
    ]

    if not all_pages:   # all pages is default option
        command_list.extend(['Tab'])
    xdotool(command_list)

    logger.info('Plot')
    xdotool(['key', 'Return'])
    logger.info('Closing window')
    xdotool(['key', 'Escape'])


def eeschema_quit():
    logger.info('Quitting eeschema')
    xdotool(['key', 'Escape', 'Escape', 'Escape'])
    wait_for_window('eeschema', 'Eeschema.*\.sch')
    logger.info('Focus main eeschema window')
    xdotool(['search', '--onlyvisible', '--name', 'Eeschema.*\.sch', 'windowfocus'])
    xdotool(['key', 'Ctrl+q'])

def eeschema_export_schematic(schematic, output_dir, all_pages=False, record=False):
    file_format = file_format.lower()
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(schematic))[0]+'.'+file_format)
    if os.path.exists(output_file):
        logger.debug('Removing old file')
        os.remove(output_file)

    with recorded_xvfb(output_dir if record else None, 'export_eeschema_screencast.ogv', width=args.rec_width, height=args.rec_height, colordepth=24):
        with PopenContext(['eeschema', schematic], close_fds=True, stderr=open(os.devnull, 'wb')) as eeschema_proc:
            eeschema_skip_errors()
            eeschema_plot_schematic(output_dir, file_format, all_pages)
            eeschema_quit()
            eeschema_proc.wait()

    return output_file

def eeschema_parse_erc(erc_file, warning_as_error = False):
    with open(erc_file, 'r') as f:
        lines = f.read().splitlines()
        last_line = lines[-1]
    
    logger.debug('Last line: '+last_line)
    m = re.search('^ \*\* ERC messages: ([0-9]+) +Errors ([0-9]+) +Warnings ([0-9]+)+$', last_line)
    messages = m.group(1)
    errors = m.group(2)
    warnings = m.group(3)

    if warning_as_error:
        return int(errors) + int(warnings)
    return int(errors)

def eeschema_run_erc_schematic(erc_file, pid):

    # Do this now since we have to wait for KiCad anyway
    clipboard_store(erc_file)

    wait_for_window('Main eeschema window', 'Eeschema.*\.sch', 25)

    logger.info('Open Tools->Electrical Rules Checker')
    xdotool(['key', 'alt+i', 'c'])

    wait_for_window('Electrical Rules Checker dialog', 'Electrical Rules Checker')
    xdotool(['key', 'Tab', 'Tab', 'Tab', 'Tab', 'space', 'Return' ])

    wait_for_window('ERC File save dialog', 'ERC File')
    logger.info('Pasting output file')
    xdotool(['key', 'ctrl+v'])
    # KiCad adds .erc unconditionally
    erc_file = erc_file + '.erc'
    if os.path.exists(erc_file):
       os.remove(erc_file)

    logger.info('Run ERC')
    xdotool(['key', 'Return'])

    logger.info('Wait for ERC file creation')
    file_util.wait_for_file_created_by_process(pid, erc_file)

    logger.info('Exit ERC')
    xdotool(['key', 'shift+Tab', 'Return'])

    return erc_file


def eeschema_netlist_commands(output_file, pid):
    logger.info('Focus main eeschema window')
    wait_for_window('eeschema', 'Eeschema.*\.sch')

    logger.info('Open Tools->Generate Netlist File')
    xdotool(['key',
        'alt+t',
        'n'
    ])

    # Do this now since we have to wait for KiCad anyway
    clipboard_store(output_file)

    logger.info('Focus Netlist window')
    wait_for_window('Netlist', 'Netlist')
    xdotool(['key','Tab','Tab','Return'])

    wait_for_window('Netlist File save dialog', 'Save Netlist File')
    logger.info('Pasting output file')
    xdotool(['key', 'ctrl+v'])
    logger.info('Copy full file path')
    xdotool(['key', 'ctrl+a', 'ctrl+c'])

    net_file = clipboard_retrieve()
    if os.path.exists(net_file):
        os.remove(net_file)

    logger.info('Generate Netlist')
    xdotool(['key', 'Return'])

    logger.info('Wait for Netlist file creation')
    file_util.wait_for_file_created_by_process(pid, net_file)

    return net_file


def eeschema_bom_xml_commands(output_file, pid):
    logger.info('Focus main eeschema window')
    wait_for_window('eeschema', 'Eeschema.*\.sch')

    logger.info('Open Tools->Generate Bill of Materials')
    xdotool(['key',
        'alt+t',
        'm'
    ])

    logger.info('Focus BoM window')
    wait_for_window('Bill of Material', 'Bill of Material')
    xdotool(['key','Return'])

    logger.info('Wait for BoM file creation')
    file_util.wait_for_file_created_by_process(pid, output_file)


def eeschema_run_erc(schematic, output_dir, warning_as_error, record=False):
    erc_file = os.path.join(output_dir, os.path.splitext(os.path.basename(schematic))[0])
    with recorded_xvfb(output_dir if record else None, 'run_erc_eeschema_screencast.ogv', width=args.rec_width, height=args.rec_height, colordepth=24):
        with PopenContext(['eeschema', schematic], close_fds=True, stderr=open(os.devnull, 'wb')) as eeschema_proc:
            eeschema_skip_errors()
            erc_file = eeschema_run_erc_schematic(erc_file,eeschema_proc.pid)
            eeschema_proc.terminate()

    return eeschema_parse_erc(erc_file, warning_as_error)

def eeschema_netlist(schematic, output_dir, record=False):
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(schematic))[0])
    with recorded_xvfb(output_dir if record else None, 'netlist_eeschema_screencast.ogv', width=args.rec_width, height=args.rec_height, colordepth=24):
        with PopenContext(['eeschema', schematic], close_fds=True, stderr=open(os.devnull, 'wb')) as eeschema_proc:
            eeschema_skip_errors()
            eeschema_netlist_commands(output_file,eeschema_proc.pid)
            eeschema_quit()
            eeschema_proc.wait()

def eeschema_bom_xml(schematic, output_dir, record=False):
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(schematic))[0]+'.xml')
    with recorded_xvfb(output_dir if record else None, 'bom_xml_eeschema_screencast.ogv', width=args.rec_width, height=args.rec_height, colordepth=24):
        with PopenContext(['eeschema', schematic], close_fds=True, stderr=open(os.devnull, 'wb')) as eeschema_proc:
            eeschema_skip_errors()
            eeschema_bom_xml_commands(output_file,eeschema_proc.pid)
            eeschema_proc.terminate()

# Restore the eeschema configuration
def restore_config():
    if os.path.exists(old_config_file):
       os.remove(config_file)
       os.rename(old_config_file,config_file)
       logger.debug('Restoring old eeschema config')

# Restore the KiCad common configuration
def restore_common_config():
    if os.path.exists(old_common_config_file):
       os.remove(common_config_file)
       os.rename(old_common_config_file,common_config_file)
       logger.debug('Restoring old KiCad common config')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KiCad schematic automation')
    subparsers = parser.add_subparsers(help='Command:', dest='command')

    parser.add_argument('schematic', help='KiCad schematic file')
    parser.add_argument('output_dir', help='Output directory')

    parser.add_argument('--record','-r',help='Record the UI automation',action='store_true')
    parser.add_argument('--rec_width',help='Record width ['+str(REC_W)+']',type=int,default=REC_W)
    parser.add_argument('--rec_height',help='Record height ['+str(REC_H)+']',type=int,default=REC_H)
    parser.add_argument('--verbose','-v',action='count',default=0)
    parser.add_argument('--version','-V',action='version', version='%(prog)s '+__version__+' - '+
                        __copyright__+' - License: '+__license__)

    export_parser = subparsers.add_parser('export', help='Export a schematic')
    export_parser.add_argument('--file_format', '-f', help='Export file format',
        choices=['svg', 'pdf'],default='svg')
    export_parser.add_argument('--all_pages', '-a', help='Plot all schematic pages in one file',
        action='store_true')

    erc_parser = subparsers.add_parser('run_erc', help='Run Electrical Rules Checker on a schematic')
    erc_parser.add_argument('--warnings_as_errors', '-w', help='Treat warnings as errors',
        action='store_true')

    netlist_parser = subparsers.add_parser('netlist', help='Create the netlist')
    bom_xml_parser = subparsers.add_parser('bom_xml', help='Create the BoM in XML format')

    args = parser.parse_args()

    # Create a logger with the specified verbosity
    logger = log.init(args.verbose)

    if not os.path.isfile(args.schematic):
        logger.error(args.schematic+' does not exist')
        exit(-1)

    # Create output dir if it doesn't exist
    output_dir = os.path.abspath(args.output_dir)+'/'
    file_util.mkdir_p(output_dir)

    # Force english + UTF-8
    os.environ['LANG'] = 'C.UTF-8'

    # Back-up the current eeschema configuration
    config_file = os.environ['HOME'] + '/.config/kicad/eeschema'
    old_config_file = config_file + '.pre_script'
    logger.debug('Eeschema config: '+config_file)
    # If we have an old back-up ask for the user to solve it
    if os.path.isfile(old_config_file):
       logger.error('Eeschema config back-up found (%s)',old_config_file)
       logger.error('It could contain your eeschema configuration, rename it to %s or discard it.',config_file)
       exit(-1)
    if os.path.isfile(config_file):
       logger.debug('Moving current config to '+old_config_file)
       os.rename(config_file,old_config_file)
       atexit.register(restore_config)

    # Create a suitable configuration
    logger.debug('Creating an eeschema config')
    text_file = open(config_file,"w")
    text_file.write('RescueNeverShow=1\n')
    try:
        index=['ps','---','dxf','pdf','svg'].index(args.file_format)
        logger.debug('Selecting plot format %s (%d)',args.file_format,index)
    except:
        index=0
    text_file.write('PlotFormat=%d\n' % index)
    text_file.close()

    # Back-up the current kicad_common configuration
    common_config_file = os.environ['HOME'] + '/.config/kicad/kicad_common'
    old_common_config_file = common_config_file + '.pre_script'
    logger.debug('Kicad common config: '+common_config_file)
    # If we have an old back-up ask for the user to solve it
    if os.path.isfile(old_common_config_file):
       logger.error('KiCad common config back-up found (%s)',old_common_config_file)
       logger.error('It could contain your kiCad configuration, rename it to %s or discard it.',common_config_file)
       exit(-1)
    if os.path.isfile(common_config_file):
       logger.debug('Moving current config to '+old_common_config_file)
       os.rename(common_config_file,old_common_config_file)
       atexit.register(restore_common_config)

    # Create a suitable configuration
    logger.debug('Creating a KiCad common config')
    text_file = open(common_config_file,"w")
    text_file.write('ShowEnvVarWarningDialog=0\n')
    text_file.write('Editor=/bin/cat\n')
    text_file.close()

    if args.command == 'export':
        eeschema_export_schematic(args.schematic, output_dir, args.all_pages, args.record)
    elif args.command == 'netlist':
        eeschema_netlist(args.schematic, output_dir, args.record)
    elif args.command == 'bom_xml':
        eeschema_bom_xml(args.schematic, output_dir, args.record)
    elif args.command == 'run_erc':
        errors = eeschema_run_erc(args.schematic, output_dir, args.warnings_as_errors, args.record)
        if errors > 0:
            logger.error('{} ERC errors detected'.format(errors))
            exit(errors)
        logger.info('No errors');
    exit(0)
