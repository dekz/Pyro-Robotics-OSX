# ODE RPM SPEC file

Summary: Open Dynamics Engine
Name: ode
Version: 0.5
Release: fc3
Group: Development/Libraries
License: LGPL or BSD-style
URL: http://ode.org/
Source: http://internap.dl.sourceforge.net/sourceforge/opende/%{name}-%{version}.tgz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: ode <= %{version}
Provides: ode = %{version}-%{release}
Prefix: /usr/local

%description
ODE is an open source, high performance library for simulating rigid
body dynamics. It is fully featured, stable, mature and platform
independent with an easy to use C/C++ API. It has advanced joint types
and integrated collision detection with friction. ODE is useful for
simulating vehicles, objects in virtual reality environments and
virtual creatures. It is currently used in many computer games, 3D
authoring tools and simulation tools.

%prep
%setup -q
%{__perl} -pi -e 's|\#OPCODE|OPCODE|' config/user-settings

%build
make configure
make ode-lib

%install
cp -r include/ode %{_includedir}
cp lib/libode.a %{_libdir}

%clean
[ "%{buildroot}" != '/' ] && %{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_libdir}/libode.a
%{_includedir}/ode/collision.h
%{_includedir}/ode/collision_space.h
%{_includedir}/ode/collision_trimesh.h
%{_includedir}/ode/common.h
%{_includedir}/ode/compatibility.h
%{_includedir}/ode/config.h
%{_includedir}/ode/contact.h
%{_includedir}/ode/error.h
%{_includedir}/ode/export-dif.h
%{_includedir}/ode/mass.h
%{_includedir}/ode/matrix.h
%{_includedir}/ode/memory.h
%{_includedir}/ode/misc.h
%{_includedir}/ode/objects.h
%{_includedir}/ode/ode.h
%{_includedir}/ode/odecpp.h
%{_includedir}/ode/odecpp_collision.h
%{_includedir}/ode/odecpp_old.h
%{_includedir}/ode/odemath.h
%{_includedir}/ode/rotation.h
%{_includedir}/ode/timer.h
