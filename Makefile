NAME = euler-copilot-tune
VERSION = 2.0.0
SRCVERSION = $(shell git rev-parse --short HEAD 2>/dev/null)
COPILOTTUNEVERSION = $(VERSION)$(if $(SRCVERSION),($(SRCVERSION)))

PYTHON=$(shell which python3)
PYTHON_SITELIB = $(shell $(PYTHON) -c 'from sysconfig import get_path; print(get_path("purelib"));')
DESTDIR   ?= /
PREFIX    ?= /usr
BINDIR     = $(DESTDIR)$(PREFIX)/bin
LIBEXECDIR = $(DESTDIR)$(PREFIX)/libexec
SYSTEMDDIR = $(DESTDIR)$(PREFIX)/lib/systemd/system
TUNECONFDIR = $(DESTDIR)/etc/euler-copilot-tune
VENV       = venv
CURDIR     = $(shell pwd)
.PHONY: all clean venv help run

all:
	@echo "run make install to install euler copilot tune in system"

collector-install:
	@echo "run make install to install euler copilot tune in system"

install-dirs:
	mkdir -p $(TUNECONFDIR)/knowledge_base
	mkdir -p $(TUNECONFDIR)/config
	mkdir -p $(TUNECONFDIR)/scripts

install: install-dirs
	$(PYTHON) setup.py install -O1 --root $(DESTDIR) --prefix $(PREFIX)
	cp -r $(CURDIR)/config $(TUNECONFDIR)
	cp -r $(CURDIR)/scripts $(TUNECONFDIR)
	cp -r $(CURDIR)/src/knowledge_base $(TUNECONFDIR)
	cp $(CURDIR)/service/*.service $(SYSTEMDDIR)

clean:
	rm -rf $(PYTHON_SITELIB)/euler_copilot_tune-*-py*.egg/
	rm -rf $(TUNECONFDIR)
	rm -f $(SYSTEMDDIR)/tune-mcpserver.service
	rm -f $(SYSTEMDDIR)/tune-openapi.service
	rm -rf $(CURDIR)/{build,dist,euler_copilot_tune*.egg-info}

rpmbuild:
	mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	cd .. && tar -zcvf $(NAME)-$(VERSION).tar.gz $(CURDIR)
	mv ../$(NAME)-$(VERSION).tar.gz ~/rpmbuild/SOURCES
	rpmbuild -ba $(NAME).spec

startup:
	systemctl daemon-reload
	systemctl restart tune-mcpserver
	systemctl restart tune-openapi

run:
	PYTHONPATH="$(PYTHONPATH):`pwd`" $(VENV)/bin/python src/start_tune.py

# check: run
# 	cd ${CURDIR}/tests && sh run_tests.sh

authors:
	git shortlog --summary --numbered --email | grep -v openeuler-ci-bot | sed 's/<root@localhost.*//' | awk '{$$1=null;print $$0}' | sed 's/^[ ]*//g | grep -v '^$'' > AUTHORS

# Help target
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install       install euler-copilot in system"
	@echo "  test          run tests"
	@echo "  clean         clean euler-copilot build and installed files"
	@echo "  run           run euler copilot tune"

venv:
	@if [ ! -d "$(VENV)" ]; then $(PYTHON) -m venv $(VENV); fi
	@echo "Created virtualenv at $(VENV)"
	$(VENV)/bin/python -m pip install --upgrade pip setuptools wheel
	$(VENV)/bin/python -m pip install -r requirements.txt
	@echo "Dependencies installed."