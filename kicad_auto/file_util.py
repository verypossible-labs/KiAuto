#!/usr/bin/env python

import os
import time
# python3-psutil
import psutil

from kicad_auto import log
logger = log.get_logger(__name__)


def wait_for_file_created_by_process(pid, file, timeout=5):
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
