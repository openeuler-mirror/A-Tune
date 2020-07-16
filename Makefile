VERSION = 0.2
.PHONY: all clean modules

PKGPATH=pkg
CURDIR=$(shell pwd)
PREFIX    ?= /usr
LIBEXEC   ?= libexec
BINDIR     = $(DESTDIR)$(PREFIX)/bin
SYSTEMDDIR = $(DESTDIR)$(PREFIX)/lib/systemd/system
SRCVERSION = $(shell git rev-parse --short HEAD 2>/dev/null)
ATUNEVERSION = $(VERSION)$(if $(SRCVERSION),($(SRCVERSION)))

GOLDFLAGS += -X gitee.com/openeuler/A-Tune/common/config.Version=$(ATUNEVERSION)
GOFLAGS = -ldflags "$(GOLDFLAGS)"

all: modules atune-adm atuned db

atune-adm:
	go build -mod=vendor -v $(GOFLAGS) -o $(PKGPATH)/atune-adm cmd/atune-adm/*.go

atuned:
	go build -mod=vendor -v $(GOFLAGS) -o $(PKGPATH)/atuned cmd/atuned/*.go

modules:
	cd ${CURDIR}/modules/server/profile/ && go build -mod=vendor -buildmode=plugin -o ${CURDIR}/pkg/daemon_profile_server.so *.go

clean:
	rm -rf $(PKGPATH)/*

db:
	sqlite3 database/atuned.db ".read database/init.sql"

install:
	@echo "BEGIN INSTALL A-Tune"
	mkdir -p $(BINDIR)
	mkdir -p $(SYSTEMDDIR)
	rm -rf $(DESTDIR)/etc/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/lib/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/share/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/
	rm -rf $(DESTDIR)/var/lib/atuned/
	rm -rf $(DESTDIR)/var/run/atuned/
	mkdir -p $(DESTDIR)/etc/atuned/tuning
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/modules
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/profiles
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/training
	mkdir -p $(DESTDIR)$(PREFIX)/share/atuned
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/collector
	mkdir -p $(DESTDIR)/var/lib/atuned
	mkdir -p $(DESTDIR)/var/run/atuned
	mkdir -p $(DESTDIR)$(PREFIX)/share/bash-completion/completions
	install -m 640 pkg/daemon_profile_server.so $(DESTDIR)$(PREFIX)/lib/atuned/modules
	install -m 750 pkg/atune-adm $(BINDIR)
	install -m 750 pkg/atuned $(BINDIR)
	install -m 640 misc/atuned.service $(SYSTEMDDIR)
	install -m 640 misc/atuned.cnf $(DESTDIR)/etc/atuned/
	install -m 640 misc/atune-engine.service $(SYSTEMDDIR)
	install -m 640 database/atuned.db $(DESTDIR)/var/lib/atuned/
	install -m 640 misc/atune-adm $(DESTDIR)$(PREFIX)/share/bash-completion/completions/
	\cp -rf scripts/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts/
	\cp -rf analysis/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/
	\cp -rf collection/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/collector/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/collector/
	\cp -rf profiles/* $(DESTDIR)$(PREFIX)/lib/atuned/profiles/
	chmod -R 640 $(DESTDIR)$(PREFIX)/lib/atuned/profiles/
	@echo "END INSTALL A-Tune"

rpm:
	git archive --format=tar --prefix=A-Tune/ HEAD | gzip -9 > openeuler-A-Tune-v$(VERSION).tar.gz
	mv openeuler-A-Tune-v$(VERSION).tar.gz ~/rpmbuild/SOURCES
	rpmbuild -ba misc/atune.spec
