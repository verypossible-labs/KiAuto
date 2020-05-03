#!/usr/bin/make
PY_COV=python3-coverage
REFDIR=tests/reference/
GOOD=tests/kicad5/good-project/good-project.kicad_pcb
GOOD_SCH=tests/kicad5/good-project/good-project.sch
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
	$(PY_COV) erase
	pytest-3
	$(PY_COV) report

test_local: lint
	rm -rf output
	$(PY_COV) erase
	pytest-3 --test_dir output
	$(PY_COV) report
	$(PY_COV) html
	x-www-browser htmlcov/index.html

test_docker_local:
	rm -rf output
	# Run in the same directory to make the __pycache__ valid
	# Also change the owner of the files to the current user (we run as root like in GitHub)
	docker run --rm -v $(CWD):$(CWD) --workdir="$(CWD)" setsoft/kicad_auto_test:latest \
		/bin/bash -c "flake8 . --count --statistics ; pytest-3 --test_dir output ; chown -R $(USER_ID):$(GROUP_ID) output/"

gen_ref:
	# Reference outputs, must be manually inspected if regenerated
	pcbnew_print_layers --output_name good_pcb_with_dwg.pdf $(GOOD) $(REFDIR) F.Cu F.SilkS Dwgs.User Edge.Cuts
	pcbnew_print_layers --output_name good_pcb_inners.pdf   $(GOOD) $(REFDIR) F.Cu F.SilkS GND.Cu Signal1.Cu Signal2.Cu Power.Cu Edge.Cuts
	pcbnew_print_layers --list $(GOOD) > $(REFDIR)good_pcb_layers.txt
	eeschema_do export --file_format pdf --all $(GOOD_SCH) $(REFDIR)
	mv $(REFDIR)good-project.pdf $(REFDIR)good_sch_all.pdf
	eeschema_do export --file_format pdf $(GOOD_SCH) $(REFDIR)
	mv $(REFDIR)good-project.pdf $(REFDIR)good_sch_top.pdf
	eeschema_do export --file_format svg --all $(GOOD_SCH) $(REFDIR)
	# I really hate this, files has time stamps, 3 of them in fact, WHY ANOTHER INSIDE!!!
	sed -E 's/date .* <\/title>/DATE <\/title>/' $(REFDIR)good-project.svg > $(REFDIR)good-project.svg.new
	mv $(REFDIR)good-project.svg.new $(REFDIR)good-project.svg
	sed -E 's/date .* <\/title>/DATE <\/title>/' $(REFDIR)logic-logic.svg > $(REFDIR)logic-logic.svg.new
	mv $(REFDIR)logic-logic.svg.new $(REFDIR)logic-logic.svg
	sed -E 's/date .* <\/title>/DATE <\/title>/' $(REFDIR)power-Power.svg > $(REFDIR)power-Power.svg.new
	mv $(REFDIR)power-Power.svg.new $(REFDIR)power-Power.svg

.PHONY: deb deb_clean test lint test_local gen_ref test_docker_local

