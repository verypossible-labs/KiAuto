#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Salvador E. Tropea
# Copyright (c) 2020 Instituto Nacional de Tecnologïa Industrial
# Copyright (c) 2019 Jesse Vincent (@obra)
# Copyright (c) 2018-2019 Seppe Stas (@seppestas) (Productize SPRL)
# Copyright (c) 2015-2016 Scott Bezek (@scottbez1)
# License: Apache 2.0
# Project: KiAuto (formerly kicad-automation-scripts)
# Adapted from: https://github.com/obra/kicad-automation-scripts
"""
Utility functions for UI automation with xdotool in a virtual framebuffer
with XVFB. Also includes utilities for accessing the clipboard for easily
and efficiently copy-pasting strings in the UI.

Based on splitflap/electronics/scripts/export_util.py by Scott Bezek
"""
import os
from subprocess import (Popen, CalledProcessError, TimeoutExpired, call, check_output, STDOUT, DEVNULL, PIPE)
import tempfile
import time
import shutil
import signal
from contextlib import contextmanager
# python3-xvfbwrapper
from xvfbwrapper import Xvfb

from kiauto import log
logger = log.get_logger(__name__)


class PopenContext(Popen):

    def __exit__(self, type, value, traceback):
        logger.debug("Closing pipe with %d", self.pid)
        # Note: currently we don't communicate with the child so these cases are never used.
        # I keep them in case they are needed, but excluded from the coverage.
        # Also note that closing stdin needs extra handling, implemented in the parent class
        # but not here.
        if self.stdout:
            self.stdout.close()  # pragma: no cover
        if self.stderr:
            self.stderr.close()  # pragma: no cover
        if self.stdin:
            self.stdin.close()   # pragma: no cover
        if type:
            logger.debug("Terminating %d", self.pid)
            # KiCad nightly uses a shell script as intermediate to run setup the environment
            # and run the proper binary. If we simply call "terminate" we just kill the
            # shell script. So we create a group and then kill the whole group.
            os.killpg(os.getpgid(self.pid), signal.SIGTERM)
            # self.terminate()
        # Wait for the process to terminate, to avoid zombies.
        try:
            # Wait for 3 seconds
            self.wait(3)
            retry = False
        except TimeoutExpired:  # pragma: no cover
            # The process still alive after 3 seconds
            retry = True
            pass
        if retry:  # pragma: no cover
            logger.debug("Killing %d", self.pid)
            # We shouldn't get here. Kill the process and wait upto 10 seconds
            os.killpg(os.getpgid(self.pid), signal.SIGKILL)
            # self.kill()
            self.wait(10)


def wait_xserver():
    timeout = 10
    DELAY = 0.5
    logger.debug('Waiting for virtual X server ...')
    logger.debug('Current DISPLAY is '+os.environ['DISPLAY'])
    if shutil.which('setxkbmap'):
        cmd = ['setxkbmap', '-query']
    elif shutil.which('setxkbmap'):  # pragma: no cover
        cmd = ['xset', 'q']
    else:  # pragma: no cover
        cmd = ['ls']
        logger.warning('No setxkbmap nor xset available, unable to verify if X is running')
    for i in range(int(timeout/DELAY)):
        with open(os.devnull, 'w') as fnull:
            logger.debug('Checking using '+str(cmd))
            ret = call(cmd, stdout=fnull, stderr=STDOUT, close_fds=True)
            # ret = call(['xset', 'q'])
        if not ret:
            return
        logger.debug('   Retry')
        time.sleep(DELAY)
    raise RuntimeError('Timed out waiting for virtual X server')


def wait_wm():
    timeout = 10
    DELAY = 0.5
    logger.debug('Waiting for Window Manager ...')
    if shutil.which('wmctrl'):
        cmd = ['wmctrl', '-m']
    else:  # pragma: no cover
        logger.warning('No wmctrl, unable to verify if WM is running')
        time.sleep(2)
        return
    logger.debug('Checking using '+str(cmd))
    for i in range(int(timeout/DELAY)):
        ret = call(cmd, stdout=DEVNULL, stderr=STDOUT, close_fds=True)
        if not ret:
            return
        logger.debug('   Retry')
        time.sleep(DELAY)
    raise RuntimeError('Timed out waiting for WM server')


@contextmanager
def start_wm(do_it):
    if do_it:
        cmd = ['fluxbox']
        logger.debug('Starting WM: '+str(cmd))
        with PopenContext(cmd, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, start_new_session=True) as wm_proc:
            wait_wm()
            try:
                yield
            finally:
                logger.debug('Terminating the WM')
                # Fluxbox sometimes will ignore SIGTERM, we can just kill it
                wm_proc.kill()
    else:
        yield


@contextmanager
def start_record(do_record, video_dir, video_name):
    if do_record:
        video_filename = os.path.join(video_dir, video_name)
        cmd = ['recordmydesktop', '--overwrite', '--no-sound', '--no-frame', '--on-the-fly-encoding',
               '-o', video_filename]
        logger.debug('Recording session with: '+str(cmd))
        with PopenContext(cmd, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, start_new_session=True) as screencast_proc:
            try:
                yield
            finally:
                logger.debug('Terminating the session recorder')
                screencast_proc.terminate()
    else:
        yield


