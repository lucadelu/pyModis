#!/usr/bin/env python
#  class to convert/process modis data
#
#  (c) Copyright Luca Delucchi 2010
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at iasma dot it
#
##################################################################
#
#  This MODIS Python class is licensed under the terms of GNU GPL 2.
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
"""Convert MODIS HDF file to GeoTiff file or create a HDF mosaic file for
several tiles using Modis Reprojection Tools.

Classes:

* :class:`convertModis`
* :class:`createMosaic`
* :class:`processModis`

Functions:

* :func:`checkMRTpath`

"""
# python 2 and 3 compatibility
from __future__ import print_function

import os
import sys


def checkMRTpath(mrtpath):
    """Function to check if MRT path it correct

       :param str mrtpath: the path to MRT directory
       :return: The path to 'bin' and 'data' directory inside MRT path
    """
    if os.path.exists(mrtpath):
        if os.path.exists(os.path.join(mrtpath, 'bin')):
            if os.environ['PATH'].find(os.path.join(mrtpath,'data')) == -1:
                os.environ['PATH'] = "{path}:{data}".format(path=os.environ['PATH'],
                                                            data=os.path.join(mrtpath, 'data'))
            mrtpathbin = os.path.join(mrtpath, 'bin')
        else:
            raise Exception('The path {path} does not exist'.format(path=os.path.join(mrtpath, 'bin')))
        if os.path.exists(os.path.join(mrtpath, 'data')):
            mrtpathdata = os.path.join(mrtpath, 'data')
            os.environ['MRTDATADIR'] = os.path.join(mrtpath, 'data')
        else:
            raise Exception('The path {path} does not exist'.format(path=os.path.join(mrtpath, 'data')))
    else:
        raise Exception('The path {name} does not exist'.format(name=mrtpath))
    return mrtpathbin, mrtpathdata


class convertModis:
    """A class to convert modis data from hdf to tif using resample
       (from MRT tools)

       :param str hdfname: the full path to the hdf file
       :param str confile: the full path to the paramater file
       :param str mrtpath: the full path to mrt directory which contains
                           the bin and data directories
    """
    def __init__(self, hdfname, confile, mrtpath):
        """Initialization function"""
        # check if the hdf file exists
        if os.path.exists(hdfname):
            self.name = hdfname
        else:
            raise Exception('{name} does not exist'.format(name=hdfname))
        # check if confile exists
        if os.path.exists(confile):
            self.conf = confile
        else:
            raise Exception('{name} does not exist'.format(name=confile))
        # check if mrtpath and subdirectories exists and set environment
        # variables
        self.mrtpathbin, self.mrtpathdata = checkMRTpath(mrtpath)

    def executable(self):
        """Return the executable of resample MRT software"""
        if sys.platform.count('linux') != -1 or sys.platform.count('darwin') != -1:
            if os.path.exists(os.path.join(self.mrtpathbin, 'resample')):
                return os.path.join(self.mrtpathbin, 'resample')
        elif sys.platform.count('win32') != -1:
            if os.path.exists(os.path.join(self.mrtpathbin, 'resample.exe')):
                return os.path.join(self.mrtpathbin, 'resample.exe')

    def run(self):
        """Exec the convertion process"""
        import subprocess
        execut = self.executable()
        if not os.path.exists(execut):
            raise Exception('The path {name} does not exist: it could be an '
                            'erroneus path or software'.format(name=execut))
        else:
            subprocess.call([execut, '-p', self.conf])
        return "The hdf file {name} was converted successfully".format(name=self.name)


