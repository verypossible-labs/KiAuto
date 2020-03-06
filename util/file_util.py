#!/usr/bin/env python

import errno
import os
import logging
import time
# python3-psutil
import psutil

from util import log
logger = log.get_logger(__name__)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def wait_for_file_created_by_process(pid, file, timeout=5):
    process = psutil.Process(pid)

    DELAY = 0.5
    for i in range(int(timeout/DELAY)):
        if os.path.isfile(file):
            if file in process.open_files():
                logger.debug('Waiting for process to close file')
                pass
            else:
                return
        else:
            logger.debug('Waiting for process to create file')
            pass
        time.sleep(DELAY)

    raise RuntimeError('Timed out waiting for creation of %s' % file)

# def wait_for_file_created_by_process(pid, file, timeout=5):
#     process = psutil.Process(pid)
# 
#     DELAY = 0.01
#     for i in range(int(timeout/DELAY)):
#         open_files = process.open_files()
#         logger.debug(open_files)
#         if os.path.isfile(file):
#             file_open = False
#             for open_file in open_files:
#                 if open_file.path == file:
#                     file_open = True
#             
#             if file_open:
#                 logger.debug('Waiting for process to close file')
#             else:
#                 return
#         else:
#             logger.debug('Waiting for process to create file')
#         time.sleep(DELAY)
# 
#     raise RuntimeError('Timed out waiting for creation of %s' % file)

