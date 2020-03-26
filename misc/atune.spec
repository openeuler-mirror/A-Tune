%define __global_requires_exclude_from  /usr/libexec

Summary: AI auto tuning system
Name: atune
Version: 0.2
Release: 0.1
License: Mulan PSL v2
URL: https://gitee.com/openeuler/A-Tune
Source: openeuler-A-Tune-v%{version}.tar.gz

BuildRequires: rpm-build protobuf-compiler golang-bin python3-pytest procps-ng
BuildRequires: sqlite >= 3.24.0
Requires: systemd
Requires: atune-client
Requires: atune-db
Requires: python3-dict2xml
Requires: python3-flask-restful
Requires: python3-pandas
Requires: python3-scikit-optimize
Requires: python3-xgboost
Requires: prefetch_tuning
Requires: perf
Requires: sysstat
Requires: hwloc-gui
Requires: psmisc

%define  debug_package %{nil}

%description
atune is a service for atuned AI tuning system.

%package client
Summary: client tool for auto tuning system
License: MuLan PSL v2

%description client
atune client tool for manage atuned AI tuning system.

%package db
Summary: database and AI model for auto tuning system
License: MuLan PSL v2

%description db
Database and AI model used by atuned AI tuning system.

%prep
%setup -n A-Tune -q

%build
cd ../
mkdir -p gopath/src/
rm -rf gopath/src/%{name}
mv A-Tune gopath/src/%{name}
cd gopath/src/%{name}
export GO111MODULE=off
make
cd ../
cp -rf %{name} ../../A-Tune

%install
%make_install

%check

%files
%license License/LICENSE
%defattr(0640,root,root,-)
%attr(0640,root,root) /usr/lib/atuned/modules/daemon_profile_server.so
%attr(0640,root,root) %{_unitdir}/atuned.service
%attr(0750,root,root) %{_bindir}/atuned
%attr(0750,root,root) /usr/libexec/atuned/scripts/*
%attr(0750,root,root) /usr/libexec/atuned/analysis/*
%exclude /usr/libexec/atuned/analysis/models/
%attr(0750,root,root) /usr/libexec/atuned/collector/*
%attr(0750,root,root) %dir /usr/lib/atuned
%attr(0750,root,root) %dir /usr/lib/atuned/modules
%attr(0750,root,root) %dir /usr/libexec/atuned
%attr(0750,root,root) %dir /usr/libexec/atuned/scripts
%attr(0750,root,root) %dir /usr/libexec/atuned/analysis
%attr(0750,root,root) %dir /usr/libexec/atuned/collector
%attr(0750,root,root) %dir /usr/share/atuned
%attr(0750,root,root) %dir /etc/atuned
%attr(0750,root,root) /etc/atuned/*

%files client
%attr(0750,root,root) %{_bindir}/atune-adm
%attr(0640,root,root) /usr/share/bash-completion/completions/atune-adm

%files db
%attr(0750,root,root) %dir /var/lib/atuned
%attr(0750,root,root) %dir /var/run/atuned
%attr(0750,root,root) /var/lib/atuned/atuned.db
%attr(0750,root,root) %dir /usr/libexec/atuned
%attr(0750,root,root) %dir /usr/libexec/atuned/analysis
%attr(0750,root,root) %dir /usr/libexec/atuned/analysis/models
%attr(0750,root,root) /usr/libexec/atuned/analysis/models/*

%post
%systemd_post atuned.service

%preun
%systemd_preun atuned.service

%postun
%systemd_postun_with_restart atuned.service

%changelog
* Thu Mar 19 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.2-0.1
- Package init

* Tue Nov 12 2019 openEuler Buildteam <buildteam@openeuler.org> - 0.1-0.1
- Package init
