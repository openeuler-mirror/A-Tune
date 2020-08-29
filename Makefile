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

CERT_PATH=/etc/atuned
GRPC_CERT_PATH=$(CERT_PATH)/grpc_certs
REST_CERT_PATH=$(CERT_PATH)/rest_certs
ENGINE_CERT_PATH=$(CERT_PATH)/engine_certs
REST_IP_ADDR=localhost
ENGINE_IP_ADDR=localhost

all: modules atune-adm atuned db

atune-adm:
	go build -mod=vendor -v $(GOFLAGS) -o $(PKGPATH)/atune-adm cmd/atune-adm/*.go

atuned:
	go build -mod=vendor -v $(GOFLAGS) -o $(PKGPATH)/atuned cmd/atuned/*.go

modules:
	cd ${CURDIR}/modules/server/profile/ && go build -mod=vendor -buildmode=plugin -o ${CURDIR}/pkg/daemon_profile_server.so *.go

clean:
	rm -rf $(PKGPATH)/*

cleanall: clean
	rm -rf $(DESTDIR)/etc/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/lib/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/share/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/
	rm -rf $(DESTDIR)/var/lib/atuned/
	rm -rf $(DESTDIR)/var/run/atuned/
	rm -rf $(DESTDIR)/var/atuned/

db:
	sqlite3 database/atuned.db ".read database/init.sql"

install: libinstall restcerts enginecerts

libinstall:
	@echo "BEGIN INSTALL A-Tune..."
	mkdir -p $(BINDIR)
	mkdir -p $(SYSTEMDDIR)
	rm -rf $(DESTDIR)/etc/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/lib/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/share/atuned/
	rm -rf $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/
	rm -rf $(DESTDIR)/var/lib/atuned/
	rm -rf $(DESTDIR)/var/run/atuned/
	rm -rf $(DESTDIR)/var/atuned/
	mkdir -p $(DESTDIR)/etc/atuned/tuning
	mkdir -p $(DESTDIR)/etc/atuned/rules
	mkdir -p $(DESTDIR)/etc/atuned/training
	mkdir -p $(DESTDIR)/etc/atuned/classification
	mkdir -p $(DESTDIR)/etc/atuned/webserver
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/modules
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/profiles
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/training
	mkdir -p $(DESTDIR)$(PREFIX)/share/atuned
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/resources
	mkdir -p $(DESTDIR)/var/lib/atuned
	mkdir -p $(DESTDIR)/var/run/atuned
	mkdir -p $(DESTDIR)/var/atuned
	mkdir -p $(DESTDIR)$(PREFIX)/share/bash-completion/completions
	install -m 640 pkg/daemon_profile_server.so $(DESTDIR)$(PREFIX)/lib/atuned/modules
	install -m 750 pkg/atune-adm $(BINDIR)
	install -m 750 pkg/atuned $(BINDIR)
	install -m 640 misc/atuned.service $(SYSTEMDDIR)
	install -m 640 misc/atuned.cnf $(DESTDIR)/etc/atuned/
	install -m 640 rules/tuning/tuning_rules.grl $(DESTDIR)/etc/atuned/rules
	install -m 640 misc/atune-engine.service $(SYSTEMDDIR)
	install -m 640 database/atuned.db $(DESTDIR)/var/lib/atuned/
	install -m 640 misc/atune-adm $(DESTDIR)$(PREFIX)/share/bash-completion/completions/
	\cp -rf scripts/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/scripts/
	\cp -rf analysis/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/
	\cp -rf resources/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/resources/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/resources/
	\cp -rf profiles/* $(DESTDIR)$(PREFIX)/lib/atuned/profiles/
	chmod -R 640 $(DESTDIR)$(PREFIX)/lib/atuned/profiles/
	@echo "END INSTALL A-Tune"

rpm:
	cd .. && tar -zcvf openeuler-A-Tune-v$(VERSION).tar.gz A-Tune
	mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	mv ../openeuler-A-Tune-v$(VERSION).tar.gz ~/rpmbuild/SOURCES
	rpmbuild -ba misc/atune.spec

models:
	rm -rf ${CURDIR}/analysis/models/*
	cd ${CURDIR}/tools/ && python3 generate_models.py

grpccerts:
	@echo "BEGIN GENERATE GRPC CERTS..."
	mkdir -p $(GRPC_CERT_PATH)
	openssl genrsa -out $(GRPC_CERT_PATH)/ca.key 2048
	openssl req -new -x509 -days 3650 -subj "/CN=ca" -key $(GRPC_CERT_PATH)/ca.key -out $(GRPC_CERT_PATH)/ca.crt
	@for name in server client; do \
		openssl genrsa -out $(GRPC_CERT_PATH)/$$name.key 2048; \
		openssl req -new -subj "/CN=$$name" -key $(GRPC_CERT_PATH)/$$name.key -out $(GRPC_CERT_PATH)/$$name.csr; \
		openssl x509 -req -sha256 -CA $(GRPC_CERT_PATH)/ca.crt -CAkey $(GRPC_CERT_PATH)/ca.key -CAcreateserial -days 3650 \
			-in $(GRPC_CERT_PATH)/$$name.csr -out $(GRPC_CERT_PATH)/$$name.crt; \
	done
	rm -rf $(GRPC_CERT_PATH)/*.srl $(GRPC_CERT_PATH)/*.csr
	@echo "END GENERATE GRPC CERTS"

restcerts:
	@echo "BEGIN GENERATE REST CERTS..."
	mkdir -p $(REST_CERT_PATH)
	openssl genrsa -out $(REST_CERT_PATH)/ca.key 2048
	openssl req -new -x509 -days 3650 -subj "/CN=ca" -key $(REST_CERT_PATH)/ca.key -out $(REST_CERT_PATH)/ca.crt
	openssl genrsa -out $(REST_CERT_PATH)/server.key 2048
	@if test $(REST_IP_ADDR) == localhost; then \
		openssl req -new -subj "/CN=localhost" -key $(REST_CERT_PATH)/server.key -out $(REST_CERT_PATH)/server.csr; \
		openssl x509 -req -sha256 -CA $(REST_CERT_PATH)/ca.crt -CAkey $(REST_CERT_PATH)/ca.key -CAcreateserial -days 3650 \
			-in $(REST_CERT_PATH)/server.csr -out $(REST_CERT_PATH)/server.crt; \
	else \
		openssl req -new -subj "/CN=$(REST_IP_ADDR)" -key $(REST_CERT_PATH)/server.key -out $(REST_CERT_PATH)/server.csr; \
		echo "subjectAltName=IP:$(REST_IP_ADDR)" > $(REST_CERT_PATH)/extfile.cnf; \
		openssl x509 -req -sha256 -CA $(REST_CERT_PATH)/ca.crt -CAkey $(REST_CERT_PATH)/ca.key -CAcreateserial -days 3650 \
			-extfile $(REST_CERT_PATH)/extfile.cnf -in $(REST_CERT_PATH)/server.csr -out $(REST_CERT_PATH)/server.crt; \
	fi
	rm -rf $(REST_CERT_PATH)/*.srl $(REST_CERT_PATH)/*.csr $(REST_CERT_PATH)/extfile.cnf
	@echo "END GENERATE REST CERTS"

enginecerts:
	@echo "BEGIN GENERATE ENGINE CERTS..."
	mkdir -p $(ENGINE_CERT_PATH)
	@if test ! -f $(ENGINE_CERT_PATH)/ca.key; then \
		openssl genrsa -out $(ENGINE_CERT_PATH)/ca.key 2048; \
		openssl req -new -x509 -days 3650 -subj "/CN=ca" -key $(ENGINE_CERT_PATH)/ca.key -out $(ENGINE_CERT_PATH)/ca.crt; \
	fi
	@for name in server client; do \
		openssl genrsa -out $(ENGINE_CERT_PATH)/$$name.key 2048; \
		if test $(ENGINE_IP_ADDR) == localhost; then \
			openssl req -new -subj "/CN=localhost" -key $(ENGINE_CERT_PATH)/$$name.key -out $(ENGINE_CERT_PATH)/$$name.csr; \
			openssl x509 -req -sha256 -CA $(ENGINE_CERT_PATH)/ca.crt -CAkey $(ENGINE_CERT_PATH)/ca.key -CAcreateserial -days 3650 \
				-in $(ENGINE_CERT_PATH)/$$name.csr -out $(ENGINE_CERT_PATH)/$$name.crt; \
		else \
			openssl req -new -subj "/CN=$(ENGINE_IP_ADDR)" -key $(ENGINE_CERT_PATH)/$$name.key -out $(ENGINE_CERT_PATH)/$$name.csr; \
			echo "subjectAltName=IP:$(ENGINE_IP_ADDR)" > $(ENGINE_CERT_PATH)/extfile.cnf; \
			openssl x509 -req -sha256 -CA $(ENGINE_CERT_PATH)/ca.crt -CAkey $(ENGINE_CERT_PATH)/ca.key -CAcreateserial -days 3650 \
				-extfile $(ENGINE_CERT_PATH)/extfile.cnf -in $(ENGINE_CERT_PATH)/$$name.csr -out $(ENGINE_CERT_PATH)/$$name.crt; \
		fi; \
	done
	rm -rf $(ENGINE_CERT_PATH)/*.srl $(ENGINE_CERT_PATH)/*.csr $(ENGINE_CERT_PATH)/extfile.cnf
	@echo "END GENERATE ENGINE CERTS"

env:
	@echo "BEGIN SET ENVIRONMENT VARIABLES..."
	@echo "export ATUNED_TLS=yes" > $(GRPC_CERT_PATH)/env
	@echo "export ATUNED_CACERT=$(GRPC_CERT_PATH)/ca.crt" >> $(CERT_PATH)/env
	@echo "export ATUNED_CLIENTCERT=$(GRPC_CERT_PATH)/client.crt" >> $(CERT_PATH)/env
	@echo "export ATUNED_CLIENTKEY=$(GRPC_CERT_PATH)/client.key" >> $(CERT_PATH)/env
	@echo "export ATUNED_SERVERCN=server" >> $(CERT_PATH)/env
	@echo "END SET ENVIRONMENT VARIABLES"

startup:
	systemctl daemon-reload
	systemctl restart atuned
	systemctl restart atune-engine

run: all install startup
