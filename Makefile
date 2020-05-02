#!/usr/bin/make
REFDIR=tests/reference/
GOOD=tests/kicad5/good-project/good-project.kicad_pcb
CWD := $(abspath $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST))))))
USER_ID=$(shell id -u)
GROUP_ID=$(shell id -g)

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

test_docker_local:
	# Run in the same directory to make the __pycache__ valid
	# Also change the owner of the files to the current user (we run as root like in GitHub)
	docker run --rm -v $(CWD):$(CWD) --workdir="$(CWD)" setsoft/kicad_auto_test:latest \
		/bin/bash -c "flake8 . --count --statistics ; pytest-3 --test_dir output ; chown -R $(USER_ID):$(GROUP_ID) output/"

gen_ref:
	pcbnew_print_layers --output_name good_pcb_with_dwg.pdf $(GOOD) $(REFDIR) F.Cu F.SilkS Dwgs.User Edge.Cuts
	pcbnew_print_layers --output_name good_pcb_inners.pdf   $(GOOD) $(REFDIR) F.Cu F.SilkS GND.Cu Signal1.Cu Signal2.Cu Power.Cu Edge.Cuts
	pcbnew_print_layers --list $(GOOD) > $(REFDIR)good_pcb_layers.txt

.PHONY: deb deb_clean test lint test_local gen_ref test_docker_local
