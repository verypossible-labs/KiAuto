#!/usr/bin/env python

import os
import time
import re
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
                    wrns[i] = None
                    break
    if skip_wrn:
        logger.info('Ignoring {} {}'.format(skip_wrn, wrn_name))
    return skip_err, skip_wrn
