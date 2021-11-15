%global with_strip 0
%define __global_requires_exclude_from  /usr/libexec

Summary: AI auto tuning system
Name: atune
Version: 1.0.0
Release: 1
License: Mulan PSL v2
URL: https://gitee.com/openeuler/A-Tune
Source: https://gitee.com/openeuler/A-Tune/repository/archive/v%{version}.tar.gz

BuildRequires: rpm-build golang-bin procps-ng
BuildRequires: sqlite >= 3.24.0 openssl
BuildRequires: python3-scikit-optimize python3-pandas python3-xgboost
BuildRequires: python3-pyyaml
Requires: systemd
Requires: atune-client
Requires: atune-db
Requires: python3-dict2xml
Requires: python3-flask-restful
Requires: python3-pandas
Requires: python3-pyyaml
%ifarch aarch64
Requires: prefetch_tuning
%endif
Requires: perf
Requires: sysstat
Requires: hwloc-gui
Requires: psmisc
Requires: atune-collector

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

%package engine
Summary: engine tool for auto tuning system
License: MuLan PSL v2
Requires: python3-scikit-optimize
Requires: python3-xgboost
Requires: python3-flask-restful
Requires: python3-pandas
Requires: python3-lhsmdu
Conflicts: atune < 0.3-0.3

%description engine
atune engine tool for manage atuned AI tuning system.

%prep
%autosetup -n A-Tune -p1

%build
%if %{with_strip}
export GOLDFLAGS="-s"
%endif
sed -i "s/^rest_tls.*/rest_tls = false/" misc/atuned.cnf
sed -i "s/^engine_tls.*/engine_tls = false/" misc/atuned.cnf
sed -i "s/^engine_tls.*/engine_tls = false/" misc/engine.cnf
make models
%make_build

%install
%make_install

%check

%files
%license License/LICENSE
%defattr(0640,root,root,-)
%attr(0640,root,root) /usr/lib/atuned/modules/daemon_profile_server.so
%attr(0640,root,root) %{_unitdir}/atuned.service
%attr(0750,root,root) %{_bindir}/atuned
%attr(0750,root,root) /usr/libexec/atuned/analysis/*
%attr(0640,root,root) /usr/lib/atuned/profiles/*
%exclude /usr/libexec/atuned/analysis/app_engine.py
%exclude /usr/libexec/atuned/analysis/models/
%exclude /usr/libexec/atuned/analysis/optimizer/
%exclude /usr/libexec/atuned/analysis/engine/
%exclude /usr/libexec/atuned/analysis/dataset/
%attr(0750,root,root) %dir /usr/lib/atuned
%attr(0750,root,root) %dir /usr/lib/atuned/modules
%attr(0750,root,root) %dir /usr/lib/atuned/profiles
%attr(0750,root,root) %dir /usr/libexec/atuned
%attr(0750,root,root) %dir /usr/libexec/atuned/analysis
%attr(0750,root,root) %dir /usr/share/atuned
%attr(0750,root,root) %dir /etc/atuned
%attr(0750,root,root) %dir /etc/atuned/rules
%attr(0750,root,root) %dir /var/atuned
%attr(0640,root,root) /etc/atuned/atuned.cnf
%exclude /etc/atuned/engine_certs/*
%exclude /etc/atuned/rest_certs/*

%files client
%attr(0750,root,root) %{_bindir}/atune-adm
%attr(0640,root,root) /usr/share/bash-completion/completions/atune-adm

%files db
%attr(0750,root,root) %dir /var/lib/atuned
%attr(0750,root,root) %dir /var/run/atuned
%attr(0750,root,root) /var/lib/atuned/atuned.db
%attr(0750,root,root) %dir /usr/libexec/atuned

%files engine
%license License/LICENSE
%defattr(0640,root,root,-)
%attr(0640,root,root) %{_unitdir}/atune-engine.service
%attr(0750,root,root) /usr/libexec/atuned/analysis/*
%attr(0750,root,root) /etc/atuned/*
%exclude /usr/libexec/atuned/analysis/app_rest.py
%exclude /usr/libexec/atuned/analysis/atuned/
%exclude /usr/libexec/atuned/analysis/dataset/
%attr(0750,root,root) %dir /usr/libexec/atuned/analysis
%attr(0750,root,root) %dir /etc/atuned
%exclude /etc/atuned/atuned.cnf
%exclude /etc/atuned/rules
%exclude /etc/atuned/engine_certs/*
%exclude /etc/atuned/rest_certs/*

%post
%systemd_post atuned.service

%preun
%systemd_preun atuned.service

%postun
%systemd_postun_with_restart atuned.service

%changelog
* Mon Nov 15 2021 hanxinke<hanxinke@huawei.com> - 1.0.0-1
- upgrade to v1.0.0

* Sat Dec 26 2020 gaoruoshu<gaoruoshu@huawei.com> - 0.3-0.3
- add security Go compile flags

* Sat Nov 28 2020 hanxinke<hanxinke@huawei.com> - 0.3-0.2
- The engine package conflicts with atune < 0.3-0.1.

* Fri Sep 4 2020 Zhipeng Xie<xiezhipeng1@huawei.com> - 0.3-0.1
- upgrade to v0.3

* Thu Mar 19 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.2-0.1
- Package init

* Tue Nov 12 2019 openEuler Buildteam <buildteam@openeuler.org> - 0.1-0.1
- Package init
