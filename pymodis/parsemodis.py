#!/usr/bin/env python
#  class to parse modis data
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
import string
import os

## lists of parameters accepted by resample MRT software
# projections
PROJ_LIST = ['AEA','GEO', 'HAM', 'IGH', 'ISIN', 'LA', 'LCC', 'MOL', 'PS',
             'SIN','TM', 'UTM', 'MERCAT']
# resampling
RESAM_LIST = ['NEAREST_NEIGHBOR', 'BICUBIC', 'CUBIC_CONVOLUTION', 'NONE']
RESAM_LIST_SWATH = ['NN', 'BI', 'CC']

# datum
DATUM_LIST = ['NODATUM', 'NAD27', 'NAD83', 'WGS66', 'WGS72', 'WGS84']
SPHERE_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
               19, 20]


class parseModis:
  """Class to parse MODIS xml files, it also can create the parameter
     configuration file for resampling MODIS DATA with the MRT software or
     convertmodis Module
  """

  def __init__(self, filename):
    """Initialization function :

       filename = the name of MODIS hdf file
    """
    from xml.etree import ElementTree
    if os.path.exists(filename):
      # hdf name
      self.hdfname = filename
    else:
      raise IOError('%s not exists' % filename)

    if os.path.exists(self.hdfname + '.xml'):
      # xml hdf name
      self.xmlname = self.hdfname + '.xml'
    else:
      raise IOError('%s not exists' % self.hdfname + '.xml')

    # tif name for the output file for resample MRT software
    self.tifname = self.hdfname.replace('.hdf', '.tif')
    with open(self.xmlname) as f:
      self.tree = ElementTree.parse(f)
    # return the code of tile for conf file
    self.code = os.path.split(self.hdfname)[1].split('.')[-2]
    self.path = os.path.split(self.hdfname)[0]

  def __str__(self):
    """Print the file without xml tags"""
    retString = ""
    try:
      for node in self.tree.iter():
        if node.text.strip() != '':
          retString = "%s = %s\n" % (node.tag, node.text)
    except:
      for node in self.tree.getiterator():
        if node.text.strip() != '':
          retString = "%s = %s\n" % (node.tag, node.text)
    return retString

  def getRoot(self):
    """Set the root element"""
    self.rootree = self.tree.getroot()

  def retDTD(self):
    """Return the DTDVersion element"""
    self.getRoot()
    return self.rootree.find('DTDVersion').text

  def retDataCenter(self):
    """Return the DataCenterId element"""
    self.getRoot()
    return self.rootree.find('DataCenterId').text

  def getGranule(self):
    """Set the GranuleURMetaData element"""
    self.getRoot()
    self.granule = self.rootree.find('GranuleURMetaData')

  def retGranuleUR(self):
    """Return the GranuleUR element"""
    self.getGranule()
    return self.granule.find('GranuleUR').text

  def retDbID(self):
    """Return the DbID element"""
    self.getGranule()
    return self.granule.find('DbID').text

  def retInsertTime(self):
    """Return the InsertTime element"""
    self.getGranule()
    return self.granule.find('InsertTime').text

  def retLastUpdate(self):
    """Return the LastUpdate element"""
    self.getGranule()
    return self.granule.find('LastUpdate').text

  def retCollectionMetaData(self):
    """Return the CollectionMetaData element as dictionary"""
    self.getGranule()
    collect = {}
    for i in self.granule.find('CollectionMetaData').getiterator():
      if i.text.strip() != '':
        collect[i.tag] = i.text
    return collect

  def retDataFiles(self):
    """Return the DataFiles element as dictionary"""
    self.getGranule()
    collect = {}
    datafiles = self.granule.find('DataFiles')
    for i in datafiles.find('DataFileContainer').getiterator():
      if i.text.strip() != '':
        collect[i.tag] = i.text
    return collect

  def retDataGranule(self):
    """Return the ECSDataGranule elements as dictionary"""
    self.getGranule()
    datagran = {}
    for i in self.granule.find('ECSDataGranule').getiterator():
      if i.text.strip() != '':
        datagran[i.tag] = i.text
    return datagran

  def retPGEVersion(self):
    """Return the PGEVersion element"""
    self.getGranule()
    return self.granule.find('PGEVersionClass').find('PGEVersion').text

  def retRangeTime(self):
    """Return the RangeDateTime elements as dictionary
    """
    self.getGranule()
    rangeTime = {}
    for i in self.granule.find('RangeDateTime').getiterator():
      if i.text.strip() != '':
        rangeTime[i.tag] = i.text
    return rangeTime

  def retBoundary(self):
    """Return the maximum extend (Bounding Box) of the MODIS file as
    dictionary"""
    self.getGranule()
    self.boundary = []
    lat = []
    lon = []
    spatialContainer = self.granule.find('SpatialDomainContainer')
    horizontal = spatialContainer.find('HorizontalSpatialDomainContainer')
    boundary = horizontal.find('GPolygon').find('Boundary')
    for i in boundary.findall('Point'):
      la = float(i.find('PointLongitude').text)
      lo = float(i.find('PointLatitude').text)
      lon.append(la)
      lat.append(lo)
      self.boundary.append({'lat': la, 'lon': lo})
    extent = {'min_lat': min(lat), 'max_lat': max(lat), 'min_lon': min(lon),
              'max_lon': max(lon)}
    return extent

  def retMeasure(self):
    """Return statistics of QA as dictionary"""
    value = {}
    self.getGranule()
    mes = self.granule.find('MeasuredParameter')
    mespc = mes.find('MeasuredParameterContainer')
    value['ParameterName'] = mespc.find('ParameterName').text
    meStat = mespc.find('QAStats')
    qastat = {}
    for i in meStat.getiterator():
      if i.tag != 'QAStats':
        qastat[i.tag] = i.text
    value['QAStats'] = qastat
    meFlag = mespc.find('QAFlags')
    flagstat = {}
    for i in meFlag.getiterator():
      if i.tag != 'QAFlags':
        flagstat[i.tag] = i.text
    value['QAFlags'] = flagstat
    return value

  def retPlatform(self):
    """Return the platform values as dictionary."""
    value = {}
    self.getGranule()
    plat = self.granule.find('Platform')
    value['PlatformShortName'] = plat.find('PlatformShortName').text
    instr = plat.find('Instrument')
    value['InstrumentShortName'] = instr.find('InstrumentShortName').text
    sensor = instr.find('Sensor')
    value['SensorShortName'] = sensor.find('SensorShortName').text
    return value

  def retPSA(self):
    """Return the PSA values as dictionary, the PSAName is the key and
       and PSAValue is the value
    """
    value = {}
    self.getGranule()
    psas = self.granule.find('PSAs')
    for i in psas.findall('PSA'):
      value[i.find('PSAName').text] = i.find('PSAValue').text
    return value

  def retInputGranule(self):
    """Return the input files (InputGranule) used to process the considered
    file"""
    value = []
    self.getGranule()
    for i in self.granule.find('InputGranule').getiterator():
      if i.tag != 'InputGranule':
        value.append(i.text)
    return value

  def retBrowseProduct(self):
    """Return the BrowseProduct element"""
    self.getGranule()
    try:
        value = self.granule.find('BrowseProduct').find('BrowseGranuleId').text
    except:
        value = None
    return value

  def confResample(self, spectral, res=None, output=None, datum='WGS84',
                  resample='NEAREST_NEIGHBOR', projtype='GEO',  utm=None,
                  projpar='( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 )',
                  bound=None
                  ):
    """Create the parameter file to use with resample MRT software to create
    tif file

        spectral = the spectral subset to be used, look the product table to
        understand the layer that you want use. For example:

            - NDVI ( 1 1 1 0 0 0 0 0 0 0 0 0) copy only layer NDVI, EVI
              and QA VI the other layers are not used
            - LST ( 1 1 0 0 1 1 0 0 0 0 0 0 ) copy only layer daily and
              nightly temperature and QA

        res = the resolution for the output file, it must be set in the map
        unit of output projection system. The software will use the
        original resolution of input file if res it isn't set

        output = the output name, if it doesn't set will use the prefix name
        of input hdf file

        utm = the UTM zone if projection system is UTM

        resample = the type of resampling, the valid values are:
            - NN (nearest neighbor)
            - BI (bilinear)
            - CC (cubic convolution)

        projtype = the output projection system, the valid values are:
            - AEA (Albers Equal Area)
            - ER (Equirectangular)
            - GEO (Geographic Latitude/Longitude)
            - HAM (Hammer)
            - ISIN (Integerized Sinusoidal)
            - IGH (Interrupted Goode Homolosine)
            - LA (Lambert Azimuthal)
            - LCC (LambertConformal Conic)
            - MERCAT (Mercator)
            - MOL (Mollweide)
            - PS (Polar Stereographic)
            - SIN (Sinusoidal)
            - UTM (Universal TransverseMercator)

        datum = the datum to use, the valid values are:
            - NAD27
            - NAD83
            - WGS66
            - WGS76
            - WGS84
            - NODATUM

        projpar = a list of projection parameters, for more info check the
        Appendix C of MODIS reprojection tool user manual
        https://lpdaac.usgs.gov/content/download/4831/22895/file/mrt41_usermanual_032811.pdf

        bound = dictionary with the following keys:
            - max_lat
            - max_lon
            - min_lat
            - min_lon
        """
    #check if spectral it's write with correct construct ( value )
    if string.find(spectral, '(') == -1 or  string.find(spectral, ')') == -1:
      raise IOError('ERROR: The spectral string should be similar to: ( 1 0 )')
    # output name
    if not output:
      fileout = self.tifname
    else:
      fileout = output
    # the name of the output parameters files for resample MRT software
    filename = os.path.join(self.path, '%s_mrt_resample.conf' % self.code)
    # if the file already exists it remove it 
    if os.path.exists(filename):
      os.remove(filename)
    # open the file
    conFile = open(filename, 'w')
    conFile.write("INPUT_FILENAME = %s\n" % self.hdfname)
    conFile.write("SPECTRAL_SUBSET = %s\n" % spectral)
    conFile.write("SPATIAL_SUBSET_TYPE = INPUT_LAT_LONG\n")
    if not bound:
      # return the boundary from the input xml file
      bound = self.retBoundary()
    else:
      if 'max_lat' not in bound or 'min_lat' not in bound  or \
      'min_lon' not in bound or 'max_lon' not in bound:
          raise IOError('bound variable is a dictionary with the following ' \
                        'keys: max_lat, min_lat, min_lon, max_lon')
    # Order:  UL: N W  - LR: S E
    conFile.write("SPATIAL_SUBSET_UL_CORNER = ( %f %f )\n" % (bound['max_lat'],
                                                              bound['min_lon']))
    conFile.write("SPATIAL_SUBSET_LR_CORNER = ( %f %f )\n" % (bound['min_lat'],
                                                              bound['max_lon']))
    conFile.write("OUTPUT_FILENAME = %s\n" % fileout)
    # if resample is in resam_list set the parameter otherwise return an error
    if resample in RESAM_LIST:
      conFile.write("RESAMPLING_TYPE = %s\n" % resample)
    else:
      raise IOError('The resampling type %s is not supportet.\n' \
                   'The resampling type supported are %s' % (resample,
                                                             RESAM_LIST))
    # if projtype is in proj_list set the parameter otherwise return an error
    if projtype in PROJ_LIST:
      conFile.write("OUTPUT_PROJECTION_TYPE = %s\n" % projtype)
    else:
      raise IOError('The projection type %s is not supported.\n' \
                   'The projections supported are %s' % (projtype, PROJ_LIST))
    conFile.write("OUTPUT_PROJECTION_PARAMETERS = %s\n" % projpar)
    # if datum is in datum_list set the parameter otherwise return an error
    if datum in DATUM_LIST:
      conFile.write("DATUM = %s\n" % datum)
    else:
      raise IOError('The datum %s is not supported.\n' \
                   'The datum supported are %s' % (datum, DATUM_LIST))
    # if utm is not None write the UTM_ZONE parameter in the file
    if utm:
      conFile.write("UTM_ZONE = %s\n" % utm)
    # if res is not None write the OUTPUT_PIXEL_SIZE parameter in the file
    if res:
      conFile.write("OUTPUT_PIXEL_SIZE = %i\n" % res)
    conFile.close()
    return filename

  def confResample_swath(self, sds, geoloc, res, output=None, 
                  sphere='8', resample='NN', projtype='GEO',  utm=None,
                  projpar='0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
                  bound=None
                  ):
    """Create the parameter file to use with resample MRT software to create
       tif file

        sds = Name of band/s (Science Data Set) to resample

        geoloc = Name geolocation file (example MOD3, MYD3)

        res = the resolution for the output file, it must be set in the map
        unit of output projection system. The software will use the
        original resolution of input file if res it isn't set

        output = the output name, if it doesn't set will use the prefix name
        of input hdf file

        sphere = Output sphere number. Valid options are:
            - 0=Clarke 1866
            - 1=Clarke 1880
            - 2=Bessel
            - 3=International 1967
            - 4=International 1909
            - 5=WGS 72
            - 6=Everest
            - 7=WGS 66
            - 8=GRS1980/WGS 84
            - 9=Airy
            - 10=Modified Everest
            - 11=Modified Airy
            - 12=Walbeck
            - 13=Southeast Asia
            - 14=Australian National
            - 15=Krassovsky
            - 16=Hough
            - 17=Mercury1960
            - 18=Modified Mercury1968
            - 19=Sphere 19 (Radius 6370997)
            - 20=MODIS Sphere (Radius 6371007.181)

        resample = the type of resampling, the valid values are:
            - NN (nearest neighbor)
            - BI (bilinear)
            - CC (cubic convolution)

        projtype = the output projection system, the valid values are:
            - AEA (Albers Equal Area)
            - ER (Equirectangular)
            - GEO (Geographic Latitude/Longitude)
            - HAM (Hammer)
            - ISIN (Integerized Sinusoidal)
            - IGH (Interrupted Goode Homolosine)
            - LA (Lambert Azimuthal)
            - LCC (LambertConformal Conic)
            - MERCAT (Mercator)
            - MOL (Mollweide)
            - PS (Polar Stereographic),
            - SIN ()Sinusoidal)
            - UTM (Universal TransverseMercator)

        utm = the UTM zone if projection system is UTM

        projpar = a list of projection parameters, for more info check
        the Appendix C of MODIS reprojection tool user manual
        https://lpdaac.usgs.gov/content/download/4831/22895/file/mrt41_usermanual_032811.pdf

        bound = dictionary with the following keys:
            - max_lat
            - max_lon
            - min_lat
            - min_lon
        """
    # output name
    if not output:
      fileout = self.tifname
    else:
      fileout = output
    # the name of the output parameters files for resample MRT software
    filename = os.path.join(self.path, '%s_mrt_resample.prm' % self.code)
    # if the file already exists it remove it 
    if os.path.exists(filename):
      os.remove(filename)
    # open the file
    conFile = open(filename, 'w')
    conFile.write("INPUT_FILENAME = %s\n" % self.hdfname)
    conFile.write("GEOLOCATION_FILENAME = %s\n" % geoloc)
    conFile.write("INPUT_SDS_NAME = %s\n" % sds)
    conFile.write("OUTPUT_SPATIAL_SUBSET_TYPE = LAT_LONG\n")
    if not bound:
      # return the boundary from the input xml file
      bound = self.retBoundary()
    else:
      if 'max_lat' not in bound or 'min_lat' not in bound  or \
      'min_lon' not in bound or 'max_lon' not in bound:
          raise IOError('bound variable is a dictionary with the following ' \
                        'keys: max_lat, min_lat, min_lon, max_lon')
    # Order:  UL: N W  - LR: S E
    conFile.write("OUTPUT_SPACE_UPPER_LEFT_CORNER (LONG LAT) = %f %f\n" % (bound['max_lat'],
                                                              bound['min_lon']))
    conFile.write("OUTPUT_SPACE_LOWER_RIGHT_CORNER (LONG LAT) = %f %f\n" % (bound['min_lat'],
                                                              bound['max_lon']))
    conFile.write("OUTPUT_FILENAME = %s\n" % fileout)
    conFile.write("OUTPUT_FILE_FORMAT = GEOTIFF_FMT\n")
    # if resample is in resam_list set the parameter otherwise return an error
    if resample in RESAM_LIST_SWATH:
      conFile.write("KERNEL_TYPE (CC/BI/NN) = %s\n" % resample)
    else:
      raise IOError('The resampling type %s is not supportet.\n' \
                   'The resampling type supported are %s' % (resample,
                                                             RESAM_LIST_SWATH))
    # if projtype is in proj_list set the parameter otherwise return an error
    if projtype in PROJ_LIST:
      conFile.write("OUTPUT_PROJECTION_NUMBER = %s\n" % projtype)
    else:
      raise IOError('The projection type %s is not supported.\n' \
                   'The projections supported are %s' % (projtype, PROJ_LIST))
    conFile.write("OUTPUT_PROJECTION_PARAMETER = %s\n" % projpar)
    # if sphere is in sphere_list set the parameter otherwise return an error
    if int(sphere) in SPHERE_LIST:
      conFile.write("OUTPUT_PROJECTION_SPHERE = %s\n" % sphere)
    else:
      raise IOError('The sphere %s is not supported.\n' \
                   'The spheres supported are %s' % (sphere, SPHERE_LIST))
    # if utm is not None write the UTM_ZONE parameter in the file
    if utm:
      if utm < '-60' or utm > '60':
        raise IOError('The valid UTM zone are -60 to 60')
      else:
        conFile.write("OUTPUT_PROJECTION_ZONE = %s\n" % utm)
    # if res is not None write the OUTPUT_PIXEL_SIZE parameter in the file
    if res:
      conFile.write("OUTPUT_PIXEL_SIZE = %f\n" % res)
    conFile.close()
    return filename


