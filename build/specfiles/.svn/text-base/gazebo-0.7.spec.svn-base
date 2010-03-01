# Gazebo
%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.4)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: Gazebo 3D Simulator
Name: gazebo
Version: 0.7.0
Release: fc6
Group: Development/Libraries
License: GPL
URL: http://playerstage.sourceforge.net
Source: %{name}-%{version}.tgz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: gazebo < %{version}
Provides: gazebo = %{version}-%{release}
Requires: ode gsl freeglut-devel wxPythonGTK2
Prefix: /usr

%description 
Gazebo 3D simulator

%build

%configure

%prep
%setup -q 

%install
%makeinstall

%clean

%files
%defattr(-,root,root)
%{_bindir}/gazebo
%{_bindir}/wxgazebo
%{_libdir}/libgazebo.a
%{_libdir}/libgazeboserver.a
%{_libdir}/pkgconfig/gazebo.pc
%{pythondir}/_gazebo.so
%{pythondir}/gazebo.py
%{pythondir}/gazebo.pyc
%{pythondir}/wxgazebo
%dir %{_datadir}/gazebo
%{_datadir}/gazebo/*
%dir %{_includedir}/gazebo
%{_includedir}/gazebo/*
%{_includedir}/gazebo.h
%dir %{_prefix}/src/gazebo
%{_prefix}/src/gazebo/*
