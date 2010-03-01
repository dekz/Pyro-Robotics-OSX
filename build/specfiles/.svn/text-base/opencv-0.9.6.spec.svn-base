# OpenCV

Summary: Open Computer Vision Project
Name: opencv
Version: 0.9.6
Release: fc3
Group: Development/Libraries
License: GPL
URL: http://playerstage.sourceforge.net
Source: %{name}-%{version}.tar.gz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: opencv <= %{version}
Provides: opencv = %{version}-%{release}
Prefix: /usr

%description 
Open Computer Vision Project

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
%dir %{_datadir}/opencv/
%{_datadir}/opencv/*
%{_libdir}/pkgconfig/opencv.pc
%{_libdir}/libcxcore.la
%{_libdir}/libcxcore.so
%{_libdir}/libcxcore.so.0
%{_libdir}/libcxcore.so.0.9.6
%{_libdir}/libhighgui.la
%{_libdir}/libhighgui.so
%{_libdir}/libhighgui.so.0
%{_libdir}/libhighgui.so.0.9.6
%{_libdir}/libcvaux.la
%{_libdir}/libcvaux.so
%{_libdir}/libcvaux.so.0
%{_libdir}/libcvaux.so.0.9.6
%{_libdir}/libcvhaartraining.a
%{_libdir}/libcv.la
%{_libdir}/libcv.so
%{_libdir}/libcv.so.0
%{_libdir}/libcv.so.0.9.6