class parseModisMulti:
  """A class to obtain some variables for the xml file of several MODIS tiles.
     It can also create the xml file
  """

  def __init__(self, hdflist):
    """hdflist = python list containing the hdf files"""
    from xml.etree import ElementTree
    self.ElementTree = ElementTree
    self.hdflist = hdflist
    self.parModis = []
    self.nfiles = 0
    # for each hdf files create a parseModis object
    for i in hdflist:
      self.parModis.append(parseModis(i))
      self.nfiles += 1


  def _most_common(self, lst):
    """Return the most common value of a list"""
    return max(set(lst), key=lst.count)


  def _checkval(self, vals):
    """Internal function to return values from list

    vals = list of values
    """
    if vals.count(vals[0]) == self.nfiles:
      return [vals[0]]
    else:
      outvals = []
      for i in vals:
        if outvals.count(i) == 0:
          outvals.append(i)
      return outvals

  def _checkvaldict(self, vals):
    """Internal function to return values from dictionary

    vals = dictionary of values
    """
    keys = vals[0].keys()
    outvals = {}
    for k in keys:
      valtemp = []
      for v in vals:
        valtemp.append(v[k])
      if valtemp.count(valtemp[0]) == self.nfiles:
        outvals[k] = valtemp[0]
      elif len(valtemp) == self.nfiles:
        outvals[k] = self._most_common(valtemp)
      else:
        raise IOError('Something wrong reading XML files')

    return outvals

  def _minval(self, vals):
    """Internal function to return the minimum value

    vals = list of values
    """
    outval = vals[0]
    for i in range(1, len(vals)):
      if outval > i:
        outval = i
    return outval

  def _maxval(self, vals):
    """Internal function to return the maximum value

    vals = list of values   
    """
    outval = vals[0]
    for i in range(1, len(vals)):
      if outval < i:
        outval = i
    return outval

  def _cicle_values(self, obj, values):
    """Internal function to add values from a dictionary

    obj = element to add values

    values = dictionary containing keys and values
    """
    for k,v in values.iteritems():
      elem = self.ElementTree.SubElement(obj, k)
      elem.text = v

  def _addPoint(self, obj, lon, lat):
    """Internal function to add a point in boundary xml tag

    obj = element to add point

    lon = longitude of point

    lat = latitude of point
    """
    pt = self.ElementTree.SubElement(obj, 'Point')
    ptlon = self.ElementTree.SubElement(pt, 'PointLongitude')
    ptlon.text = str(self.boundary[lon])
    ptlat = self.ElementTree.SubElement(pt, 'PointLatitude')
    ptlat.text = str(self.boundary[lat])

  def valDTD(self, obj):
    """Function to add DTDVersion

    obj = element to add DTDVersion
    """
    values = []
    for i in self.parModis:
      values.append(i.retDTD())
    for i in self._checkval(values):
      dtd = self.ElementTree.SubElement(obj, 'DTDVersion')
      dtd.text = i

  def valDataCenter(self, obj):
    """Function to add DataCenter

    obj = element to add DataCenter
    """
    values = []
    for i in self.parModis:
      values.append(i.retDataCenter())
    for i in self._checkval(values):
      dci = self.ElementTree.SubElement(obj, 'DataCenterId')
      dci.text = i

  def valGranuleUR(self, obj):
    """Function to add GranuleUR

    obj = element to add GranuleUR
    """
    values = []
    for i in self.parModis:
      values.append(i.retGranuleUR())
    for i in self._checkval(values):
      gur = self.ElementTree.SubElement(obj, 'GranuleUR')
      gur.text = i

  def valDbID(self, obj):
    """Function to add DbID

    obj = element to add DbID
    """
    values = []
    for i in self.parModis:
      values.append(i.retDbID())
    for i in self._checkval(values):
      dbid = self.ElementTree.SubElement(obj, 'DbID')
      dbid.text = i

  def valInsTime(self, obj):
    """Function to add the minimum of InsertTime

    obj = element to add InsertTime
    """
    values = []
    for i in self.parModis:
      values.append(i.retInsertTime())
    obj.text = self._minval(values)

  def valCollectionMetaData(self, obj):
    """Function to add CollectionMetaData

    obj = element to add CollectionMetaData
    """
    values = []
    for i in self.parModis:
      values.append(i.retCollectionMetaData())
    self._cicle_values(obj, self._checkvaldict(values))

  def valDataFiles(self, obj):
    """Function to add DataFileContainer

    obj = element to add DataFileContainer
    """
    values = []
    for i in self.parModis:
      values.append(i.retDataFiles())
    for i in values:
      dfc = self.ElementTree.SubElement(obj, 'DataFileContainer')
      self._cicle_values(dfc, i)

  def valPGEVersion(self, obj):
    """Function to add PGEVersion
    
    obj = element to add PGEVersion
    """
    values = []
    for i in self.parModis:
      values.append(i.retPGEVersion())
    for i in self._checkval(values):
      pge = self.ElementTree.SubElement(obj, 'PGEVersion')
      pge.text = i

  def valRangeTime(self, obj):
    """Function to add RangeDateTime

    obj = element to add RangeDateTime
    """
    values = []
    for i in self.parModis:
      values.append(i.retRangeTime())
    self._cicle_values(obj, self._checkvaldict(values))

  def valBound(self):
    """Function return the Bounding Box of mosaic
    """
    boundary = self.parModis[0].retBoundary()
    for i in range(1, len(self.parModis)):
      bound = self.parModis[i].retBoundary()
      if bound['min_lat'] < boundary['min_lat']:
        boundary['min_lat'] = bound['min_lat']
      if bound['min_lon'] < boundary['min_lon']:
        boundary['min_lon'] = bound['min_lon']
      if bound['max_lat'] > boundary['max_lat']:
        boundary['max_lat'] = bound['max_lat']
      if bound['max_lon'] > boundary['max_lon']:
        boundary['max_lon'] = bound['max_lon']
    self.boundary = boundary

  def valMeasuredParameter(self, obj):
    """Function to add ParameterName

    obj = element to add ParameterName
    """
    valuesQAStats = []
    valuesQAFlags = []
    valuesParameter = []
    for i in self.parModis:
      valuesQAStats.append(i.retMeasure()['QAStats'])
      valuesQAFlags.append(i.retMeasure()['QAFlags'])
      valuesParameter.append(i.retMeasure()['ParameterName'])
    for i in self._checkval(valuesParameter):
      pn = self.ElementTree.SubElement(obj, 'ParameterName')
      pn.text = i

  def valInputPointer(self, obj):
    """Function to add InputPointer

    obj = element to add InputPointer
    """
    for i in self.parModis:
      for v in i.retInputGranule():
        ip = self.ElementTree.SubElement(obj, 'InputPointer')
        ip.text = v

  def valPlatform(self, obj):
    """Function to add Platform elements

    obj = element to add Platform elements
    """
    valuesSName = []
    valuesInstr = []
    valuesSensor = []
    for i in self.parModis:
        valuesSName.append(i.retPlatform()['PlatformShortName'])
        valuesInstr.append(i.retPlatform()['InstrumentShortName'])
        valuesSensor.append(i.retPlatform()['SensorShortName'])
    for i in self._checkval(valuesSName):
      pn = self.ElementTree.SubElement(obj, 'PlatformShortName')
      pn.text = i

    valInstr = self._checkval(valuesInstr)
    valSens = self._checkval(valuesSensor)

    if len(valInstr) != len(valSens):
      raise IOError('Something wrong reading XML files')
    else:
      for i in range(len(valInstr)):
        ins = self.ElementTree.SubElement(obj, 'Instrument')
        pn = self.ElementTree.SubElement(ins, 'InstrumentShortName')
        pn.text = valInstr[i]
        sens = self.ElementTree.SubElement(ins, 'Sensor')
        ps = self.ElementTree.SubElement(sens, 'SensorShortName')
        ps.text = valSens[i]

  def writexml(self, outputname):
    """Write a xml file for a mosaic

    outputname = the name of xml file
    """
    # the root element
    granule = self.ElementTree.Element('GranuleMetaDataFile')
    # add DTDVersion
    self.valDTD(granule)
    # add DataCenterId
    self.valDataCenter(granule)
    # add GranuleURMetaData
    gurmd = self.ElementTree.SubElement(granule, 'GranuleURMetaData')
    # add GranuleUR
    self.valGranuleUR(gurmd)
    # add dbID
    self.valDbID(gurmd)

    # TODO ADD InsertTime LastUpdate

    # add CollectionMetaData
    cmd = self.ElementTree.SubElement(gurmd, 'CollectionMetaData')
    self.valCollectionMetaData(cmd)
    # add DataFiles
    df = self.ElementTree.SubElement(gurmd, 'DataFiles')
    self.valDataFiles(df)

    # TODO ADD ECSDataGranule

    # add PGEVersionClass
    pgevc = self.ElementTree.SubElement(gurmd, 'PGEVersionClass')
    self.valPGEVersion(pgevc)
    # add RangeDateTime
    rdt = self.ElementTree.SubElement(gurmd, 'RangeDateTime')
    self.valRangeTime(rdt)
    # SpatialDomainContainer
    sdc = self.ElementTree.SubElement(gurmd, 'SpatialDomainContainer')
    hsdc = self.ElementTree.SubElement(sdc, 'HorizontalSpatialDomainContainer')
    gp = self.ElementTree.SubElement(hsdc, 'GPolygon')
    bound = self.ElementTree.SubElement(gp, 'Boundary')
    self.valBound()
    self._addPoint(bound, 'min_lon', 'max_lat')
    self._addPoint(bound, 'max_lon', 'max_lat')
    self._addPoint(bound, 'min_lon', 'min_lat')
    self._addPoint(bound, 'max_lon', 'min_lat')
    # add MeasuredParameter
    mp = self.ElementTree.SubElement(gurmd, 'MeasuredParameter')
    mpc = self.ElementTree.SubElement(mp, 'MeasuredParameterContainer')
    self.valMeasuredParameter(mpc)
    # Platform
    pl = self.ElementTree.SubElement(gurmd, 'Platform')
    self.valPlatform(pl)

    # add PSAs
    psas = self.ElementTree.SubElement(gurmd, 'PSAs')
    # TODO ADD all PSA

    # add InputGranule and InputPointer
    ig = self.ElementTree.SubElement(gurmd, 'InputGranule')
    self.valInputPointer(ig)
    # TODO ADD BrowseProduct
    output = open(outputname, 'w')
    output.write('<?xml version="1.0" encoding="UTF-8"?>')
    output.write('<!DOCTYPE GranuleMetaDataFile SYSTEM "http://ecsinfo.gsfc.' \
    'nasa.gov/ECSInfo/ecsmetadata/dtds/DPL/ECS/ScienceGranuleMetadata.dtd">')
    output.write(self.ElementTree.tostring(granule))
    output.close()
