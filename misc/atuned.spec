# All right reserved by Huawei Co,Ltd

%define __global_requires_exclude_from  /usr/libexec
#%define  debug_package %{nil}

Summary: AI auto tunning system
Name: atune
Version: 0.0.1
Release: 1
Packager: Huawei-2012-Euler-atuned
Group: Development/System
License: GPL
BuildRequires: rpm-build
Requires: systemd
Source: %{name}-%{version}.tar.gz

%description
atune is a service for atuned AI tunning system.

%prep
%setup -q

%build
cd ../
mkdir -p gopath/src/
rm -rf gopath/src/%{name}
mv %{name}-%{version} gopath/src/%{name}
cd gopath/src/%{name}
make
cd ../
\cp -rf %{name} ../../%{name}-%{version}

%install
mkdir -p %{buildroot}/etc/atuned
mkdir -p %{buildroot}/usr/lib/atuned/modules
mkdir -p %{buildroot}/usr/share/atuned
mkdir -p %{buildroot}/usr/libexec/atuned/scripts
mkdir -p %{buildroot}/usr/libexec/atuned/analysis
mkdir -p %{buildroot}/usr/libexec/atuned/collector
mkdir -p %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_unitdir}/
mkdir -p %{buildroot}/var/lib/atuned
mkdir -p %{buildroot}/usr/share/bash-completion/completions

install -m 640 pkg/daemon_profile_server.so %{buildroot}/usr/lib/atuned/modules
install -m 750 pkg/atune-adm %{buildroot}%{_bindir}/
install -m 750 pkg/atuned %{buildroot}%{_bindir}/
install -m 640 misc/atuned.service %{buildroot}%{_unitdir}/
install -m 640 misc/atuned.cnf %{buildroot}/etc/atuned/
install -m 640 database/atuned.db %{buildroot}/var/lib/atuned/
install -m 640 misc/atune-adm %{buildroot}/usr/share/bash-completion/completions/
install -m 640 misc/atune.logo %{buildroot}/usr/share/atuned
\cp -rf scripts/* %{buildroot}/usr/libexec/atuned/scripts/
install -m 640 kmodules/prefetch_tunning_per_cpu/prefetch_tunning.ko %{buildroot}/usr/libexec/atuned/scripts/prefetch
chmod -R 750 %{buildroot}/usr/libexec/atuned/scripts/
\cp -rf analysis/* %{buildroot}/usr/libexec/atuned/analysis/
chmod -R 750 %{buildroot}/usr/libexec/atuned/analysis/
\cp -rf libexec/* %{buildroot}/usr/libexec/atuned/collector/
chmod -R 750 %{buildroot}/usr/libexec/atuned/collector/

%files
%defattr(0640,root,root,-)
%attr(0640,root,root) /usr/lib/atuned/modules/daemon_profile_server.so
%attr(0640,root,root) %{_unitdir}/atuned.service
%attr(0750,root,root) %{_bindir}/atune-adm
%attr(0750,root,root) %{_bindir}/atuned
%attr(0750,root,root) /usr/libexec/atuned/scripts/*
%attr(0750,root,root) /usr/libexec/atuned/analysis/*
%attr(0750,root,root) /usr/libexec/atuned/collector/*
%attr(0640,root,root) /usr/share/bash-completion/completions/atune-adm
%attr(0750,root,root) /var/lib/atuned/atuned.db
%attr(0750,root,root) %dir /usr/lib/atuned
%attr(0750,root,root) %dir /usr/lib/atuned/modules
%attr(0750,root,root) %dir /usr/libexec/atuned
%attr(0750,root,root) %dir /usr/libexec/atuned/scripts
%attr(0750,root,root) %dir /usr/libexec/atuned/analysis
%attr(0750,root,root) %dir /usr/libexec/atuned/collector
%attr(0750,root,root) %dir /usr/share/atuned
%attr(0640,root,root) /usr/share/atuned/atune.logo
%attr(0750,root,root) %dir /etc/atuned
%attr(0750,root,root) /etc/atuned/*

%post
%systemd_post atuned.service

%preun
%systemd_preun atuned.service

%postun
%systemd_postun_with_restart atuned.service

%changelog
* Mon Jul 01 2019 Qiangmin Lin <linqiangmin@huawei.com> 0.0.1
- Init atuned arch and code struct
* Mon Jul 01 2019 Jianhai Luan <luanjianhai@huawei.com> 0.0.1
* Mon Jul 01 2019 Xiaoguang Li <lixiaoguang2@huawei.com> 0.0.1
* Mon Jul 01 2019 Wei Li <liwei391@huawei.com> 0.0.1
- Init atuned
* Mon Jul 01 2019 Xiaotong Ji <jixiaotong1@huawei.com> 0.0.1
- Init aware for ML
* Mon Jul 01 2019 MingCong Song <songmingcong@huawei.com> 0.0.1
- Init DataSet Model
