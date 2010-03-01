%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.3)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: Numeric library for Python
Name: numpy
Version: 0.9.8
Release: fc5
Group: Development/Libraries
License: BSD
URL: http://numpy.org/
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: numpy <= %{version}
Requires: python, lapack, lapack-devel, atlas, atlas-devel
Provides: numpy = %{version}-%{release}
Prefix: /usr/local

%description
Numerical Python adds a fast array facility to the Python language.

%install
tar xfz ../SOURCES/%{name}-%{version}.tar.gz
cd %{name}-%{version}
python setup.py install

%clean
[ "%{buildroot}" != '/' ] && %{__rm} -rf /usr/src/redhat/BUILD/%{name}-%{version}

%files
%defattr(-,root,root)
%{pythondir}/%{name}
