VERSION = 1.0.0
.PHONY: all clean modules

PKGPATH=pkg
CURDIR=$(shell pwd)
PYDIR=$(shell which python3)
PREFIX    ?= /usr
LIBEXEC   ?= libexec
BINDIR     = $(DESTDIR)$(PREFIX)/bin
SYSTEMDDIR = $(DESTDIR)$(PREFIX)/lib/systemd/system
SRCVERSION = $(shell git rev-parse --short HEAD 2>/dev/null)
ATUNEVERSION = $(VERSION)$(if $(SRCVERSION),($(SRCVERSION)))
SHELL = /bin/bash

GOLDFLAGS += -X gitee.com/openeuler/A-Tune/common/config.Version=$(ATUNEVERSION)
GOFLAGS = -ldflags '-s -w -extldflags "-static" -extldflags "-zrelro" -extldflags "-znow" -extldflags "-ftrapv" $(GOLDFLAGS)'

CERT_PATH=$(DESTDIR)/etc/atuned
GRPC_CERT_PATH=$(CERT_PATH)/grpc_certs
REST_CERT_PATH=$(CERT_PATH)/rest_certs
ENGINE_CERT_PATH=$(CERT_PATH)/engine_certs
REST_IP_ADDR=localhost
ENGINE_IP_ADDR=localhost

all: abs-python modules atune-adm atuned db

abs-python:
	@if [ $(PYDIR) ] ; then \
		sed -i "s?ExecStart=python3?ExecStart=$(PYDIR)?g" $(CURDIR)/misc/atune-engine.service; \
	else \
		echo "no python3 exists."; \
	fi

