.PHONY: all clean modules

PKGPATH=pkg
CURDIR=$(shell pwd)
PREFIX    ?= /usr
LIBEXEC   ?= libexec
BINDIR     = $(DESTDIR)$(PREFIX)/bin
SYSTEMDDIR = $(DESTDIR)$(PREFIX)/lib/systemd/system

all: modules atune-adm atuned db

atune-adm:
	export GOPATH=`cd ../../;pwd` && go build -v -o $(PKGPATH)/atune-adm cmd/atune-adm/*.go

atuned:
	export GOPATH=`cd ../../;pwd` && go build -v -o $(PKGPATH)/atuned cmd/atuned/*.go

modules:
	export GOPATH=`cd ../../;pwd` && cd ${CURDIR}/modules/server/profile/ && go build -buildmode=plugin -o ${CURDIR}/pkg/daemon_profile_server.so *.go

clean:
	rm -rf $(PKGPATH)/*

db:
	sqlite3 database/atuned.db ".read database/init.sql"

install:
	@echo "BEGIN INSTALL A-Tune"
	mkdir -p $(BINDIR)
	mkdir -p $(SYSTEMDDIR)
	mkdir -p $(DESTDIR)/etc/atuned/tuning
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/modules
	mkdir -p $(DESTDIR)$(PREFIX)/share/atuned
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/collector
	mkdir -p $(DESTDIR)/var/lib/atuned
	mkdir -p $(DESTDIR)$(PREFIX)/share/bash-completion/completions
	install -m 640 pkg/daemon_profile_server.so $(DESTDIR)$(PREFIX)/lib/atuned/modules
	install -m 750 pkg/atune-adm $(BINDIR)
	install -m 750 pkg/atuned $(BINDIR)
	install -m 640 misc/atuned.service $(SYSTEMDDIR)
	install -m 640 misc/atuned.cnf $(DESTDIR)/etc/atuned/
	install -m 640 database/atuned.db $(DESTDIR)/var/lib/atuned/
	install -m 640 misc/atune-adm $(DESTDIR)$(PREFIX)/share/bash-completion/completions/
	install -m 640 misc/atune.logo $(DESTDIR)$(PREFIX)/share/atuned
	\cp -rf scripts/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts/
	\cp -rf analysis/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/
	\cp -rf collection/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/collector/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/collector/
	@echo "END INSTALL A-Tune"