@contextmanager
def start_x11vnc(do_it, old_display):
    if do_it:
        if not shutil.which('x11vnc'):
            logger.error("x11vnc isn't installed, please install it")
            yield
        else:
            cmd = ['x11vnc', '-display', os.environ['DISPLAY'], '-localhost']
            logger.debug('Starting VNC server: '+str(cmd))
            with PopenContext(cmd, stdout=DEVNULL, stderr=DEVNULL, close_fds=True, start_new_session=True) as x11vnc_proc:
                if old_display is None:
                    old_display = ':0'
                logger.debug('To monitor the Xvfb now you can start: "ssvncviewer '+old_display+'"(or similar)')
                try:
                    yield
                finally:
                    logger.debug('Terminating the x11vnc server')
                    x11vnc_proc.terminate()
    else:
        yield


@contextmanager
def recorded_xvfb(cfg):
    try:
        old_display = os.environ['DISPLAY']
    except KeyError:
        old_display = None
        pass
    with Xvfb(width=cfg.rec_width, height=cfg.rec_height, colordepth=cfg.colordepth):
        wait_xserver()
        with start_x11vnc(cfg.start_x11vnc, old_display):
            with start_wm(cfg.use_wm):
                with start_record(cfg.record, cfg.video_dir, cfg.video_name):
                    yield


def xdotool(command):
    return check_output(['xdotool'] + command, stderr=DEVNULL)
    # return check_output(['xdotool'] + command)


def clipboard_store(string):
    # I don't know how to use Popen/run to make it run with pipes without
    # either blocking or losing the messages.
    # Using files works really well.
    logger.debug('Clipboard store "'+string+'"')
    # Write the text to a file
    fd_in, temp_in = tempfile.mkstemp(text=True)
    os.write(fd_in, string.encode())
    os.close(fd_in)
    # Capture output
    fd_out, temp_out = tempfile.mkstemp(text=True)
    process = Popen(['xclip', '-selection', 'clipboard', temp_in], stdout=fd_out, stderr=STDOUT)
    ret_code = process.wait()
    os.remove(temp_in)
    os.lseek(fd_out, 0, os.SEEK_SET)
    ret_text = os.read(fd_out, 1000)
    os.close(fd_out)
    os.remove(temp_out)
    ret_text = ret_text.decode()
    if ret_text:  # pragma: no cover
        logger.error('Failed to store string in clipboard')
        logger.error(ret_text)
        raise
    if ret_code:  # pragma: no cover
        logger.error('Failed to store string in clipboard')
        logger.error('xclip returned %d' % ret_code)
        raise


def clipboard_retrieve():
    p = Popen(['xclip', '-o', '-selection', 'clipboard'], stdout=PIPE, stderr=STDOUT)
    output = ''
    for line in p.stdout:
        output += line.decode()
    logger.debug('Clipboard retrieve "'+output+'"')
    return output


def debug_window(id=None):  # pragma: no cover
    if log.get_level() < 2:
        return
    if shutil.which('xprop'):
        if id is None:
            try:
                id = xdotool(['getwindowfocus']).rstrip()
            except CalledProcessError:
                logger.debug('xdotool getwindowfocus failed!')
                pass
        if id:
            call(['xprop', '-id', id])


def wait_focused(id, timeout=10):
    DELAY = 0.5
    logger.debug('Waiting for %s window to get focus...', id)
    for i in range(int(timeout/DELAY)):
        cur_id = xdotool(['getwindowfocus']).rstrip()
        logger.debug('Currently focused id: %s', cur_id)
        if cur_id == id:
            return
        time.sleep(DELAY)
    debug_window(cur_id)  # pragma: no cover
    raise RuntimeError('Timed out waiting for %s window to get focus' % id)


def wait_not_focused(id, timeout=10):
    DELAY = 0.5
    logger.debug('Waiting for %s window to lose focus...', id)
    for i in range(int(timeout/DELAY)):
        try:
            cur_id = xdotool(['getwindowfocus']).rstrip()
        except CalledProcessError:
            # When no window is available xdotool receives ID=1 and exits with error
            return
        logger.debug('Currently focused id: %s', cur_id)
        if cur_id != id:
            return
        time.sleep(DELAY)
    debug_window(cur_id)  # pragma: no cover
    raise RuntimeError('Timed out waiting for %s window to lose focus' % id)


def wait_for_window(name, window_regex, timeout=10, focus=True, skip_id=0, others=None):
    DELAY = 0.5
    logger.info('Waiting for "%s" ...', name)
    if skip_id:
        logger.debug('Will skip %s', skip_id)
    xdotool_command = ['search', '--onlyvisible', '--name', window_regex]

    for i in range(int(timeout/DELAY)):
        try:
            window_id = xdotool(xdotool_command).splitlines()
            logger.debug('Found %s window (%d)', name, len(window_id))
            if len(window_id) == 1:
                id = window_id[0]
            if len(window_id) > 1:
                id = window_id[1]
            logger.debug('Window id: %s', id)
            if id != skip_id:
                if focus:
                    xdotool_command = ['windowfocus', '--sync', id]
                    xdotool(xdotool_command)
                    wait_focused(id, timeout)
                return window_id
            else:
                logger.debug('Skipped')
        except CalledProcessError:
            pass
        # Check if we have a list of alternative windows
        if others:
            for other in others:
                cmd = ['search', '--onlyvisible', '--name', other]
                try:
                    xdotool(cmd)
                    raise ValueError(other)
                except CalledProcessError:
                    pass
        time.sleep(DELAY)
    debug_window()  # pragma: no cover
    raise RuntimeError('Timed out waiting for %s window' % name)


def wait_point(cfg):
    if cfg.wait_for_key:
        input('Press a key')
