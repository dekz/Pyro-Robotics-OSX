# lib3ds

Summary: lib3ds
Name: lib3ds
Version: 1.2.0
Release: fc5
Group: Development/Libraries
License: GPL
URL: http://playerstage.sourceforge.net
Source: %{name}-%{version}.tgz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: lib3ds <= %{version}
Provides: lib3ds = %{version}-%{release}
Prefix: /usr

%description 
lib3ds

%build
%configure

%prep
%setup -q

%install
%makeinstall

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_libdir}/lib3ds.a
%dir %{_includedir}/lib3ds
%{_includedir}/lib3ds/*
%{_bindir}/3dsdump
%{_bindir}/3ds2m
%{_mandir}/man1//3dsdump.1
%{_mandir}/man1/3ds2m.1
%{_bindir}/lib3ds-config
%{_mandir}/man1/lib3ds-config.1
%{_datadir}/aclocal/lib3ds.m4
