#!/usr/bin/env python

import os
import time
import re
import shutil
import atexit
# python3-psutil
import psutil

from kicad_auto.misc import (WRONG_ARGUMENTS)
from kicad_auto import log
logger = log.get_logger(__name__)

# Collected errors and unconnecteds (warnings)
errs = []
wrns = []
# Error filters
err_filters = []


def wait_for_file_created_by_process(pid, file, timeout=15):
    process = psutil.Process(pid)

    DELAY = 0.2
    logger.debug('Waiting for file %s', file)
    for i in range(int(timeout/DELAY)):
        open_files = process.open_files()
        logger.debug(open_files)
        if os.path.isfile(file):
            file_open = False
            for open_file in open_files:
                if open_file.path == file:
                    file_open = True
            if file_open:
                logger.debug('Waiting for process to close file')
            else:
                return
        else:
            logger.debug('Waiting for process to create file')
        time.sleep(DELAY)

    raise RuntimeError('Timed out waiting for creation of %s' % file)


def load_filters(file):
    """ Load errors filters """
    if not os.path.isfile(file):
        logger.error("Filter file `{}` doesn't exist".format(file))
        exit(WRONG_ARGUMENTS)
    logger.debug('Loading filter errors')
    with open(file, 'r') as f:
        ln = 1
        fl = 0
        for line in f:
            line = line.rstrip()
            if len(line) > 0 and line[0] != '#':
                m = re.search(r'^(\d+),(.*)$', line)
                if m:
                    err_filters.append([m.group(1), m.group(2)])
                    fl = fl+1
                else:
                    logger.error('Syntax error at line {} in filter file `{}`: `{}`'.format(ln, file, line))
                    logger.error('Use `ERROR_NUMBER,REGEX` format')
                    exit(WRONG_ARGUMENTS)
            ln = ln+1
        logger.info('Loaded {} error filters from `{}`'.format(fl, file))


def apply_filters(err_name, wrn_name):
    """ Apply the error filters to the list of errors and unconnecteds """
    if len(err_filters) == 0:
        return (0, 0)
    c = len(errs)
    skip_err = 0
    for i in range(c):
        err = errs[i]
        for f in err_filters:
            if err.startswith('({})'.format(f[0])):
                m = re.search(f[1], err)
                if m:
                    skip_err = skip_err+1
                    logger.warning('Ignoring '+errs[i])
                    logger.debug('Matched regex `{}`'.format(f[1]))
                    errs[i] = None
                    break
    if skip_err:
        logger.info('Ignoring {} {}'.format(skip_err, err_name))
    c = len(wrns)
    skip_wrn = 0
    for i in range(c):
        wrn = wrns[i]
        for f in err_filters:
            if wrn.startswith('({})'.format(f[0])):
                m = re.search(f[1], wrn)
                if m:
                    skip_wrn = skip_wrn+1
                    logger.info('Ignoring '+wrns[i])
                    logger.debug('Matched regex `{}`'.format(f[1]))
                    wrns[i] = None
                    break
    if skip_wrn:
        logger.info('Ignoring {} {}'.format(skip_wrn, wrn_name))
    return skip_err, skip_wrn


def check_kicad_config_dir(cfg):
    if not os.path.isdir(cfg.kicad_conf_path):
        logger.debug('Creating KiCad config dir')
        os.makedirs(cfg.kicad_conf_path, exist_ok=True)


def check_lib_table(fuser, fsys):
    if not os.path.isfile(fuser):
        logger.debug('Missing default sym-lib-table')
        for f in fsys:
            if os.path.isfile(f):
                shutil.copy2(f, fuser)
                return
        logger.warning('Missing default system symbol table '+fsys[0] +
                       ' KiCad will most probably fail')  # pragma: no cover


def restore_one_config(name, fname, fbkp):
    if fbkp and os.path.exists(fbkp):
        os.remove(fname)
        os.rename(fbkp, fname)
        logger.debug('Restoring old %s config', name)
        return None
    return fbkp


def restore_config(cfg):
    """ Restore original user configuration """
    cfg.conf_eeschema_bkp = restore_one_config('eeschema', cfg.conf_eeschema, cfg.conf_eeschema_bkp)
    cfg.conf_kicad_bkp = restore_one_config('KiCad common', cfg.conf_kicad, cfg.conf_kicad_bkp)
    cfg.conf_hotkeys_bkp = restore_one_config('user hotkeys', cfg.conf_hotkeys, cfg.conf_hotkeys_bkp)
    cfg.conf_pcbnew_bkp = restore_one_config('pcbnew', cfg.conf_pcbnew, cfg.conf_pcbnew_bkp)


def backup_config(name, file, err, cfg):
    config_file = file
    old_config_file = file+'.pre_script'
    logger.debug(name+' config: '+config_file)
    # If we have an old back-up ask for the user to solve it
    if os.path.isfile(old_config_file):
        logger.error(name+' config back-up found (%s)', old_config_file)
        logger.error('It could contain your %s configuration, rename it to %s or discard it.', name.lower(), config_file)
        exit(err)
    if os.path.isfile(config_file):
        logger.debug('Moving current config to '+old_config_file)
        os.rename(config_file, old_config_file)
        atexit.register(restore_config, cfg)
        return old_config_file
    return None
