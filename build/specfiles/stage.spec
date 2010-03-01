# Stage

%define py_ver    %(python -c 'import sys;print(sys.version[0:3])')

Summary: Stage, a 2D simulator
Name: stage
Version: 1.6.4
Release: fc3
Group: Development/Libraries
License: GPL
URL: http://playerstage.sourceforge.net
Source: %{name}-%{version}.tgz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: stage <= %{version}
Provides: stage = %{version}-%{release}
Requires: player
Prefix: /usr/local

%description 
Stage, a 2D simulator

%prep
%setup -q -n stage
./bootstrap

%build
%configure

%install
cd ./docsrc
make
cd ..
%makeinstall

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_libdir}/libstageplugin.a
%{_libdir}/libstage.so.1
%{_libdir}/libstage.so.1.0.0
%{_libdir}/libstage.a
%{_libdir}/libstageplugin.so
%{_libdir}/libstageplugin.la
%{_libdir}/pkgconfig/stage.pc
%{_libdir}/libstage.so
%{_libdir}/libstageplugin.so.1
%{_libdir}/libstageplugin.so.1.0.0
%{_libdir}/libstage.la
%{_includedir}/stage.h
%dir %{_datadir}/stage
%{_datadir}/stage/*
%{_bindir}/stest
%dir %{_prefix}/doc/stage_user
%{_prefix}/doc/stage_user/*
%dir %{_prefix}/doc/stage_reference
%{_prefix}/doc/stage_reference/*
