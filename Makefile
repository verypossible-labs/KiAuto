#!/usr/bin/make
REFDIR=tests/reference/
GOOD=tests/kicad5/good-project/good-project.kicad_pcb

deb:
	fakeroot dpkg-buildpackage -uc -b

deb_clean:
	fakeroot debian/rules clean

lint:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --statistics

test: lint
	pytest-3

test_local: lint
	pytest-3 --test_dir output

gen_ref:
	pcbnew_print_layers --output_name good_pcb_with_dwg.pdf $(GOOD) $(REFDIR) F.Cu F.SilkS Dwgs.User Edge.Cuts
	pcbnew_print_layers --output_name good_pcb_inners.pdf   $(GOOD) $(REFDIR) F.Cu F.SilkS GND.Cu Signal1.Cu Signal2.Cu Power.Cu Edge.Cuts
	pcbnew_print_layers --list $(GOOD) > $(REFDIR)good_pcb_layers.txt

.PHONY: deb deb_clean test lint test_local gen_ref
