%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.4)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: 2d robotics simulator
Name: stage
Version: 2.0.3
Release: fc6
License: GPL
Group: Development/Libraries
URL: http://playerstage.sf.net/
Packager: D.S. Blank <dblank@dblank@cs.brynmawr.edu>
Obsoletes: stage < %{version}
Provides: stage = %{version}-%{release}
BuildRequires: player
Requires: player
Source0: %{name}-%{version}.tgz

%description
Stage robot simulator

%prep
%setup -q 
#./bootstrap

%build
%configure

%install
%makeinstall

%clean

%files
%defattr(-,root,root,-)
%{_bindir}/stest
%{_includedir}/stage.h
%{_libdir}/libstage.a
%{_libdir}/libstage.la
%{_libdir}/libstage.so
%{_libdir}/libstage.so.2
%{_libdir}/libstage.so.2.0.0
%{_libdir}/libstageplugin.a
%{_libdir}/libstageplugin.la
%{_libdir}/libstageplugin.so
%{_libdir}/libstageplugin.so.1
%{_libdir}/libstageplugin.so.1.0.0
%{_libdir}/pkgconfig/stage.pc
%{_datadir}/stage/worlds/autolab.cfg
%{_datadir}/stage/worlds/autolab.world
%{_datadir}/stage/worlds/beacons.inc
%{_datadir}/stage/worlds/bitmaps/autolab.png
%{_datadir}/stage/worlds/bitmaps/cave.png
%{_datadir}/stage/worlds/bitmaps/ghost.png
%{_datadir}/stage/worlds/bitmaps/hospital.png
%{_datadir}/stage/worlds/bitmaps/hospital_section.png
%{_datadir}/stage/worlds/bitmaps/rink.png
%{_datadir}/stage/worlds/bitmaps/sal2.png
%{_datadir}/stage/worlds/bitmaps/simple_rooms.png
%{_datadir}/stage/worlds/bitmaps/space_invader.png
%{_datadir}/stage/worlds/bitmaps/submarine.png
%{_datadir}/stage/worlds/bitmaps/table.png
%{_datadir}/stage/worlds/chatterbox.inc
%{_datadir}/stage/worlds/everything.cfg
%{_datadir}/stage/worlds/everything.world
%{_datadir}/stage/worlds/map.inc
%{_datadir}/stage/worlds/pioneer.inc
%{_datadir}/stage/worlds/pucktarget.inc
%{_datadir}/stage/worlds/sick.inc
%{_datadir}/stage/worlds/simple.cfg
%{_datadir}/stage/worlds/simple.world
%{_datadir}/stage/worlds/vfh.cfg
%{_datadir}/stage/worlds/wavefront.cfg

%changelog
* Mon May 15 2006 Douglas S. Blank <dblank@brynmawr.edu> - 2-1
- Initial build.

