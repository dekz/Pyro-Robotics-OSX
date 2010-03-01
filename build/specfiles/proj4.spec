# PROJ.4 RPM SPEC file

Summary: Cartographic Projections Library
Name: proj
Version: 4.5.0
Release: fc5
Group: Development/Libraries
License: MIT
URL: http://proj.maptools.org/
Source: ftp://ftp.remotesensing.org/proj/%{name}-%{version}.tgz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: proj <= %{version}
Provides: proj = %{version}-%{release}
Prefix: /usr/local

%description
PROJ.4 is in active use by GRASS GIS, MapServer, PostGIS, Thuban, OGDI
and OGRCoordinateTransformation as well as various other projects

%prep
%setup -q

%build

%configure

%install
make install

%clean
[ "%{buildroot}" != '/' ] && %{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/proj
%{_bindir}/nad2nad
%{_bindir}/nad2bin
%{_bindir}/geod
%{_bindir}/invgeod
%{_bindir}/cs2cs
%{_bindir}/invproj
%{_includedir}/projects.h
%{_includedir}/nad_list.h
%{_includedir}/proj_api.h
%{_includedir}/org_proj4_Projections.h
/usr/share/man/man1/geod.1
/usr/share/man/man1/nad2nad.1
/usr/share/man/man1/proj.1
/usr/share/man/man1/cs2cs.1
/usr/share/man/man3/pj_init.3
/usr/share/proj
