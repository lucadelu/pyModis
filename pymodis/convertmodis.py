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

from datetime import *
import os
import sys


class convertModis:
  """A class to convert modis data from hdf to tif using resample
  (from MRT tools)
  """
  def __init__(self, hdfname, confile, mrtpath):
    """Initialization function :

       hdfname = the full path to the hdf file

       confile = the full path to the paramater file

       mrtpath = the full path to mrt directory where inside you have bin and
       data directories
    """
    # check if the hdf file exists
    if os.path.exists(hdfname):
      self.name = hdfname
    else:
      raise IOError('%s not exists' % hdfname)
    # check if confile exists
    if os.path.exists(confile):
      self.conf = confile
    else:
      raise IOError('%s not exists' % confile)
    # check if mrtpath and subdirectories exists and set environment variables
    if os.path.exists(mrtpath):
      if os.path.exists(os.path.join(mrtpath,'bin')):
        self.mrtpathbin = os.path.join(mrtpath,'bin')
        os.environ['PATH'] = "%s:%s" % (os.environ['PATH'],os.path.join(mrtpath,
                                                                        'data'))
      else:
        raise IOError('The path %s not exists' % os.path.join(mrtpath,'bin'))
      if os.path.exists(os.path.join(mrtpath,'data')):
        self.mrtpathdata = os.path.join(mrtpath,'data')
        os.environ['MRTDATADIR'] = os.path.join(mrtpath,'data')
      else:
        raise IOError('The path %s not exists' % os.path.join(mrtpath,'data'))
    else:
      raise IOError('The path %s not exists' % mrtpath)

  def executable(self):
    """Return the executable of resample MRT software
    """
    if sys.platform.count('linux') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'resample')):
        return os.path.join(self.mrtpathbin,'resample')
    elif sys.platform.count('win32') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'resample.exe')):
        return os.path.join(self.mrtpathbin, 'resample.exe')

  def run(self):
    """Exec the convertion process"""
    import subprocess
    execut = self.executable()
    if not os.path.exists(execut):
      raise IOError('The path %s not exists, could be an erroneus path or '\
                    + 'software') % execut
    else:
      subprocess.call([execut,'-p',self.conf])
    return "The hdf file %s was converted" % self.name


class createMosaic:
  """A class to convert several MODIS tiles into a mosaic"""
  def __init__(self,
              listfile,
              outprefix,
              mrtpath,
              subset = False
              ):
    import tempfile
    # check if the hdf file exists
    if os.path.exists(listfile):
      self.basepath = os.path.split(listfile)[0]
      self.fullpath = os.path.realpath(self.basepath)
      self.listfiles = listfile
      self.tmplistfiles = open(os.path.join(tempfile.gettempdir(),
                               '%s.prm' % str(os.getpid())), 'w')
      self.HDFfiles = open(listfile).readlines()
    else:
      raise IOError('%s not exists' % hdfname)
    # check if mrtpath and subdirectories exists and set environment variables
    if os.path.exists(mrtpath):
      if os.path.exists(os.path.join(mrtpath,'bin')):
        self.mrtpathbin = os.path.join(mrtpath,'bin')
        os.environ['PATH'] = "%s:%s" % (os.environ['PATH'],os.path.join(mrtpath,
                                                                        'data'))
      else:
        raise IOError('The path %s not exists' % os.path.join(mrtpath,'bin'))
      if os.path.exists(os.path.join(mrtpath,'data')):
        self.mrtpathdata = os.path.join(mrtpath,'data')
        os.environ['MRTDATADIR'] = os.path.join(mrtpath,'data')
      else:
        raise IOError('The path %s not exists' % os.path.join(mrtpath,'data'))
    else:
      raise IOError('The path %s not exists' % mrtpath)
    self.out = os.path.join(self.basepath, outprefix + '.hdf')
    self.outxml = self.out + '.xml'
    self.subset = subset

  def write_mosaic_xml(self):
    """Write the XML metadata file for MODIS mosaic"""
    from parsemodis import parseModisMulti
    listHDF = []
    for i in self.HDFfiles:
      if i.find(self.basepath) == -1 and i.find('.hdf.xml') == -1:
        print "Attection maybe you have the not full path in the HDF file list"
        listHDF.append(os.path.join(self.basepath,i.strip()))
        self.tmplistfiles.write("%s\n" % os.path.join(self.basepath,i.strip()))
      elif i.find('.hdf.xml') == -1:
        listHDF.append(i.strip())
        self.tmplistfiles.write("%s\n" % os.path.join(self.fullpath,i.strip()))
    pmm = parseModisMulti(listHDF)
    pmm.writexml(self.outxml)
    self.tmplistfiles.close()


  def executable(self):
    """Return the executable of mrtmosaic MRT software
    """
    if sys.platform.count('linux'):
      if os.path.exists(os.path.join(self.mrtpathbin,'mrtmosaic')):
        return os.path.join(self.mrtpathbin,'mrtmosaic')
    elif sys.platform.count('win32'):
      if os.path.exists(os.path.join(self.mrtpathbin,'mrtmosaic.exe')):
        return os.path.join(self.mrtpathbin, 'mrtmosaic.exe')

  def run(self):
    """Exect the mosaic process"""
    import subprocess
    execut = self.executable()
    if not os.path.exists(execut):
      raise IOError('The path %s not exists, could be an erroneus path or '\
                    + 'software') % execut
    else:
      self.write_mosaic_xml()
      if self.subset:
        subprocess.call([execut,'-i',self.tmplistfiles.name,'-o',self.out,'-s',
                         self.subset], stderr = subprocess.STDOUT)
      else:
        subprocess.call([execut,'-i',self.tmplistfiles.name,'-o',self.out],
                        stderr = subprocess.STDOUT)
    return "The mosaic file %s is created" % self.out


