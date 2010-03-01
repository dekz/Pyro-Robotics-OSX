%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.4)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: robotics protocols
Name: player
Version: 2.0.3
Release: fc6
License: GPL
Group: Development/Libraries
URL: http://playerstage.sf.net/
Packager: D.S. Blank <dblank@dblank@cs.brynmawr.edu>
Obsoletes: player < %{version}
Provides: player = %{version}-%{release}
Source0: %{name}-%{version}.tgz
BuildRequires: ode ode-devel gsl freeglut-devel wxPythonGTK2 libtool-ltdl-devel
Requires: ode gsl wxPythonGTK2

%description
Player robot protocols

%prep
%setup -q 

%build
ln -b -s /usr/lib/libltdl.so.3 /usr/lib/libltdl.so
mkdir -p /usr/X11R6/lib/X11
ln -b -s /usr/share/X11/rgb.txt /usr/X11R6/lib/X11/rgb.txt
%configure

%install
%makeinstall

%clean

%files
%defattr(-,root,root,-)
%{_libdir}/python%{pythonver}/site-packages/playerc.py
%{_libdir}/python%{pythonver}/site-packages/playerc.pyc
#%{_libdir}/python%{pythonver}/site-packages/playerc.pyo
%{_libdir}/python%{pythonver}/site-packages/_playerc.so
%{_bindir}/player
%{_bindir}/playercam
%{_bindir}/playerjoy
%{_bindir}/playernav
%{_bindir}/playerprint
%{_bindir}/playerv
%{_bindir}/playervcr
%{_bindir}/playerwritemap
%{_bindir}/playerxdrgen.py
#%{_bindir}/playerxdrgen.pyc
#%{_bindir}/playerxdrgen.pyo
%{_includedir}/player-2.0/
%{_libdir}/libplayerc.a
%{_libdir}/libplayerc++.a
%{_libdir}/libplayerc.la
%{_libdir}/libplayerc++.la
%{_libdir}/libplayercore.a
%{_libdir}/libplayercore.la
%{_libdir}/libplayercore.so
%{_libdir}/libplayercore.so.2
%{_libdir}/libplayercore.so.2.0.3
%{_libdir}/libplayerc.so
%{_libdir}/libplayerc++.so
%{_libdir}/libplayerc.so.2
%{_libdir}/libplayerc++.so.2
%{_libdir}/libplayerc.so.2.0.3
%{_libdir}/libplayerc++.so.2.0.3
%{_libdir}/libplayerdrivers.a
%{_libdir}/libplayerdrivers.la
%{_libdir}/libplayerdrivers.so
%{_libdir}/libplayerdrivers.so.2
%{_libdir}/libplayerdrivers.so.2.0.3
%{_libdir}/libplayererror.a
%{_libdir}/libplayererror.la
%{_libdir}/libplayererror.so
%{_libdir}/libplayererror.so.2
%{_libdir}/libplayererror.so.2.0.3
%{_libdir}/libplayerjpeg.a
%{_libdir}/libplayerjpeg.la
%{_libdir}/libplayerjpeg.so
%{_libdir}/libplayerjpeg.so.2
%{_libdir}/libplayerjpeg.so.2.0.3
%{_libdir}/libplayertcp.a
%{_libdir}/libplayertcp.la
%{_libdir}/libplayertcp.so
%{_libdir}/libplayertcp.so.2
%{_libdir}/libplayertcp.so.2.0.3
%{_libdir}/libplayerxdr.a
%{_libdir}/libplayerxdr.la
%{_libdir}/libplayerxdr.so
%{_libdir}/libplayerxdr.so.2
%{_libdir}/libplayerxdr.so.2.0.3
%{_libdir}/pkgconfig/playercore.pc
%{_libdir}/pkgconfig/playerc.pc
%{_libdir}/pkgconfig/playerc++.pc
%{_libdir}/pkgconfig/playerdrivers.pc
%{_libdir}/pkgconfig/playererror.pc
%{_libdir}/pkgconfig/playertcp.pc
%{_libdir}/pkgconfig/playerxdr.pc
%{_datadir}/player/

%changelog
* Mon May 15 2006 Douglas S. Blank <dblank@brynmawr.edu> - 2-1
- Initial build.

