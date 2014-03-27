#
# spec file for package pyModis (0.7.4)
#
# Copyright (c) 2014 Angelos Tzotsos <tzotsos@opensuse.org>
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pyModis package itself (unless the
# license for the pyModis package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%define pyname pymodis
%define pyname_cap pyModis

Name:           python-%{pyname}
Version:        0.7.4
Release:        0
Summary:        PyModis is a FOSS Python library to work with MODIS data
License:        GPLv2+
Url:            http://pymodis.fem-environment.eu
Group:          Productivity/Scientific/Other
Source0:        %{pyname_cap}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
BuildRequires:  python-devel 
BuildRequires:  python-setuptools
BuildRequires:  python-numpy
BuildRequires:  fdupes
Requires:	python
Requires:       python-numpy
Requires:       python-gdal

%description
PyModis is a Free and Open Source Python based library to work with MODIS data. It offers bulk-download for user selected time ranges, mosaicking of MODIS tiles, and the reprojection from Sinusoidal to other projections, convert HDF format to other formats

%prep
%setup -q -n %{pyname_cap}-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}

python setup.py install --prefix=%{_prefix} --root=%{buildroot} \
                                            --record-rpm=INSTALLED_FILES

%fdupes -s %{buildroot}

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root,-)

%changelog
