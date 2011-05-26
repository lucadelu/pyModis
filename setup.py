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
from distutils.core import setup

setup(
  name = 'pyModis',
  version = '0.3',
  py_modules = ['modis'],
  scripts = ['downloadmodis.py'],
  author = 'Luca Delucchi',
  author_email = 'luca.delucchi@iasma.it',
  url = 'http://gis.fem-environment.eu/gis-development/pyModis',
  description = 'Python library for MODIS data',
  long_description = 'Python library to download MODIS data',
  license = 'GNU GPL 2 or later'
)
