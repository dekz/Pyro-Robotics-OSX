# GDAL RPM SPEC file

%define pythonver %(%{__python} -c 'import sys; print sys.version[:3]' || echo 2.3)
%define pythondir %(%{__python} -c 'import sys; print [x for x in sys.path if x[-13:] == "site-packages"][0]')

Summary: Geospatial Data Abstraction Library
Name: gdal
Version: 1.3.2
Release: fc5
Group: Development/Libraries
License: X/MIT-style
URL: http://www.remotesensing.org/gdal/
Source: http://www.gdal.org/dl/%{name}-%{version}.tar.gz
Packager: D.S. Blank <dblank@cs.brynmawr.edu>
Obsoletes: gdal <= %{version}
Provides: gdal = %{version}-%{release}
Prefix: /usr/local

%description 
GDAL is a translator library for raster geospatial data formats that
is released under an X/MIT style Open Source license. As a library, it
presents a single abstract data model to the calling application for
all supported formats.

%prep
%setup -q

%build
%configure

%install
%{__rm} -rf %{buildroot}
%makeinstall

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/epsg_tr.py
%{_bindir}/gcps2vec.py
%{_bindir}/gcps2wld.py
%{_bindir}/gdal2xyz.py
%{_bindir}/gdaladdo
%{_bindir}/gdalchksum.py
%{_bindir}/gdal-config
%{_bindir}/gdal_contour
%{_bindir}/gdalimport.py
%{_bindir}/gdalinfo
%{_bindir}/gdal_merge.py
%{_bindir}/gdaltindex
%{_bindir}/gdal_translate
%{_bindir}/gdalwarp
%{_bindir}/ogr2ogr
%{_bindir}/ogrinfo
%{_bindir}/ogrtindex
%{_bindir}/pct2rgb.py
%{_bindir}/rgb2pct.py
%{_includedir}/cpl_config.h
%{_includedir}/cpl_conv.h
%{_includedir}/cpl_csv.h
%{_includedir}/cpl_error.h
%{_includedir}/cpl_list.h
%{_includedir}/cpl_minixml.h
%{_includedir}/cpl_multiproc.h
%{_includedir}/cpl_odbc.h
%{_includedir}/cpl_port.h
%{_includedir}/cpl_string.h
%{_includedir}/cpl_vsi.h
%{_includedir}/gdal_alg.h
%{_includedir}/gdal_frmts.h
%{_includedir}/gdal.h
%{_includedir}/gdal_priv.h
%{_includedir}/gdal_version.h
%{_includedir}/gdalwarper.h
%{_includedir}/gvgcpfit.h
%{_includedir}/memdataset.h
%{_includedir}/ogr_api.h
%{_includedir}/ogr_core.h
%{_includedir}/ogr_feature.h
%{_includedir}/ogr_featurestyle.h
%{_includedir}/ogr_geometry.h
%{_includedir}/ogr_p.h
%{_includedir}/ogrsf_frmts.h
%{_includedir}/ogr_spatialref.h
%{_includedir}/ogr_srs_api.h
%{_includedir}/rawdataset.h
%{_includedir}/thinplatespline.h
%{_includedir}/vrtdataset.h
%{_libdir}/libgdal.a
%{_libdir}/libgdal.la
%{_libdir}/libgdal.so
%{_libdir}/libgdal.so.1
%{_libdir}/libgdal.so.1.10.0
%{_mandir}/man1/gdaladdo.1
%{_mandir}/man1/gdal-config.1
%{_mandir}/man1/gdal_contour.1
%{_mandir}/man1/gdalinfo.1
%{_mandir}/man1/gdaltindex.1
%{_mandir}/man1/gdal_translate.1
%{_mandir}/man1/gdal_utilities.1
%{_mandir}/man1/gdalwarp.1
%{_mandir}/man1/ogr2ogr.1
%{_mandir}/man1/ogrinfo.1
%{_mandir}/man1/ogrtindex.1
%{_mandir}/man1/ogr_utilities.1
%{_datadir}/gdal_datum.csv
%{_datadir}/gdalicon.png
