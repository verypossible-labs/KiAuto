KiCad automation scripts
========================

![Python application](https://github.com/INTI-CMNB/kicad-automation-scripts/workflows/Python%20application/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/INTI-CMNB/kicad-automation-scripts/badge.svg?branch=master&service=github)](https://coveralls.io/github/INTI-CMNB/kicad-automation-scripts?branch=master)

A bunch of scripts to automate [KiCad](https://www.kicad-pcb.org/) processes using UI automation with [xdotool](https://www.semicomplete.com/projects/xdotool/).

This is a fork of Productize SPRL's  [scripts](https://github.com/productize/kicad-automation-scripts), based in big parts on Scott Bezek's scripts in his 
[split-flap display project](https://scottbez1.github.io/splitflap/).
For more info see his [excellent blog posts][scot's blog].

Currently tested and working:

- Exporting schematics to PDF, SVG, PS, DXF and HPGL
- Exporting layouts to PDF 
- Running ERC on schematics
- Running DRC on layouts
- Netlist generation
- Basic BoM generation (mainly the XML needed for [KiBoM](https://github.com/SchrodingersGat/KiBoM))

If you are looking for Gerbers, Drill and Position take a look at [KiPlot](https://github.com/INTI-CMNB/kiplot).

If you are looking for STEP files creation take a look at *kicad2step*, part of KiCad.

## Installation

### Dependencies

If you are installing from a Debian package you don't need to worry about dependencies, otherwise you need to install:

- [**KiCad**](http://kicad-pcb.org/) 5.1.x
- [**xsltproc**](http://xmlsoft.org/xslt/) (usually installed as a KiCad dependency). Only needed for BoMs.
- [**xdotool**](https://github.com/jordansissel/xdotool)
- [**xclip**](https://github.com/astrand/xclip)

If you want to debug problems you could also need:

- [**recordmydesktop**](http://recordmydesktop.sourceforge.net/about.php), to create a video of the KiCad session.
- [**x11vnc**](http://www.karlrunge.com/x11vnc/) and a client like [**ssvnc**](http://www.karlrunge.com/x11vnc/ssvnc.html), to see the KiCad live interaction.
- [**fluxbox**](http://fluxbox.org/) and [**wmctrl**](http://tripie.sweb.cz/utils/wmctrl/) if you want to have a window manager when using **x11vnc**. Othewise windows can't be moved.

### No installation

You can use the scripts without installing. The scripts are located at the *src/* directory.

You can also define a bash aliases:

```
alias pcbnew_do=PATH_TO_REPO/src/pcbnew_do
alias eeschema_do=PATH_TO_REPO/src/eeschema_do
```

Note that the following Python 3 packages must be installed:

- [**xvfbwrapper**](https://pypi.org/project/xvfbwrapper/)
- [**psutil**](https://pypi.org/project/psutil/)

### Python style installation

Just run the setup, like with any other Python tool:

```
sudo python3 setup.py install
```

### Installation on Ubuntu/Debian:

Get the Debian package from the [releases section](https://github.com/INTI-CMNB/kicad-automation-scripts/releases) and run:
```
sudo apt install ./kicad-automation-scripts.inti-cmnb_*_all.deb 
```

## Usage

You can get detailed help using the *--help* command line option. Here I include some basic usage.

### Export a schematic to PDF (or SVG)

```
eeschema_do export -a YOUR_SCHEMATIC.sch DESTINATION/
```
This will create *DESTINATION/YOUR_SCHEMATIC.pdf* file containing all the schematic pages. If you want just one page remove the *-a* option. If you want an SVG file just use *-f svg* like this:
```
eeschema_do export -a -f svg YOUR_SCHEMATIC.sch DESTINATION/
```
In this case you'll get one SVG for each page in your schematic.

### Run ERC:

To run the Electrical Rules Check:
```
eeschema_do run_erc YOUR_SCHEMATIC.sch DESTINATION/
```
If an error is detected you'll get a message and the script will return a negative error level. Additionally you'll get *DESTINATION/YOUR_SCHEMATIC.erc* containing KiCad's report.

### Generate netlist:

To generate or update the netlist, needed by other tools:
``` 
eeschema_do netlist YOUR_SCHEMATIC.sch DESTINATION/
```
You'll get *DESTINATION/YOUR_SCHEMATIC.net*

### Update BoM XML/basic BoM generation:

Tools like [KiBoM](https://github.com/SchrodingersGat/KiBoM) can generate a nice BoM, but in order to run them from the command line you need to be sure that the project's XML BoM is updated. You can do it running:
``` 
eeschema_do bom_xml YOUR_SCHEMATIC.sch DESTINATION/
```
After running it *./YOUR_SCHEMATIC.xml* will be updated. You'll also get *DESTINATION/YOUR_SCHEMATIC.csv* contain a very basic BoM generated using KiCad's *bom2grouped_csv.xsl* template.

### Run DRC:

To run the Distance Rules Check:
```
pcbnew_do run_drc YOUR_PCB.kicad_pcb DESTINATION/
```
If an error is detected you'll get a message and the script will return a negative error level. Additionally you'll get *DESTINATION/drc_result.rpt* containing KiCad's report. You can select the name of the report using *--output_name* and you can ignore unconneted nets using *--ignore_unconnected*.

### Export layout as PDF

This is useful to complement your gerber files including some extra information in the *Dwgs.User* or *Cmts.User* layer.
```
pcbnew_do export YOUR_PCB.kicad_pcb DESTINATION/ LAYER1 LAYER2
```
Will generate *DESTINATION/printed.pdf* containing LAYER1 and LAYER2 overlapped. You can list as many layers as you want. I use things like ```F.Cu Dwgs.User```. The name of the layers is the same you see in the GUI, if your first inner layer is GND you just need to use ```GND.Cu```.

If you need to get a list of valid layers run:

```
pcbnew_do export --list YOUR_PCB.kicad_pcb
```

### Common options

By default all the scripts run very quiet. If you want to get some information about what's going on use *-v*. 

The nature of these scripts make them very fragile. In particular when you run them in your every day desktop. You must avoid having *eeschema* and/or *pcbnew* windows opened while running the scripts. If you need to debug a problem you can:
1. Use the *-vv* option to get debug information
2. Use the *-r* option to record a video (OGV format) containing the GUI session. The file will be stored in the output directory and its name will begin with the name of the requested command.
3. Use the *-s* and *-w* options to start **x11vnc**. The execution will stop asking for a keypress. At this time you can start a VNC client like this: ```ssvncviewer :0```. You'll be able to see KiCad running and also interact with it.
4. Same as 3 but also using *-m*, in this case you'll get a window manager to move the windows and other stuff.

### Ignoring warnings and errors from ERC/DRC

Sometimes we need to ignore some warnings and/or errors reported during the ERC and/or DRC test.

To achieve it you need to create a *filters file*. Each line contains a rule to exclude one or more matching errors. The syntax is:

```
ERROR_NUMBER,REGULAR_EXPRESSION
```

The regular expression must follow the Python syntax. In the simplest case this can be just the text that the error must contain.

The error number is just the KiCad internal number for the error you want to ignore.

Here is an example, suppose our report says:

```
** Created on 2020-06-05 11:16:21 **

** Found 2 DRC errors **
ErrType(45): Courtyards overlap
    @(144.361 mm, 101.752 mm): Footprint C16 on F.Cu
    @(144.825 mm, 101.244 mm): Footprint C19 on F.Cu
ErrType(45): Courtyards overlap
    @(159.885 mm, 97.663 mm): Footprint R4 on F.Cu
    @(160.393 mm, 97.191 mm): Footprint C21 on F.Cu

** Found 0 unconnected pads **

** End of Report **
```

Here we have two errors, both number 45. So lets suppose we want to ignore the first error, we could use the following filter:

```
45,Footprint C16
```

This will ignore any error of type 45 (Courtyards overlap) related to *Footprint C16*. To use
it you just need mto use the *-f* command line option:


```
pcbnew_do run_drc -f FILTER_FILE YOUR_PCB.kicad_pcb DESTINATION/
```


## Useful references

split-flap: https://github.com/scottbez1/splitflap

scot's blog: https://scottbezek.blogspot.be/2016/04/scripting-kicad-pcbnew-exports.html

Dockerhub: https://hub.docker.com/repository/docker/setsoft/kicad_auto
