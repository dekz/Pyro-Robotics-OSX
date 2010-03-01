%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.3)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: Modular toolkit for Data Processing
Name: python-mdp
Version: 1.1.0
Release: fc5
Group: Development/Libraries
License: LGPL
URL: http://mdp-toolkit.sourceforge.net/
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: python-mdp <= %{version}
Requires: python-scipy
Provides: python-mdp = %{version}-%{release}
Prefix: /usr/local

%description
Modular toolkit for Data Processing (MDP) is a Python library to
perform data processing. Already implemented algorithms include:
Principal Component Analysis (PCA), Independent Component Analysis
(ICA), Slow Feature Analysis (SFA), and Growing Neural Gas (GNG).

%install
tar xfz ../SOURCES/MDP-%{version}.tar.gz
cd MDP-%{version}
python setup.py install

%clean
[ "%{buildroot}" != '/' ] && %{__rm} -rf /usr/src/redhat/BUILD/MDP-%{version}

%files
%defattr(-,root,root)
%{pythondir}/mdp
%{pythondir}/graph