class createMosaic:
    """A class to convert several MODIS tiles into a mosaic

       :param str listfile: the path to file with the list of HDF MODIS
                            file
       :param str outprefix: the prefix for output files
       :param str mrtpath: the full path to mrt directory which contains
                           the bin and data directories
       :param str subset: a string composed by 1 and 0 according with the
                          layer to mosaic. The string should something like
                          '1 0 1 0 0 0 0'
    """
    def __init__(self, listfile, outprefix, mrtpath, subset=False):
        """Function to initialize the object"""
        import tempfile
        # check if the hdf file exists
        if os.path.exists(listfile):
            self.basepath = os.path.split(listfile)[0]
            self.fullpath = os.path.realpath(self.basepath)
            self.listfiles = listfile
            self.tmplistfiles = open(os.path.join(tempfile.gettempdir(),
                                                  '{name}.prm'.format(name=str(os.getpid()))), 'w')
            self.HDFfiles = open(listfile).readlines()
        else:
            raise Exception('{name} not exists'.format(name=listfile))
        # check if mrtpath and subdirectories exists and set environment
        # variables
        self.mrtpathbin, self.mrtpathdata = checkMRTpath(mrtpath)
        self.out = os.path.join(self.basepath, outprefix + '.hdf')
        self.outxml = self.out + '.xml'
        self.subset = subset

    def write_mosaic_xml(self):
        """Write the XML metadata file for MODIS mosaic"""
        from .parsemodis import parseModisMulti
        listHDF = []
        for i in self.HDFfiles:
            if i.find(self.basepath) == -1 and i.find('.hdf.xml') == -1:
                print("Attention: maybe you do not have the full path in the"
                      " HDF file list")
                listHDF.append(os.path.join(self.basepath, i.strip()))
                self.tmplistfiles.write("{name}\n".format(name=os.path.join(self.basepath, i.strip())))
            elif i.find('.hdf.xml') == -1:
                listHDF.append(i.strip())
                self.tmplistfiles.write("{name}\n".format(name=os.path.join(self.fullpath, i.strip())))
        pmm = parseModisMulti(listHDF)
        pmm.writexml(self.outxml)
        self.tmplistfiles.close()

    def executable(self):
        """Return the executable of mrtmosaic MRT software"""
        if sys.platform.count('linux') or sys.platform.count('darwin'):
            if os.path.exists(os.path.join(self.mrtpathbin, 'mrtmosaic')):
                return os.path.join(self.mrtpathbin, 'mrtmosaic')
        elif sys.platform.count('win32'):
            if os.path.exists(os.path.join(self.mrtpathbin, 'mrtmosaic.exe')):
                return os.path.join(self.mrtpathbin, 'mrtmosaic.exe')

    def run(self):
        """Exect the mosaic process"""
        import subprocess
        execut = self.executable()
        if not os.path.exists(execut):
            raise Exception('The path {name} does not exist, it could be an '
                            'erroneus path or software'.format(name=execut))
        else:
            self.write_mosaic_xml()
            if self.subset:
                subprocess.call([execut, '-i', self.tmplistfiles.name, '-o',
                                self.out, '-s', self.subset],
                                stderr=subprocess.STDOUT)
            else:
                subprocess.call([execut, '-i', self.tmplistfiles.name, '-o',
                                 self.out], stderr=subprocess.STDOUT)
        return "The mosaic file {name} has been created".format(name=self.out)


class processModis:
    """A class to process raw modis data from hdf to tif using swath2grid
       (from MRT Swath tools)

       :param str hdfname: the full path to the hdf file
       :param str confile: the full path to the paramater file
       :param str mrtpath: the full path to mrt directory which contains
                           the bin and data directories
    """
    def __init__(self, hdfname, confile, mrtpath):
        """Function to initialize the object"""
        # check if the hdf file exists
        if os.path.exists(hdfname):
            self.name = hdfname
        else:
            raise Exception('%s does not exist' % hdfname)
        # check if confile exists
        if os.path.exists(confile):
            self.conf = confile
        else:
            raise Exception('%s does not exist' % confile)
        # check if mrtpath and subdirectories exists and set environment
        # variables
        self.mrtpathbin, self.mrtpathdata = checkMRTpath(mrtpath)

    def executable(self):
        """Return the executable of resample MRT software"""
        if sys.platform.count('linux') != -1 or sys.platform.count('darwin') != -1:
            if os.path.exists(os.path.join(self.mrtpathbin, 'swath2grid')):
                return os.path.join(self.mrtpathbin, 'swath2grid')
        elif sys.platform.count('win32') != -1:
            if os.path.exists(os.path.join(self.mrtpathbin, 'swath2grid.exe')):
                return os.path.join(self.mrtpathbin, 'swath2grid.exe')

    def run(self):
        """Exec the convertion process"""
        import subprocess
        execut = self.executable()
        if not os.path.exists(execut):
            raise Exception('The path {name} does not exist, it could be an '
                            'erroneus path or software'.format(name=execut))
        else:
            subprocess.call([execut, '-pf={name}'.format(name=self.conf)])
        return "The hdf file {name} has been converted".format(name=self.name)
