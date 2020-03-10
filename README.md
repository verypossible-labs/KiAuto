KiCad automation scripts
========================

A bunch of scripts to automate [KiCad] processes using UI automation with [xdotool].

This is a fork of Productize SPRL's  [scripts](https://github.com/productize/kicad-automation-scripts), based in big parts on Scott Bezek's scripts in his 
[split-flap display project][split-flap].
For more info see his [excellent blog posts][scot's blog].

Currently tested and working:

- Exporting schematics to PDF and SVG
- Exporting layouts to PDF 
- Running ERC on schematics
- Running DRC on layouts
- Netlist generation
- Basic BoM generation (mainly the XML needed for KiBoM)

Note that this version is more oriented to support running the scripts in your main system, instead of a docker image.

## Instalation

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

Tools like KiBoM can generate a nice BoM, but in order to run them from the command line you need to be sure that the project's XML BoM is updated. You can do it running:
``` 
eeschema_do bom_xml YOUR_SCHEMATIC.sch DESTINATION/
```
After running it *./YOUR_SCHEMATIC.xml* will be updated. You'll also get *DESTINATION/YOUR_SCHEMATIC.csv* contain a very basic BoM generated using KiCad's *bom2grouped_csv.xsl* template.

### Run DRC:

To run the Distance Rules Check:
```
pcbnew_run_drc YOUR_PCB.kicad_pcb DESTINATION/
```
If an error is detected you'll get a message and the script will return a negative error level. Additionally you'll get *DESTINATION/drc_result.rpt* containing KiCad's report. You can select the name of the report using *--output_name* and you can ignore unconneted nets using *--ignore_unconnected*.

### Export layout as PDF

This is useful to complement your gerber files including some extra information in the *Dwgs.User* or *Cmts.User* layer.
```
pcbnew_print_layers YOUR_PCB.kicad_pcb DESTINATION/ LAYER1 LAYER2
```
Will generate *DESTINATION/printed.pdf* containing LAYER1 and LAYER2 overlapped. You can list as many layers as you want. I use things like ```F.Cu Dwgs.User```. The name of the layers is the same you see in the GUI, if your first inner layer is GND you just need to use ```GND.Cu```.

### Common options

By default all the scripts run very quiet. If you want to get some information about what's going on use *-v*. 

The nature of these scripts make them very fragile. In particular when you run them in your every day desktop. You must avoid having *eeschema* and/or *pcbnew* windows opened while running the scripts. If you need to debug a problem you can:
1. Use the *-vv* option to get debug information
2. Use the *-r* option to record a video (OGV format) containing the GUI session. The file will be stored in the output directory and its name will begin with the name of the requested command.

## Useful references

KiCad: http://kicad-pcb.org/
xdotool: https://github.com/jordansissel/xdotool
split-flap: https://github.com/scottbez1/splitflap
scot's blog: https://scottbezek.blogspot.be/2016/04/scripting-kicad-pcbnew-exports.html
Dockerhub: https://hub.docker.com/r/productize/kicad-automation-scripts
