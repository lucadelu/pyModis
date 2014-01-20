#!/usr/bin/python
# -*- coding: utf-8 -*-
#  class to download modis data
#
#  (c) Copyright Luca Delucchi 2010
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at iasma dot it
#
##################################################################
#
#  Modis class is licensed under the terms of GNU GPL 2
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of
#  the License,or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
##################################################################

try:
    from setuptools import setup
except:
    from distutils.core import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
  name='pyModis',
  version='0.7.3',
  py_modules=['pymodis.downmodis', 'pymodis.convertmodis',
              'pymodis.parsemodis', 'pymodis.optparse_required'],
  #packages = ['pymodis'],
  scripts=['scripts/modis_download.py', 'scripts/modis_multiparse.py',
           'scripts/modis_parse.py', 'scripts/modis_mosaic.py',
           'scripts/modis_convert.py', 'scripts/modis_download_from_list.py'],
  author='Luca Delucchi',
  author_email='luca.delucchi@fmach.it',
  url='http://pymodis.fem-environment.eu',
  description='Python library for MODIS data',
  long_description=read('README'),
  install_requires=['GDAL', 'numpy'],
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
    "Programming Language :: Python",
    "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)"
  ],
)
