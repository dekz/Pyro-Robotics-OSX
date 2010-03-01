%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.3)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: Scientific Tools for Python
Name: python-scipy
Version: 0.4.9
Release: fc5
Group: Development/Libraries
License: BSD
URL: http://www.scipy.org/
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: python-scipy <= %{version}
Requires: python, numpy, lapack, lapack-devel, atlas, atlas-devel
Provides: python-scipy = %{version}-%{release}
Prefix: /usr/local

%description
SciPy is open-source software for mathematics, science, and
engineering. It is also the name of a very popular conference on
scientific programming with Python. The core library is NumPy which
provides convenient and fast N-dimensional array manipulation. The
SciPy library is build to work with NumPy arrays, and provides many
user-friendly and efficient numerical routines such as routines for
numerical integration and optimization. Together, they run on all
popular operating systems, are quick to install, and are free of
charge. NumPy and SciPy are easy to use, but powerful enough to be
depended upon by some of the world's leading scientists and
engineers. If you need to manipulate numbers on a computer and display
or publish the results, give SciPy a try!

%install
tar xfz ../SOURCES/scipy-%{version}.tar.gz
cd scipy-%{version}/Lib
python setup.py install

%clean
[ "%{buildroot}" != '/' ] && %{__rm} -rf /usr/src/redhat/BUILD/scipy-%{version}

%files
%defattr(-,root,root)
%{pythondir}/scipy
%{pythondir}/IPython/UserConfig/ipythonrc-scipy