class processModis:
  """A class to process raw modis data from hdf to tif using swath2grid (from MRT Swath tools)
  """
  def __init__(self, 
              hdfname, confile, mrtpath, 
              inputhdf = None, outputhdf = None, geolocfile = None
  ):
    """Initialization function :
       hdfname = the full path to the hdf file
       confile = the full path to the paramater file
       mrtpath = the full path to mrt directory where inside you have bin and 
                 data directories
    """
    # check if the hdf file exists
    if os.path.exists(hdfname):
      self.name = hdfname
    else:
      raise IOError('%s not exists' % hdfname)
    # check if confile exists
    if os.path.exists(confile):
      self.conf = confile
    else:
      raise IOError('%s not exists' % confile)
    # check if mrtpath and subdirectories exists and set environment variables
    if os.path.exists(mrtpath):
      if os.path.exists(os.path.join(mrtpath,'bin')):
        self.mrtpathbin = os.path.join(mrtpath,'bin')
        os.environ['PATH'] = "%s:%s" % (os.environ['PATH'],os.path.join(mrtpath,
                                                                        'data'))
      else:
        raise IOError('The path %s not exists' % os.path.join(mrtpath,'bin'))
      if os.path.exists(os.path.join(mrtpath,'data')):
        self.mrtpathdata = os.path.join(mrtpath,'data')
        os.environ['MRTDATADIR'] = os.path.join(mrtpath,'data')
      else:
        raise IOError('The path %s not exists' % os.path.join(mrtpath,'data'))
    else:
      raise IOError('The path %s not exists' % mrtpath)

  def executable(self):
    """Return the executable of resample MRT software
    """
    if sys.platform.count('linux') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'swath2grid')):
        return os.path.join(self.mrtpathbin,'swath2grid')
    elif sys.platform.count('win32') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'swath2grid.exe')):
        return os.path.join(self.mrtpathbin,'swath2grid.exe')

  def run(self):
    """Exec the convertion process"""
    import subprocess
    execut = self.executable()
    if not os.path.exists(execut):
      raise IOError('The path %s not exists, could be an erroneus path or '\
                    + 'software') % execut
    else:
      subprocess.call([execut,'-pf=%s' % self.conf])
    return "The hdf file %s was converted" % self.name
