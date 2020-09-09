#!/usr/bin/make
PY_COV=python3-coverage
PYTEST=pytest-3
REFDIR=tests/reference/
GOOD=tests/kicad5/good-project/good-project.kicad_pcb
REFILL=tests/kicad5/zone-refill/zone-refill.kicad_pcb
GOOD_SCH=tests/kicad5/good-project/good-project.sch
CWD := $(abspath $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST))))))
USER_ID=$(shell id -u)
GROUP_ID=$(shell id -g)

deb:
	fakeroot dpkg-buildpackage -uc -b

deb_clean:
	fakeroot debian/rules clean

lint:
	# flake8 --filename is broken
	ln -sf src/eeschema_do eeschema_do.py
	ln -sf src/pcbnew_do pcbnew_do.py
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --statistics
	rm eeschema_do.py pcbnew_do.py

test: lint
	$(PY_COV) erase
	$(PYTEST)
	$(PY_COV) report

test_local: lint
	rm -rf output
	$(PY_COV) erase
	$(PYTEST) --test_dir output
	$(PY_COV) report
	$(PY_COV) html
	x-www-browser htmlcov/index.html

test_docker_local:
	rm -rf output
	$(PY_COV) erase
	# Run in the same directory to make the __pycache__ valid
	# Also change the owner of the files to the current user (we run as root like in GitHub)
	docker run --rm -v $(CWD):$(CWD) --workdir="$(CWD)" setsoft/kicad_auto_test:latest \
		/bin/bash -c "flake8 . --count --statistics ; $(PYTEST) --test_dir output ; chown -R $(USER_ID):$(GROUP_ID) output/ tests/kicad5/"
	$(PY_COV) report
	$(PY_COV) html
	x-www-browser htmlcov/index.html

docker_shell:
	docker run  -it --rm -v $(CWD):$(CWD) --workdir="$(CWD)" \
	-v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$(DISPLAY) \
	--user $(USER_ID):$(GROUP_ID) \
	--volume="/etc/group:/etc/group:ro" \
	--volume="/etc/passwd:/etc/passwd:ro" \
	--volume="/etc/shadow:/etc/shadow:ro" \
	--volume="/home/$(USER):/home/$(USER):rw" \
	setsoft/kicad_auto_test:latest /bin/bash

docker_deb_shell:
	docker run  -it --rm -v $(CWD):$(CWD) --workdir="$(CWD)" \
	-v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$(DISPLAY) \
	--user $(USER_ID):$(GROUP_ID) \
	--volume="/etc/group:/etc/group:ro" \
	--volume="/etc/passwd:/etc/passwd:ro" \
	--volume="/etc/shadow:/etc/shadow:ro" \
	--volume="/home/$(USER):/home/$(USER):rw" \
	setsoft/kicad_pybuild:latest /bin/bash

gen_ref:
	# Reference outputs, must be manually inspected if regenerated
	cp -a $(REFILL).refill $(REFILL)
	src/pcbnew_do export --output_name zone-refill.pdf $(REFILL) $(REFDIR) F.Cu B.Cu Edge.Cuts
	cp -a $(REFILL).ok $(REFILL)
	src/pcbnew_do export --output_name good_pcb_with_dwg.pdf $(GOOD) $(REFDIR) F.Cu F.SilkS Dwgs.User Edge.Cuts
	src/pcbnew_do export --output_name good_pcb_inners.pdf   $(GOOD) $(REFDIR) F.Cu F.SilkS GND.Cu Signal1.Cu Signal2.Cu Power.Cu Edge.Cuts
	src/pcbnew_do export --list $(GOOD) > $(REFDIR)good_pcb_layers.txt
	src/eeschema_do export --file_format pdf --all $(GOOD_SCH) $(REFDIR)
	mv $(REFDIR)good-project.pdf $(REFDIR)good_sch_all.pdf
	src/eeschema_do export --file_format pdf $(GOOD_SCH) $(REFDIR)
	mv $(REFDIR)good-project.pdf $(REFDIR)good_sch_top.pdf
	src/eeschema_do export --file_format svg --all $(GOOD_SCH) $(REFDIR)
	# I really hate this, files has time stamps, 3 of them in fact, WHY ANOTHER INSIDE!!!
	sed -E 's/date .* <\/title>/DATE <\/title>/' $(REFDIR)good-project.svg > $(REFDIR)good-project.svg.new
	mv $(REFDIR)good-project.svg.new $(REFDIR)good-project.svg
	sed -E 's/date .* <\/title>/DATE <\/title>/' $(REFDIR)logic-logic.svg > $(REFDIR)logic-logic.svg.new
	mv $(REFDIR)logic-logic.svg.new $(REFDIR)logic-logic.svg
	sed -E 's/date .* <\/title>/DATE <\/title>/' $(REFDIR)power-Power.svg > $(REFDIR)power-Power.svg.new
	mv $(REFDIR)power-Power.svg.new $(REFDIR)power-Power.svg
	src/eeschema_do export --file_format ps --all $(GOOD_SCH) $(REFDIR)
	sed -E -e 's/^%%CreationDate: .*/%%CreationDate: DATE/' -e 's/^%%Title: .*/%%Title: TITLE/' $(REFDIR)good-project.ps > $(REFDIR)good-project.ps.new
	mv $(REFDIR)good-project.ps.new $(REFDIR)good-project.ps
	sed -E -e 's/^%%CreationDate: .*/%%CreationDate: DATE/' -e 's/^%%Title: .*/%%Title: TITLE/' $(REFDIR)logic-logic.ps > $(REFDIR)logic-logic.ps.new
	mv $(REFDIR)logic-logic.ps.new $(REFDIR)logic-logic.ps
	sed -E -e 's/^%%CreationDate: .*/%%CreationDate: DATE/' -e 's/^%%Title: .*/%%Title: TITLE/' $(REFDIR)power-Power.ps > $(REFDIR)power-Power.ps.new
	mv $(REFDIR)power-Power.ps.new $(REFDIR)power-Power.ps

single_test:
	rm -rf pp
	-$(PYTEST) --log-cli-level debug -k "$(SINGLE_TEST)" --test_dir pp
	@echo "********************" Output
	@cat pp/*/output.txt
	@echo "********************" Error
	@tail -n 30 pp/*/error.txt

.PHONY: deb deb_clean test lint test_local gen_ref test_docker_local single_test

