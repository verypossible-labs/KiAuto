import os
import re
from sys import exit, path

# Default W,H for recording
REC_W = 1366
REC_H = 960

# Return error codes
# Positive values are ERC/DRC errors
NO_SCHEMATIC = 1
WRONG_ARGUMENTS = 2   # This is what argsparse uses
EESCHEMA_CFG_PRESENT = 11
KICAD_CFG_PRESENT = 3
NO_PCB = 4
PCBNEW_CFG_PRESENT = 5
WRONG_LAYER_NAME = 6
WRONG_PCB_NAME = 7
WRONG_SCH_NAME = 8
PCBNEW_ERROR = 9
EESCHEMA_ERROR = 10
NO_PCBNEW_MODULE = 11
USER_HOTKEYS_PRESENT = 12
# Wait 25 s to pcbnew/eeschema window to be present
WAIT_START = 25
# Name for testing versions
NIGHTLY = 'nightly'

KICAD_VERSION_5_99 = 5099000
KICAD_SHARE = '/usr/share/kicad/'
KICAD_NIGHTLY_SHARE = '/usr/share/kicad-nightly/'


class Config(object):
    def __init__(self, logger, args=None):
        self.export_format = 'pdf'
        if args:
            # Session debug
            self.use_wm = args.use_wm  # Use a Window Manager, dialogs behaves in a different way
            self.start_x11vnc = args.start_x11vnc
            self.rec_width = args.rec_width
            self.rec_height = args.rec_height
            self.record = args.record
            self.video_dir = args.output_dir
            self.wait_for_key = args.wait_key
            # Others
            if hasattr(args, 'file_format'):
                self.export_format = args.file_format.lower()
        else:
            # Session debug
            self.use_wm = False
            self.start_x11vnc = False
            self.rec_width = REC_W
            self.rec_height = REC_H
            self.record = False
            self.video_dir = None
            self.wait_for_key = False
        self.colordepth = 24
        self.video_name = None
        # Executable and dirs
        self.eeschema = 'eeschema'
        self.pcbnew = 'pcbnew'
        self.kicad_conf_dir = 'kicad'
        ng_ver = os.environ.get('KIAUS_USE_NIGHTLY')
        if ng_ver:
            self.eeschema += '-'+NIGHTLY
            self.pcbnew += '-'+NIGHTLY
            self.kicad_conf_dir += os.path.join(NIGHTLY, ng_ver)
            # Path to the Python module
            path.insert(0, '/usr/lib/kicad-nightly/lib/python3/dist-packages')
        # Detect KiCad version
        try:
            import pcbnew
        except ImportError:
            logger.error("Failed to import pcbnew Python module."
                         " Is KiCad installed?"
                         " Do you need to add it to PYTHONPATH?")
            exit(NO_PCBNEW_MODULE)
        m = re.match(r'(\d+)\.(\d+)\.(\d+)', pcbnew.GetBuildVersion())
        self.kicad_version_major = int(m.group(1))
        self.kicad_version_minor = int(m.group(2))
        self.kicad_version_patch = int(m.group(3))
        self.kicad_version = self.kicad_version_major*1000000+self.kicad_version_minor*1000+self.kicad_version_patch
        logger.debug('Detected KiCad v{}.{}.{} ({})'.format(self.kicad_version_major, self.kicad_version_minor,
                     self.kicad_version_patch, self.kicad_version))
        # Config file names
        self.kicad_conf_path = os.path.join(os.environ['HOME'], '.config/'+self.kicad_conf_dir)
        # - eeschema config
        self.conf_eeschema = os.path.join(self.kicad_conf_path, 'eeschema')
        self.conf_eeschema_bkp = None
        self.conf_eeschema_json = False
        if self.kicad_version >= KICAD_VERSION_5_99:
            self.conf_eeschema += '.json'
            self.conf_eeschema_json = True
        # - pcbnew config
        # 20200912: pcbnew still in old format
        self.conf_pcbnew = os.path.join(self.kicad_conf_path, 'pcbnew')
        self.conf_pcbnew_bkp = None
        self.conf_pcbnew_json = False
        # - kicad config
        self.conf_kicad = os.path.join(self.kicad_conf_path, 'kicad_common')
        self.conf_kicad_bkp = None
        self.conf_kicad_json = False
        if self.kicad_version >= KICAD_VERSION_5_99:
            self.conf_kicad += '.json'
            self.conf_kicad_json = True
        # - hotkeys
        self.conf_hotkeys = os.path.join(self.kicad_conf_path, 'user.hotkeys')
        self.conf_hotkeys_bkp = None
        # - sym-lib-table
        self.user_sym_lib_table = os.path.join(self.kicad_conf_path, 'sym-lib-table')
        self.user_fp_lib_table = os.path.join(self.kicad_conf_path, 'fp-lib-table')
        self.sys_sym_lib_table = [KICAD_SHARE+'template/sym-lib-table']
        self.sys_fp_lib_table = [KICAD_SHARE+'template/fp-lib-table']
        if ng_ver:
            # 20200912: sym-lib-table is missing
            self.sys_sym_lib_table.insert(0, KICAD_NIGHTLY_SHARE+'template/sym-lib-table')
            self.sys_fp_lib_table.insert(0, KICAD_NIGHTLY_SHARE+'template/fp-lib-table')
        # Some details about the UI
        if self.kicad_version >= KICAD_VERSION_5_99:
            # KiCad 5.99.0
            self.ee_window_title = r'\[/\] — Eeschema$'  # "PROJECT [HIERARCHY_PATH] - Eeschema"
        else:
            # KiCad 5.1.6
            self.ee_window_title = r'Eeschema.*\.sch'  # "Eeschema - file.sch"


__version__ = '1.4.2'
