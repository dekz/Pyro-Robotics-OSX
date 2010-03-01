# Player

%define py_ver    %(python -c 'import sys;print(sys.version[0:3])')

Summary: Player robot interface
Name: player
Version: 1.6.4
Release: fc3
Group: Development/Libraries
License: GPL
URL: http://playerstage.sourceforge.net
Source: %{name}-%{version}.tgz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: player <= %{version}
Provides: player = %{version}-%{release}
Requires: gsl 
Prefix: /usr/local

%description 
Player robot interface

%prep
%setup -q -n player
./bootstrap

%build
%configure

%install
%makeinstall

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_libdir}/libplayerqueue.a
%{_libdir}/libplayerc.a
%{_libdir}/libplayercclient.a
%{_libdir}/libplayerpacket.a
%{_libdir}/pkgconfig/playerclient.pc
%{_libdir}/pkgconfig/player.pc
%{_libdir}/pkgconfig/libplayerc.pc
%{_libdir}/pkgconfig/playercclient.pc
%{_libdir}/python%{py_ver}/site-packages/_playerc.so
%{_libdir}/python%{py_ver}/site-packages/playerc.py
%{_libdir}/python%{py_ver}/site-packages/playerc.pyc
%{_libdir}/libplayerclient.a
%dir %{_includedir}/player
%{_includedir}/player/*
%{_includedir}/playerclient.h
%{_includedir}/player.h
%{_includedir}/stage1p3.h
%{_includedir}/playerqueue.h
%{_includedir}/jpeg.h
%{_includedir}/playercclient.h
%{_includedir}/playerpacket.h
%{_includedir}/playerc.h
%{_includedir}/playerconfig.h
%{_includedir}/playercommon.h
%{_includedir}/playermcomtypes.h
%dir %{_datadir}/player
%{_datadir}/player/*
%{_bindir}/playervcr
%{_bindir}/player
%{_bindir}/playerjoy
%{_bindir}/playerv
%{_bindir}/playerprint
%{_bindir}/playernav
%dir %{_prefix}/src/player
%{_prefix}/src/player/*
