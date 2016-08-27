#!/usr/bin/python
# -*- coding: utf-8 -*-
#  class to download modis data
#
#  (c) Copyright Luca Delucchi 2010-2016
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at fmach dot it
#
##################################################################
#
#  The Modis class is licensed under the terms of GNU GPL 2
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
##################################################################

import os
import re
try:
    from setuptools import setup
except:
    from distutils.core import setup
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
if sys.version_info.major == 3:
    with open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
        README = f.read()
    with open(os.path.join(HERE, 'pymodis', '__init__.py'), encoding='utf-8') as fp:
        VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)
else:
    with open(os.path.join(HERE, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(HERE, 'pymodis', '__init__.py')) as fp:
        VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)

setup(
    name='pyModis',
    version=VERSION,
    py_modules=['pymodis.downmodis', 'pymodis.convertmodis',
                'pymodis.parsemodis', 'pymodis.optparse_required',
                'pymodis.optparse_gui', 'pymodis.qualitymodis',
                'pymodis.convertmodis_gdal',  'pymodis.productmodis'], 
    #packages = ['pymodis'],
    scripts=['scripts/modis_download.py', 'scripts/modis_multiparse.py',
             'scripts/modis_parse.py', 'scripts/modis_mosaic.py',
             'scripts/modis_convert.py', 'scripts/modis_quality.py',
             'scripts/modis_download_from_list.py'],
    author='Luca Delucchi',
    author_email='luca.delucchi@fmach.it',
    url='http://www.pymodis.org',
    description='Python library for MODIS data',
    long_description=README,
    install_requires=['GDAL', 'numpy', 'future',  'requests'],
    extras_require={'GUI': ["wxPython", "wxPython-common"]},
    license='GNU GPL 2 or later',
    platforms=['Any'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Topic :: Scientific/Engineering :: GIS",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
	"Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
    ],
)
