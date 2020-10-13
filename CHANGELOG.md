# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

## [1.5.2] - 2020-10-12
### Added
- Option to pcbnew_do export:
  - `--mirror/-M`      Mirror printing (KiCad 6 only!)

## [1.5.1] - 2020-10-08
### Added
- Options to pcbnew_do export:
  - `--scaling/-s`     Scale factor (0 fit page)
  - `--pads/-p`        Pads style (0 none, 1 small, 2 full)
  - `--no-title/-t`    Remove the title-block
  - `--monochrome/-m`  Print in blanck and white
  - `--separate/-S`    Layers in separated sheets

## [1.5.0] - 2020-10-05
### Added
- Support for KiCad Nightly
  - Just define the environment variable: `KIAUS_USE_NIGHTLY=5.99`

## [1.4.2] - 2020-09-10
### Fixed
- Crash when no arguments.
- Crash when no x11vnc and it was requested.
- Lost warning messages when using --warnings_as_errors

## [1.4.1] - 2020-06-14
### Added
- --fill_zones/-f option to 'pcbnew_do export' to fill zones before printing.

### Changed
- Filtered errors are displayed as warnings, but ignored.
- Filtered warnings are displayed as information.
- When an error/warning is filtered a debug message informs which regex matched.

## [1.4.0] - 2020-06-08
### Added
- --errors_filter/-f option to provide a file containing errors to ignore from DRC/ERC.

### Fixed
- Sometimes when using a WM the "pcbnew_do export" failed to open the Printer dialog.
- Sometimes when exiting xdotool didn't find any window and reported error.
- When the filled zones changed during DRC the PCB could be saved even when we didn't
  specify --save

## [1.3.1] - 2020-05-19
### Fixed
- Under some situations the EEschema plot dialog failed to clear the old file path
  and we pasted concatenated. Was introduced when fixing the browse button selected.

## [1.3.0] - 2020-05-18
### Added
- --wait_key/-w option to send the commands step by step (debug)
- --start_x11vnc/-s option to start a server so we can monitor what's going on (debug)
- --use_wm/-m option to start a window manager (fluxbox) so we can interact better (debug)

### Changed
- Now we exit eeschema and pcbnew without killing the application.
- Default record height now is 960.

### Fixed
- Error and Warning dialog detection. Now we use more specific regular expressions.
- Sometimes the 'Plot Schematic Options' starts with the browse button selected and we
must move left.
- Sometimes the netlist dialog starts with the generation button selected and we move to
the plugin button instead. Now we detect it and go back to the generate button.

## [1.2.0] - 2020-05-13
### Added
- Support for PS, DXF and HPGL to the schematic export.
- Support for eeschema already running.
- Support for loading KiCad 4 schematics (asking for Remap symbols)

### Changed
- pcbnew_print_layers to "pcbnew_do export" to be coherent with "eeschema_do"
- pcbnew_run_drc to "pcbnew_do run_drc" ditto

### Fixed
- --ignore_unconnected of pcbnew_run_drc wasn't implemented.
- ERC omitted warnings if errors were detected.
- The project file could be altered, or even lost, during schematic export.

## [1.1.6] - 2020-04-23
### Changed
- Now we use setxkbmap instead of xset to test X is working.
If setxkbmap isn't available we default to xset.

## [1.1.5] - 2020-04-20
### Added
- More support for docker environment in the pcbnew scripts

### Changed
- Now eeschema_do reports ERC warnings as warning messages

## [1.1.4] - 2020-04-20
### Added
- Support missing *-lib-table in user config
- Create the KiCad config dir if it doesn't exist

### Fixed
- Two missing dependences.

## [1.1.3] - 2020-03-30
### Changed
- Debug and info colors.

## [1.1.2] - 2020-03-21
### Added
- Support for the names used by kiplot for the inner layers.

## [1.1.1] - 2020-03-18
### Fixed
- Supressed eeschema stdout to avoid printing the ERC report.
- ERC errors now reported as negative values.

## [1.1.0] - 2020-03-16
### Added
- --save to save the PCB after DRC (updating filled zones)

### Changed
- Sorted command line options

### Fixed
- Give more priority to the local module instead of the system wide installed.

## [1.0.0] - 2020-03-10
### Added
- Option to list all layers to pcbnew_print_layers.
- Documentation for the new scripts.
- Debian package files.
- Different error levels.
- --version and --verbose.
- Unified the loggers and made it coloured.
- Width and height config for the record function.
- --output_name option to the DRC.
- Netlist generation
- Simple BoM (XML) generation
- Print a PDF containing one or more layers.

### Changed
- Error level of src/pcbnew_run_drc to negative to be more coherent with the
run_erc command.
- Interpreter to Python 3.
- Renamed the main scripts so they don't include .py in the name.
- Renamed the "util" package to "kicad_auto" (less generic).
- Moved the eeschema/export_bom.py functionality to the bom_xml command of
src/eeschema_do.
- eeschema/schematic.py -> src/eeschema_do.py (more descriptive name).
- Now we keep only the last recorded video.
- Added creation of a suitable eeschema config, instead of editing the current.
- Made schematic and output_dir position args (always used).
- Removed --screencast_dir in favor of --record (+ size).
- _pcbnew/print_layers.py to src/pcbnew_print_layers.
- Renamed _pcbnew/run_drc.py to src/pcbnew_run_drc.
- Made some debug/info message classification to make it cleaner.
- Supressed the recordmydesktop output.
- Now the screencast files are named according to the recorded task.
- Suppressed the pcbnew stderr (noissy).
- Disabled long waits to test for old errors.
- Adapted to KiCad 5.1.x.
- Saves the current pcbnew/eeschema config and creates one usable.
The originals are restored.

### Removed
- Custom configs. Now they are generated on-the-fly.
- _pcbnew/generate_svg.py, its functionality can be achieved using pcbnew_print_layers.
- _pcbnew/generate_gerber.py, kiplot project has a better solution.

### Fixed
- Simplified the copy/paste mechanism used for run_erc. The old one could fail.
- src/pcbnew* always recorded the session.
- Adjusted the pcbnew first time-out, for some reason I'm getting huge delays.
- A test (and wait) for the Xvfb, sometimes is slow and xclip runs before it.
- clipboard_store rewrite, the old version ignored any errors
- Made stronger the eeschema config parser.
- Language set as english + UTF-8 (to run outside docker).