atune-adm:
	go build -mod=vendor -v $(GOFLAGS) -o $(PKGPATH)/atune-adm cmd/atune-adm/*.go

atuned:
	go build -mod=vendor -v $(GOFLAGS) -o $(PKGPATH)/atuned cmd/atuned/*.go

modules:
	cd ${CURDIR}/modules/server/profile/ && go build -mod=vendor -v $(GOFLAGS) -buildmode=plugin -o ${CURDIR}/pkg/daemon_profile_server.so *.go

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

install: libinstall models restcerts enginecerts yaml-generator autoconfig

collector-install:
	@echo "BEGIN INSTALL A-Tune-Collector..."
	! pip3 show atune-collector || pip3 uninstall atune-collector -y
	rm -rf collector
	git clone https://gitee.com/openeuler/A-Tune-Collector.git collector
	cd collector && python3 setup.py install
	@echo "END INSTALL A-Tune-Collector..."

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
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/modules
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/profiles
	mkdir -p $(DESTDIR)$(PREFIX)/lib/atuned/training
	mkdir -p $(DESTDIR)$(PREFIX)/share/atuned
	mkdir -p $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/models
	mkdir -p $(DESTDIR)/var/lib/atuned
	mkdir -p $(DESTDIR)/var/run/atuned
	mkdir -p $(DESTDIR)/var/atuned
	mkdir -p $(DESTDIR)$(PREFIX)/share/bash-completion/completions
	install -m 640 pkg/daemon_profile_server.so $(DESTDIR)$(PREFIX)/lib/atuned/modules
	install -m 750 pkg/atune-adm $(BINDIR)
	install -m 750 pkg/atuned $(BINDIR)
	install -m 640 misc/atuned.service $(SYSTEMDDIR)
	install -m 640 misc/atuned.cnf $(DESTDIR)/etc/atuned/
	install -m 640 misc/engine.cnf $(DESTDIR)/etc/atuned/
	install -m 640 misc/ui.cnf $(DESTDIR)/etc/atuned/
	install -m 640 rules/tuning/tuning_rules.grl $(DESTDIR)/etc/atuned/rules
	install -m 640 misc/atune-engine.service $(SYSTEMDDIR)
	install -m 640 database/atuned.db $(DESTDIR)/var/lib/atuned/
	install -m 640 misc/atune-adm $(DESTDIR)$(PREFIX)/share/bash-completion/completions/
	install -m 640 misc/atune-ui.service $(SYSTEMDDIR)
	\cp -rf analysis/* $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/
	chmod -R 750 $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/
	\cp -rf profiles/* $(DESTDIR)$(PREFIX)/lib/atuned/profiles/
	chmod -R 750 $(DESTDIR)$(PREFIX)/lib/atuned/profiles/
	@echo "END INSTALL A-Tune"

autoconfig:
	@echo "START UPDATE ATUNED CONFIG..."
	@sh scripts/update_atuned_config.sh
	@echo "END UPDATE ATUNED CONFIG"

rpm:
	cd .. && tar -zcvf v$(VERSION).tar.gz A-Tune
	mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	mv ../v$(VERSION).tar.gz ~/rpmbuild/SOURCES
	rpmbuild -ba misc/atune.spec

models:
	cd ${CURDIR}/tools/ && python3 generate_models.py --model_path $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/models 

search:
	cd ${CURDIR}/tools/ && python3 generate_models.py --search=True --model_path $(DESTDIR)$(PREFIX)/$(LIBEXEC)/atuned/analysis/models

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
	cp /etc/pki/tls/openssl.cnf $(REST_CERT_PATH)
	@if test $(REST_IP_ADDR) == localhost; then \
		echo "[SAN]\nsubjectAltName=DNS:$(REST_IP_ADDR)" >> $(REST_CERT_PATH)/openssl.cnf; \
		echo "subjectAltName=DNS:$(REST_IP_ADDR)" > $(REST_CERT_PATH)/extfile.cnf; \
	else \
		echo "[SAN]\nsubjectAltName=IP:$(REST_IP_ADDR)" >> $(REST_CERT_PATH)/openssl.cnf; \
		echo "subjectAltName=IP:$(REST_IP_ADDR)" > $(REST_CERT_PATH)/extfile.cnf; \
	fi
	openssl req -new -subj "/CN=$(REST_IP_ADDR)" -config $(REST_CERT_PATH)/openssl.cnf \
		-key $(REST_CERT_PATH)/server.key -out $(REST_CERT_PATH)/server.csr
	openssl x509 -req -sha256 -CA $(REST_CERT_PATH)/ca.crt -CAkey $(REST_CERT_PATH)/ca.key -CAcreateserial -days 3650 \
		-extfile $(REST_CERT_PATH)/extfile.cnf -in $(REST_CERT_PATH)/server.csr -out $(REST_CERT_PATH)/server.crt
	rm -rf $(REST_CERT_PATH)/*.srl $(REST_CERT_PATH)/*.csr $(REST_CERT_PATH)/*.cnf
	@echo "END GENERATE REST CERTS"

enginecerts:
	@echo "BEGIN GENERATE ENGINE CERTS..."
	mkdir -p $(ENGINE_CERT_PATH)
	@if test ! -f $(ENGINE_CERT_PATH)/ca.key; then \
		openssl genrsa -out $(ENGINE_CERT_PATH)/ca.key 2048; \
		openssl req -new -x509 -days 3650 -subj "/CN=ca" -key $(ENGINE_CERT_PATH)/ca.key -out $(ENGINE_CERT_PATH)/ca.crt; \
	fi
	cp /etc/pki/tls/openssl.cnf $(ENGINE_CERT_PATH)
	@if test $(ENGINE_IP_ADDR) == localhost; then \
		echo "[SAN]\nsubjectAltName=DNS:$(ENGINE_IP_ADDR)" >> $(ENGINE_CERT_PATH)/openssl.cnf; \
		echo "subjectAltName=DNS:$(ENGINE_IP_ADDR)" > $(ENGINE_CERT_PATH)/extfile.cnf; \
	else \
		echo "[SAN]\nsubjectAltName=IP:$(ENGINE_IP_ADDR)" >> $(ENGINE_CERT_PATH)/openssl.cnf; \
		echo "subjectAltName=IP:$(ENGINE_IP_ADDR)" > $(ENGINE_CERT_PATH)/extfile.cnf; \
	fi
	@for name in server client; do \
		openssl genrsa -out $(ENGINE_CERT_PATH)/$$name.key 2048; \
		openssl req -new -subj "/CN=$(ENGINE_IP_ADDR)" -config $(ENGINE_CERT_PATH)/openssl.cnf \
			-key $(ENGINE_CERT_PATH)/$$name.key -out $(ENGINE_CERT_PATH)/$$name.csr; \
		openssl x509 -req -sha256 -CA $(ENGINE_CERT_PATH)/ca.crt -CAkey $(ENGINE_CERT_PATH)/ca.key -CAcreateserial -days 3650 \
			-extfile $(ENGINE_CERT_PATH)/extfile.cnf -in $(ENGINE_CERT_PATH)/$$name.csr -out $(ENGINE_CERT_PATH)/$$name.crt; \
	done
	rm -rf $(ENGINE_CERT_PATH)/*.srl $(ENGINE_CERT_PATH)/*.csr $(ENGINE_CERT_PATH)/*.cnf
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
	systemctl restart atune-ui

yaml-generator:
	\cp -rf tuning/yamls/* $(DESTDIR)/etc/atuned/tuning
	chmod -R 750 $(DESTDIR)/etc/atuned/tuning
	cd ${CURDIR}/tools/ && python3 generate_tuning_file.py -d $(DESTDIR)/etc/atuned/tuning

run: all collector-install install startup

check: run
	cd ${CURDIR}/tests && sh run_tests.sh

authors:
	git shortlog --summary --numbered --email|grep -v openeuler-ci-bot|sed 's/<root@localhost.*//'| awk '{$$1=null;print $$0}'|sed 's/^[ ]*//g' > AUTHORS
