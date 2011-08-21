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
#  History
##################################################################
#
#  0.4.0 Fix a lot of bugs, add convertModis class to convert hdf to other
#        format and projection system (To release)
#  0.3.0 Fixed the choosing of days, change name modisClass to downModis 
#        and add parseModis (2011-05-24)
#  0.2.1 Little change in the logging option (2011-01-21)
#  0.2.0 Added logging and change something in debug methods (2010-12-01)
#  0.1.3 Correct a little problem with "Connection timed out"
#  0.1.2 Added two debug methods (2010-13-08) 
#  0.1.1 Added moveFile method (2010-07-02)
#  0.1.0 First Version of MODIS Python Class (2010-06-19)
#
##################################################################

# tilesUsed="h17v04,h17v05,h18v02,h18v03,h18v05,h19v04,h19v05"
# writePath="/home/luca/test_modis"

__version__ = '0.4.0'

from datetime import *
import string
import os
import sys
import glob
import logging
import socket
from ftplib import FTP
import ftplib
from xml.etree import ElementTree

class downModis:
  """A class to download MODIS data from NASA FTP repository"""
  def __init__(self, 
                password,
                destinationFolder,
                user = "anonymous",
                url = "e4ftl01u.ecs.nasa.gov",
                tiles = None,
                path = "MOLT/MOD11A1.005",
                today = None,
                enddate = None,
                delta = 10,
                jpg = False,
                debug = False
              ):
    """Initialization function :
        password = is your password, usually your email address
        destinationFolder = where the files will be stored
        user = your username, by default anonymous
        url = the url where to download the MODIS data
        path = the directory where the data that you want to download are 
               stored on the ftp server
        tiles = a list of tiles that you want to download, None == all tiles
        today = the day to start downloading; in order to pass a date different from
                today use the format YYYY-MM-DD
        delta = timelag i.e. the number of days starting from today 
                (backwards

        Creates a ftp instance, connects user to ftp server and goes into the 
        directory where the MODIS data are stored
    """

    # url modis
    self.url = url
    # user for download
    self.user = user
    # password for download
    self.password = password
    # directory where data are collected
    self.path = path
    # tiles to downloads
    if tiles:
        self.tiles = tiles.split(',')
    else:
        self.tiles = tiles
    # set destination folder
    if os.access(destinationFolder,os.W_OK):
      self.writeFilePath = destinationFolder
    else:
      raise IOError("Folder to store downloaded files does not exist or is not" \
    + "writeable")
    # return the name of product
    if len(self.path.split('/')) == 2:
      self.product = self.path.split('/')[1]
    elif len(self.path.split('/')) == 3:
      self.product = self.path.split('/')[2]
    # write a file with the name of file downloaded
    self.filelist = open(os.path.join(self.writeFilePath, 'listfile' \
    + self.product + '.txt'),'w')
    # set jpg download
    self.jpeg = jpg
    # today
    self.today = today
    # force the last day
    self.enday = enddate
    # delta of days
    self.delta = delta
    # status of tile download
    self.status = True
    # for debug, you can download only xml files
    self.debug = debug
    # for logging
    LOG_FILENAME = os.path.join(self.writeFilePath, 'modis' \
    + self.product + '.log')
    LOGGING_FORMAT='%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, \
    format=LOGGING_FORMAT)
    
  def connectFTP(self):
    """ Set connection to ftp server, move to path where data are stored
    and create a list of directory for all days"""
    try:
      # connect to ftp server
      self.ftp = FTP(self.url)
      self.ftp.login(self.user,self.password)
      # enter in directory
      self.ftp.cwd(self.path)
      self.dirData = []
      # return data inside directory
      self.ftp.dir(self.dirData.append)
      # reverse order of data for have first the nearest to today
      self.dirData.reverse()
      # check if dirData contain only directory, delete all files
      self.dirData = [elem.split()[-1] for elem in self.dirData if elem.startswith("d")]
      if self.debug==True:
        logging.debug("Open connection %s" % self.url)
    except EOFError:
      logging.error('Error in connection')
      self.connectFTP()

  def closeFTP(self):
    """ Close ftp connection """
    self.ftp.quit()
    self.filelist.close()
    if self.debug==True:
      logging.debug("Close connection %s" % self.url)

  def _setDirectoryIn(self,day):
    """ Enter in the directory of the day """
    try:
      self.ftp.cwd(day)
    except (ftplib.error_reply,socket.error), e:
      logging.error("Error %s entering in directory %s" % e, day)
      self._setDirectoryIn(day)

  def _setDirectoryOver(self):
    """ Come back to old path """
    try:
      self.ftp.cwd('..')
    except (ftplib.error_reply,socket.error), e:
      logging.error("Error %s when try to come back" % e)
      self._setDirectoryOver()

  def _str2date(self,strin):
      """Return a date object from a string"""
      todaySplit = strin.split('-')
      return date(int(todaySplit[0]), int(todaySplit[1]),int(todaySplit[2]))

  def _getToday(self):
    """Return the first day for start to download"""
    if self.today == None:
      # set today variable to today
      self.today = date.today()
    else:
      # set today variable to data pass from user
      self.today = self._str2date(self.today)
      # set enday variable to data
    if self.enday != None:
      self.enday = self._str2date(self.enday)
      
  def getListDays(self):
      """ Return a list of all selected days """
      self._getToday()

      today_s = self.today.strftime("%Y.%m.%d")
      # dirData is reverse sorted
      for i, d in enumerate(self.dirData):
        if d <= today_s:
          today_avail = d
          today_index = i
          break
      else:
        logging.error("No data available for requested days")
        import sys
        sys.exit()
      days = self.dirData[today_index:][:self.delta]
      # this is useful for 8/16 days data, delta could download more images
      # that you want
      if self.enday != None:
        enday_s = self.enday.strftime("%Y.%m.%d")
        delta = 0
        # it make a for cicle from the last value and find the internal delta
        #to remove file outside temporaly range
        for i in range(-(len(days)),0):
          if days[i] < enday_s:
            break
          else:
            delta = delta + 1
        # remove days outside new delta
        days = days[:delta]
      return days

  def getFilesList(self):
    """ Create a list of files to download, it is possible choose to download 
    also the jpeg files or only the hdf files"""
    def cicle_file(jpeg=False,tile=True):
      finalList = []
      for i in self.listfiles:
        File = i.split('.')
        # distinguish jpeg files from hdf files by the number of index 
        # where find the tile index
        if not tile and not (File.count('jpg') or File.count('BROWSE')):
          finalList.append(i)
        if tile and self.tiles.count(File[3]) == 1 and jpeg: #is a jpeg of tiles number
          finalList.append(i)
        if tile and self.tiles.count(File[2]) == 1: #is a hdf of tiles number
          finalList.append(i)
      return finalList

    # return the file's list inside the directory of each day
    try:
      self.listfiles = self.ftp.nlst() 
      # download also jpeg
      if self.jpeg:
        # finallist is ugual to all file with jpeg file
        if not self.tiles:
          finalList = self.listfiles
        # finallist is ugual to tiles file with jpeg file
        else:
          finalList = cicle_file(jpeg=True)
      # not download jpeg
      else:
        if not self.tiles:
          finalList = cicle_file(tile=False)          
        else:
          finalList = cicle_file()
      if self.debug==True:
        logging.debug("The number of file to download is: %i" % len(finalList))
      return finalList
    except (ftplib.error_reply,socket.error), e:
      logging.error("Error %s when try to receive list of files" % e)
      self.getFilesList()

  def _checkDataExist(self,listNewFile, move = 0):
    """ Check if a data already exists in the directory of download 
    Move serve to know if function is called from download or move function"""
    fileInPath = []
    # add all files in the directory where we will save new modis data
    for f in os.listdir(self.writeFilePath):
      if os.path.isfile(os.path.join(self.writeFilePath, f)):
        fileInPath.append(f)
    # different return if this method is used from downloadsAllDay() or 
    # moveFile()
    if move == 0:
      listOfDifferent = list(set(listNewFile) - set(fileInPath))
    elif move == 1:
      listOfDifferent = list(set(fileInPath) - set(listNewFile))
    return listOfDifferent

  def _getNewerVersion(self,oldFile,newFile):
    """ Return newer version of a file"""
    oldFileSplit = oldFile.split('.')
    newFileSplit = newFile.split('.')
    if oldFileSplit[4] > newFileSplit[4]:
      return oldFile
    else:
      return newFile

  def downloadFile(self,filDown,filSave):
    """Download the single file"""
    #try to download file
    try:
      self.ftp.retrbinary("RETR " + filDown, filSave.write)
      self.filelist.write("%s\n" % filDown)
      if self.debug==True:
        logging.debug("File %s downloaded" % filDown)
    #if it have an error it try to download again the file
    except (ftplib.error_reply,socket.error), e:
      logging.error("Cannot download %s, retry.." % filDown)
      self.connectFTP()
      self.downloadFile(filDown,filSave)

  def dayDownload(self,listFilesDown):
    """ Downloads tiles are in files_hdf_consider """
    # for each file in files' list
    for i in listFilesDown:
        fileSplit = i.split('.')
        filePrefix = fileSplit[0] + '.' + fileSplit[1] + '.' + fileSplit[2] \
        + '.' + fileSplit[3]
        #for debug, download only xml
        if (self.debug and fileSplit[-1] == 'xml') or not self.debug:
          # check data exists in the return directory, if it doesn't exists
          oldFile = glob.glob1(self.writeFilePath, filePrefix + "*" \
          + fileSplit[-1])
          numFiles = len(oldFile)
          if numFiles == 0:
            file_hdf = open(os.path.join(self.writeFilePath,i), "wb")
          elif numFiles == 1:
            # check the version of file  
            fileDown = self._getNewerVersion(oldFile[0],i)
            if fileDown != oldFile[0]:
              os.remove(os.path.join(self.writeFilePath,oldFile[0]))
              file_hdf = open(os.path.join(self.writeFilePath,fileDown), "wb")
          elif numFiles > 1:
            logging.error("There are to much files for %s" % i)
            #raise EOFError("There are to much file with the same prefix")
          if numFiles == 0 or (numFiles == 1 and fileDown != oldFile[0]):
            self.downloadFile(i,file_hdf)

  def downloadsAllDay(self):
    """ Downloads all the tiles considered """
    #return the days to download
    days = self.getListDays()
    if self.debug==True:
      logging.debug("The number of days to download is: %i" % len(days))
    #for each day
    for day in days:
      #enter in the directory of day
      self._setDirectoryIn(day)
      #obtain list of all files
      listAllFiles = self.getFilesList()
      #obtain list of files to download
      listFilesDown = self._checkDataExist(listAllFiles)
      #download files for a day
      self.dayDownload(listFilesDown)
      self._setDirectoryOver()
    self.closeFTP()
    if self.debug==True:
      logging.debug("Download terminated")
    return 0

  def debugLog(self):
    # create logger
    logger = logging.getLogger("PythonLibModis debug")
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - " \
                + "%(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger

  def debugDays(self):
    """This function is useful to debug the number of days"""
    logger = debugLog()
    days = self.getListDays()
    # if lenght of list of days and the delta of day they are different
    if len(days) != self.delta:
      # for each day
      for i in range(1,self.delta+1):
        # calculate the current day
        delta = timedelta(days = i)
        day = self.today - delta
        day = day.strftime("%Y.%m.%d") 
        # check if day is in the days list
        if day not in days:
          logger.critical("This day %s is not present on list" % day)
    # the lenght of list of days and delta are ugual
    else:
      logger.info("All right!!")
    
  def debugMaps(self):
    """This function is useful to debug the number of maps to download for 
    each day"""
    logger = debugLog()
    days = self.getListDays()
    for day in days:
      self._setDirectoryIn(day)
      listAllFiles = self.getFilesList()
      string = day + ": " + str(len(listAllFiles)) + "\n"
      logger.debug(string)
      self._setDirectoryOver()   

class parseModis:
  """Class to parse MODIS xml files, it also can create the parameter 
    configuration file for resampling with the MRT software
  """
  def __init__(self, filename):
    """Initialization function :
       filename = the name of MODIS hdf file
    """
    if os.path.exists(filename):
      # hdf name
      self.hdfname = filename
    else:
      raise IOError('%s not exists' % self.hdfname)

    if os.path.exists(self.hdfname + '.xml'):
      # xml hdf name
      self.xmlname = self.hdfname + '.xml'
    else:
      raise IOError('%s not exists' % self.hdfname + '.xml')

    # tif name for the output file for resample MRT software
    self.tifname = self.hdfname.replace('.hdf','.tif')
    with open(self.xmlname) as f:
      self.tree = ElementTree.parse(f)
    # return the code of tile for conf file
    self.code = os.path.split(self.hdfname)[1].split('.')[-2]
    self.path = os.path.split(self.hdfname)[0]
    ## lists of parameters accepted by resample MRT software
    # projections
    self.proj_list = ('GEO', 'HAM', 'IGH', 'ISIN', 'LA', 'LCC', 'MOL', 'PS', 
                      'SIN','TM', 'UTM', 'MERCAT')
    # resampling
    self.resam_list = ('NEAREST_NEIGHBOR', 'BICUBIC', 'CUBIC_CONVOLUTION', 'NONE')
    self.resam_list_swath = ('NN', 'BI', 'CC')
    
    # datum
    self.datum_list = ('NONE', 'NAD27', 'NAD83', 'WGS66', 'WGS72', 'WGS84')
    self.sphere_list = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)

  def __str__(self):
    """Print the file without xml tags"""
    retString = ""
    try:
      for node in self.tree.iter():
        if node.text.strip() != '':
          retString = "%s = %s\n" % (node.tag,node.text) 
    except:
      for node in self.tree.getiterator():
        if node.text.strip() != '':
          retString = "%s = %s\n" % (node.tag,node.text) 
    return retString

  def _getRoot(self):
    """Set the root element"""
    self.rootree = self.tree.getroot()

  def retDTD(self):
    """Return the DTDVersion element"""
    self._getRoot()
    return self.rootree.find('DTDVersion').text

  def retDataCenter(self):
    """Return the DataCenterId element"""
    self._getRoot()
    return self.rootree.find('DataCenterId').text

  def _getGranule(self):
    """Set the GranuleURMetaData element"""
    self._getRoot()
    self.granule = self.rootree.find('GranuleURMetaData')

  def retGranuleUR(self):
    """Return the GranuleUR element"""
    self._getGranule()
    return self.granule.find('GranuleUR').text

  def retDbID(self):
    """Return the DbID element"""
    self._getGranule()
    return self.granule.find('DbID').text

  def retInsertTime(self):
    """Return the DbID element"""
    self._getGranule()
    return self.granule.find('InsertTime').text

  def retLastUpdate(self):
    """Return the DbID element"""
    self._getGranule()
    return self.granule.find('LastUpdate').text

  def retCollectionMetaData(self):
    """Return the CollectionMetaData element"""
    self._getGranule()
    collect = {}
    for i in self.granule.find('CollectionMetaData').getiterator():
      if i.text.strip() != '':
        collect[i.tag] = i.text
    return collect

  def retDataFiles(self):
    """Return the DataFiles element"""
    self._getGranule()
    collect = {}
    datafiles = self.granule.find('DataFiles')
    for i in datafiles.find('DataFileContainer').getiterator():
      if i.text.strip() != '':
        collect[i.tag] = i.text
    return collect

  def retDataGranule(self):
    """Return the ECSDataGranule elements"""
    self._getGranule()
    datagran = {}
    for i in self.granule.find('ECSDataGranule').getiterator():
      if i.text.strip() != '':
        datagran[i.tag] = i.text
    return datagran

  def retPGEVersion(self):
    """Return the PGEVersion element"""
    self._getGranule()
    return self.granule.find('PGEVersionClass').find('PGEVersion').text

  def retRangeTime(self):
    """Return the RangeDateTime elements inside a dictionary with the element
       name like dictionary key
    """
    self._getGranule()
    rangeTime = {}
    for i in self.granule.find('RangeDateTime').getiterator():
      if i.text != None:
        if i.text.strip() != '':
          rangeTime[i.tag] = i.text
    return rangeTime

  def retBoundary(self):
    """Return the maximum extend of the MODIS file inside a dictionary"""
    self._getGranule()
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
      self.boundary.append({'lat': la, 'lon':lo})
    extent = {'min_lat':min(lat),'max_lat':max(lat),'min_lon':min(lon),
                'max_lon':max(lon)}
    return extent

  def retMeasure(self):
    """Return statistics inside a dictionary"""
    value = {}
    self._getGranule()
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
    """Return the platform values inside a dictionary."""
    value = {}
    self._getGranule()
    plat = self.granule.find('Platform')
    value['PlatformShortName'] = plat.find('PlatformShortName').text
    instr = plat.find('Instrument')
    value['InstrumentShortName'] = instr.find('InstrumentShortName').text
    sensor = instr.find('Sensor')
    value['SensorShortName'] = sensor.find('SensorShortName').text
    return value

  def retPSA(self):
    """Return the PSA values inside a dictionary, the PSAName is he key and
       and PSAValue is the value
    """
    value = {}
    self._getGranule()
    psas = self.granule.find('PSAs')
    for i in psas.findall('PSA'):
      value[i.find('PSAName').text] = i.find('PSAValue').text
    return value

  def retInputGranule(self):
    """Return the input files used to process the considered file"""
    value = []
    self._getGranule()
    for i in self.granule.find('InputGranule').getiterator():
      if i.tag != 'InputGranule':
        value.append(i.text)
    return value

  def retBrowseProduct(self):
    """Return the PGEVersion element"""
    self._getGranule()
    return self.granule.find('BrowseProduct').find('BrowseGranuleId').text

  def metastring(self):
    """Return a string with some metadata. The output it's used on GRASS GIS
       to set the metadata with r.support command
    """
    date = self.retRangeTime()
    qa = self.retMeasure()
    pge = self.retPGEVersion()
    daynight = self.retDataGranule()
    stri = "Date:%s;BeginningTime:%s;EndingTime:%s;DayNightFlag:%s;"
    stri += "QAPercentCloudCover:%s;QAPercentMissingData:%s;PGEVersion:%s"
    out = stri % ( date['RangeBeginningDate'], date['RangeBeginningTime'], 
          date['RangeEndingTime'], daynight['DayNightFlag'], 
          qa['QAStats']['QAPercentCloudCover'], 
          qa['QAStats']['QAPercentMissingData'], pge)
    return out

  def confResample(self, spectral, res = None, output = None, datum = 'WGS84',
                  resampl = 'NEAREST_NEIGHBOR', projtype = 'GEO',  utm = None,
                  projpar = '( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 )',
                  ):
    """Create the parameter file to use with resample MRT software to create
       tif file
        spectral = the spectral subset to use, look the product table to 
                   understand the layer that you want use. 
                   For example: 
                    - NDVI ( 1 1 1 0 0 0 0 0 0 0 0 0) copy only layer NDVI, EVI 
                      and QA VI the other layers are not used
                    - LST ( 1 1 0 0 1 1 0 0 0 0 0 0 ) copy only layer daily and
                      nightly temperature and QA
        res = the resolution for the output file, it must be set in the map 
              unit of output projection system. The software will use the original
              resolution of input file if res it isn't set
        output = the output name, if it doesn't set will use the prefix name of 
                 input hdf file
        utm = the UTM zone if projection system is UTM
        resampl = the type of resampling, the valid values are: NN (nearest 
                  neighbor), BI (bilinear), CC (cubic convolution)
        projtype = the output projection system, the valid values are: AEA 
                   (Albers Equal Area), ER (Equirectangular), GEO (Geographic 
                   Latitude/Longitude), HAM (Hammer), ISIN (Integerized Sinusoidal), 
                   IGH (Interrupted Goode Homolosine), LA (Lambert Azimuthal), 
                   LCC (LambertConformal Conic), MERCAT (Mercator), MOL (Mollweide), 
                   PS (Polar Stereographic), SIN ()Sinusoidal), UTM (Universal 
                   TransverseMercator)
        datum = the datum to use, the valid values are: NAD27, NAD83, WGS66,
                WGS76, WGS84, NONE
        projpar = a list of projection parameters
        """
    # output name
    if not output:
      fileout = self.tifname
    else:
      if output.find('.tif') == -1:
        fileout = os.path.join(self.path, output + '.tif')
      else: 
        fileout = os.path.join(self.path, output)
    # the name of the output parameters files for resample MRT software
    filename = os.path.join(self.path,'%s_mrt_resample.conf' % self.code)
    # if the file already exists it remove it 
    if os.path.exists(filename):
      os.remove(filename)
    # open the file
    conFile = open(filename, 'w')
    conFile.write("INPUT_FILENAME = %s\n" % self.hdfname)
    conFile.write("SPECTRAL_SUBSET = %s\n" % spectral)
    conFile.write("SPATIAL_SUBSET_TYPE = INPUT_LAT_LONG\n")
    # return the boundary from the input xml file
    bound = self.retBoundary()
    # Order:  UL: N W  - LR: S E
    conFile.write("SPATIAL_SUBSET_UL_CORNER = ( %f %f )\n" % (bound['max_lat'],
                                                              bound['min_lon']))
    conFile.write("SPATIAL_SUBSET_LR_CORNER = ( %f %f )\n" % (bound['min_lat'],
                                                              bound['max_lon']))
    conFile.write("OUTPUT_FILENAME = %s\n" % fileout)
    # if resampl is in resam_list set the parameter otherwise return an error
    if resampl in self.resam_list:
      conFile.write("RESAMPLING_TYPE = %s\n" % resampl)
    else:
      raise IOError('The resampling type %s is not supportet.\n' \
                   'The resampling type supported are %s' % (resampl,resam_list))
    # if projtype is in proj_list set the parameter otherwise return an error
    if projtype in self.proj_list:
      conFile.write("OUTPUT_PROJECTION_TYPE = %s\n" % projtype)
    else:
      raise IOError('The projection type %s is not supported.\n' \
                   'The projections supported are %s' % (projtype,proj_list))
    conFile.write("OUTPUT_PROJECTION_PARAMETERS = %s\n" % projpar)
    # if datum is in datum_list set the parameter otherwise return an error
    if datum in self.datum_list:
      conFile.write("DATUM = %s\n" % datum)
    else:
      raise IOError('The datum %s is not supported.\n' \
                   'The datum supported are %s' % (datum,datum_list))
    # if utm is not None write the UTM_ZONE parameter in the file
    if utm:
      conFile.write("UTM_ZONE = %s\n" % utm)
    # if res is not None write the OUTPUT_PIXEL_SIZE parameter in the file
    if res:
      conFile.write("OUTPUT_PIXEL_SIZE = %i\n" % res)
    conFile.close()
    return filename

  def confResample_swath(self, sds, geoloc, res, output = None, 
                  sphere = '8', resampl = 'NN', projtype = 'GEO',  utm = None,
                  projpar = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
                  ):
    """Create the parameter file to use with resample MRT software to create
       tif file
        sds = Name of band/s (Science Data Set) to resample
        geoloc = Name geolocation file (example MOD3, MYD3)
        res = the resolution for the output file, it must be set in the map 
              unit of output projection system. The software will use the original
              resolution of input file if res it isn't set
        output = the output name, if it doesn't set will use the prefix name of 
                 input hdf file
        sphere = Output sphere number. Valid options are: 
                 0=Clarke 1866, 1=Clarke 1880, 2=Bessel, 3=International 1967, 
                 4=International 1909, 5=WGS 72, 6=Everest, 7=WGS 66, 
                 8=GRS1980/WGS 84, 9=Airy, 10=Modified Everest, 11=Modified Airy, 
                 12=Walbeck, 13=Southeast Asia, 14=Australian National, 
                 15=Krassovsky, 16=Hough, 17=Mercury1960, 18=Modified Mercury1968, 
                 19=Sphere 19 (Radius 6370997), 20=MODIS Sphere (Radius 6371007.181)
        resampl = the type of resampling, the valid values are: NN (nearest 
                  neighbor), BI (bilinear), CC (cubic convolution)
        projtype = the output projection system, the valid values are: 
                   AEA (Albers Equal Area), ER (Equirectangular), 
                   GEO (Geographic Latitude/Longitude), HAM (Hammer), 
                   ISIN (Integerized Sinusoidal),IGH (Interrupted Goode Homolosine), 
                   LA (Lambert Azimuthal), LCC (LambertConformal Conic),
                   MERCAT (Mercator), MOL (Mollweide), PS (Polar Stereographic),
                   SIN ()Sinusoidal), UTM (Universal TransverseMercator)
        utm = the UTM zone if projection system is UTM
        projpar = a list of projection parameters
        """
    # output name
    if not output:
      fileout = self.tifname
    else:
      fileout = output
    # the name of the output parameters files for resample MRT software
    filename = os.path.join(self.path,'%s_mrt_resample.prm' % self.code)
    # if the file already exists it remove it 
    if os.path.exists(filename):
      os.remove(filename)
    # open the file
    conFile = open(filename, 'w')
    conFile.write("INPUT_FILENAME = %s\n" % self.hdfname)
    conFile.write("GEOLOCATION_FILENAME = %s\n" % geoloc)
    conFile.write("INPUT_SDS_NAME = %s\n" % sds)
    conFile.write("OUTPUT_SPATIAL_SUBSET_TYPE = LAT_LONG\n")
    # return the boundary from the input xml file
    bound = self.retBoundary()
    # Order:  UL: N W  - LR: S E
    conFile.write("OUTPUT_SPACE_UPPER_LEFT_CORNER (LONG LAT) = %f %f\n" % (bound['max_lat'],
                                                              bound['min_lon']))
    conFile.write("OUTPUT_SPACE_LOWER_RIGHT_CORNER (LONG LAT) = %f %f\n" % (bound['min_lat'],
                                                              bound['max_lon']))
    conFile.write("OUTPUT_FILENAME = %s\n" % fileout)
    conFile.write("OUTPUT_FILE_FORMAT = GEOTIFF_FMT\n")
    # if resampl is in resam_list set the parameter otherwise return an error
    if resampl in self.resam_list_swath:
      conFile.write("KERNEL_TYPE (CC/BI/NN) = %s\n" % resampl)
    else:
      raise IOError('The resampling type %s is not supportet.\n' \
                   'The resampling type supported are %s' % (resampl,self.resam_list_swath))
    # if projtype is in proj_list set the parameter otherwise return an error
    if projtype in self.proj_list:
      conFile.write("OUTPUT_PROJECTION_NUMBER = %s\n" % projtype)
    else:
      raise IOError('The projection type %s is not supported.\n' \
                   'The projections supported are %s' % (projtype,proj_list))
    conFile.write("OUTPUT_PROJECTION_PARAMETER = %s\n" % projpar)
    # if sphere is in sphere_list set the parameter otherwise return an error
    if int(sphere) in self.sphere_list:
      conFile.write("OUTPUT_PROJECTION_SPHERE = %s\n" % sphere)
    else:
      raise IOError('The sphere %s is not supported.\n' \
                   'The spheres supported are %s' % (sphere,self.sphere_list))
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
  """A class to some variable for the xml file of a mosaic
  """
  def __init__(self,hdflist):
    self.ElementTree = ElementTree
    self.hdflist = hdflist
    self.parModis = []
    self.nfiles = 0
    for i in hdflist:
      self.parModis.append(parseModis(i))
      self.nfiles += 1

  def _retValues(self, funct):
    values = []
    for i in self.parModis:
      values.append(getattr(i,funct)())
    return values

  def _checkval(self,vals):
    """Internal function to return the different values from a list"""
    if vals.count(vals[0]) == self.nfiles:
      return [vals[0]]
    else:
      outvals = []
      for i in vals:
        if outvals.count(i) == 0:
          outvals.append(i)
      return outvals
      
  def _checkvaldict(self,vals):
    """Internal function to return the different values from a dict"""
    keys = vals[0].keys()
    outvals = {}
    for k in keys:
      valtemp = []
      for v in vals:
        valtemp.append(v[k])
      if valtemp.count(valtemp[0]) == self.nfiles:
        outvals[k] = valtemp[0]
      else:
        raise IOError('Something wrong reading XML files')
    return outvals

  def _minval(self, vals):
    """Internal function to return the minimun value"""
    outval = vals[0]
    for i in range(1,len(vals)):
      if outval > vals[i]:
        outval = vals[i]
    return outval
    
  def _maxval(self, vals):
    """Internal function to return the maximum value"""
    outval = vals[0]
    for i in range(1,len(vals)):
      if outval < vals[i]:
        outval = vals[i]
    return outval

  def _meanval(self,vals):
    """Internal function to return the mean value"""
    out = 0
    for v in vals:
      out += float(v)
    return out/len(vals)

  def _cicle_values(self, ele,values):
    """Function to add values from a dictionary"""
    for k,v in values.iteritems():
      elem = self.ElementTree.SubElement(ele,k)
      elem.text = v

  def _moreValues(self, obj, fun, ele):
    """Funtion to add elemets to the xml from a list"""
    values = self._retValues(fun)
    for i in self._checkval(values):
      dtd = self.ElementTree.SubElement(obj,ele)
      dtd.text = i

  def _moreValuesCicle(self, obj, fun):
    """Funtion to add elemets to the xml from a dict"""
    values = self._retValues(fun)
    self._cicle_values(obj,self._checkvaldict(values))

  def _valInsertTime(self, obj):
    """Function to add InsertTime value"""
    values = self._retValues('retInsertTime')
    time = self.ElementTree.SubElement(obj,'InsertTime')
    minimum = self._minval(values)
    time.text = minimum

  def _valLastUpdate(self, obj):
    """Function to add InsertTime value"""
    values = self._retValues('retLastUpdate')
    time = self.ElementTree.SubElement(obj,'LastUpdate')
    minimum = self._maxval(values)
    time.text = minimum

  def _valDataFiles(self, obj):
    """Function to add DataFileContainer values"""
    values = self._retValues('retDataFiles')
    for i in values:
      dfc = self.ElementTree.SubElement(obj, 'DataFileContainer')
      self._cicle_values(dfc,i)

  def _valPGEVersion(self,obj):
    """Function to add PGEVersion values"""
    values = self._retValues('retPGEVersion')
    for i in self._checkval(values):
      pge = self.ElementTree.SubElement(obj,'PGEVersion')
      pge.text = i

  def _valBound(self):
    """Return the maximun extent of mosaic"""
    boundary = self.parModis[0].retBoundary()
    for i in range(1,len(self.parModis)):
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

  def _addPoint(self,obj,lon,lat):
    """Function to add a single point of maximum extent"""
    pt = self.ElementTree.SubElement(obj, 'Point')
    ptlon = self.ElementTree.SubElement(pt, 'PointLongitude')
    ptlon.text = str(self.boundary[lon])
    ptlat = self.ElementTree.SubElement(pt, 'PointLatitude')
    ptlat.text = str(self.boundary[lat])

  def _valMeasuredParameter(self,obj):
    """Function to add MeasuredParameter values"""
    valuesQAStats = {}
    valuesQAFlags = {}
    valuesParameter = []
    keysQAStats = self.parModis[0].retMeasure()['QAStats'].keys()
    for i in keysQAStats:
      valuesQAStats[i] = []
    keysQAFlags = self.parModis[0].retMeasure()['QAFlags'].keys()
    for i in keysQAFlags:
      valuesQAFlags[i] = []
    for i in self.parModis:
      for k,v in i.retMeasure()['QAStats'].iteritems():
        valuesQAStats[k].append(v)
      for k,v in i.retMeasure()['QAFlags'].iteritems():
        valuesQAFlags[k].append(v)
      valuesParameter.append(i.retMeasure()['ParameterName'])
    for i in self._checkval(valuesParameter):
      pn = self.ElementTree.SubElement(obj,'ParameterName')
      pn.text = i
    qstats = self.ElementTree.SubElement(obj,'QAStats')
    for k, v in valuesQAStats.iteritems():
      qstat = self.ElementTree.SubElement(qstats,k)
      qstat.text = str(self._meanval(v))

  def _valInputPointer(self,obj):
    """Function to add InputPointer values"""
    for i in self.parModis:
      for v in i.retInputGranule():
        ip = self.ElementTree.SubElement(obj,'InputPointer')
        ip.text = v

  def _valPlatform(self, obj):
    """Function to add Platform values"""
    valuesSName = []
    valuesInstr = []
    valuesSensor = []
    for i in self.parModis:
      valuesSName.append(i.retPlatform()['PlatformShortName'])
      valuesInstr.append(i.retPlatform()['InstrumentShortName'])
      valuesSensor.append(i.retPlatform()['SensorShortName'])
    for i in self._checkval(valuesSName):
      pn = self.ElementTree.SubElement(obj,'PlatformShortName')
      pn.text = i
    valInstr = self._checkval(valuesInstr)
    valSens = self._checkval(valuesSensor)
    if len(valInstr) != len(valSens):
      raise IOError('Something wrong reading XML files')
    else:
      for i in range(len(valInstr)):
        ins = self.ElementTree.SubElement(obj,'Instrument')
        pn = self.ElementTree.SubElement(ins,'InstrumentShortName')
        pn.text = valInstr[i]
        sens = self.ElementTree.SubElement(ins,'Sensor')
        ps = self.ElementTree.SubElement(sens,'SensorShortName')
        ps.text = valSens[i]

  def _valPSA(self, obj):
    """Function to add PSA values"""
    values = {}
    # add all keys
    keys = self.parModis[0].retPSA().keys()
    for i in keys:
      values[i] = []
    # for each key create a list of values
    for i in self.parModis:
      for k,v in i.retPSA().iteritems():
        values[k].append(v)
    # these values could be different so they must be added all
    valApp = ['TileID','HORIZONTALTILENUMBER','VERTICALTILENUMBER']
    for v in valApp:
      for i in values[v]:
        psa = self.ElementTree.SubElement(obj,'PSA')
        psaname = self.ElementTree.SubElement(psa, 'PSAName')
        psaname.text = v
        psavalue = self.ElementTree.SubElement(psa, 'PSAValue')
        psavalue.text = i
    # add CLOUD_CONTAMINATED_LST_SCREENED, if one of values is NO set NO otherwise YES
    try:
      psa = self.ElementTree.SubElement(obj,'PSA')
      psaname = self.ElementTree.SubElement(psa, 'PSAName')
      psaname.text = 'CLOUD_CONTAMINATED_LST_SCREENED'
      psavalue = self.ElementTree.SubElement(psa, 'PSAValue')
      if values['CLOUD_CONTAMINATED_LST_SCREENED'].count('NO') == 0:
        psavalue.text = 'NO'
      else:
        psavalue.text = 'YES'
    except:
      pass
    # for these values calculate the mean value
    valMean = ['QAFRACTIONGOODQUALITY', 'QAPERCENTNOTPRODUCEDOTHER', 'N_GRAN_POINTERS',
    'QAFRACTIONNOTPRODUCEDCLOUD','QAPERCENTOTHERQUALITY','QAFRACTIONNOTPRODUCEDOTHER',
    'QAPERCENTNOTPRODUCEDCLOUD','QAFRACTIONOTHERQUALITY','QAPERCENTGOODQUALITY']
    for v in valMean:
      if v in values.keys():
        psa = self.ElementTree.SubElement(obj,'PSA')
        psaname = self.ElementTree.SubElement(psa, 'PSAName')
        psaname.text = v
        psavalue = self.ElementTree.SubElement(psa, 'PSAValue')
        psavalue.text = str(self._meanval(values[v]))
      
  def writexml(self,outputname):
    """Return a xml file for a mosaic"""
    # the root element
    granule = self.ElementTree.Element('GranuleMetaDataFile')
    # add DTDVersion
    self._moreValues(granule, 'retDTD', 'DTDVersion')
    # add DataCenterId
    self._moreValues(granule, 'retDataCenter', 'DataCenterId')
    # add GranuleURMetaData
    gurmd = self.ElementTree.SubElement(granule,'GranuleURMetaData')
    # add GranuleUR
    self._moreValues(granule, 'retGranuleUR', 'GranuleUR')
    # add dbID
    self._moreValues(granule, 'retDbID', 'DbID')

    self._valInsertTime(granule)
    self._valLastUpdate(granule)
    # CHECK InsertTime LastUpdate

    # add CollectionMetaData
    cmd = self.ElementTree.SubElement(gurmd,'CollectionMetaData')
    self._moreValuesCicle(cmd,'retCollectionMetaData')
    # add DataFiles
    df = self.ElementTree.SubElement(gurmd,'DataFiles')
    self._valDataFiles(df)
    
    # TODO ADD ECSDataGranule
    
    # add PGEVersionClass
    pgevc = self.ElementTree.SubElement(gurmd,'PGEVersionClass')
    self._valPGEVersion(pgevc)
    # add RangeDateTime
    rdt = self.ElementTree.SubElement(gurmd,'RangeDateTime')
    self._moreValuesCicle(rdt,'retRangeTime')
    # SpatialDomainContainer
    sdc = self.ElementTree.SubElement(gurmd,'SpatialDomainContainer')
    hsdc = self.ElementTree.SubElement(sdc,'HorizontalSpatialDomainContainer')
    gp = self.ElementTree.SubElement(hsdc,'GPolygon')
    bound = self.ElementTree.SubElement(gp,'Boundary')
    self._valBound()
    self._addPoint(bound,'min_lon','max_lat')
    self._addPoint(bound,'max_lon','max_lat')
    self._addPoint(bound,'min_lon','min_lat')
    self._addPoint(bound,'max_lon','min_lat')
    # add MeasuredParameter
    mp = self.ElementTree.SubElement(gurmd,'MeasuredParameter')
    mpc = self.ElementTree.SubElement(mp,'MeasuredParameterContainer')
    self._valMeasuredParameter(mpc)
    
    # TODO ADD qflags

    # Platform
    pl = self.ElementTree.SubElement(gurmd,'Platform')
    self._valPlatform(pl)
    # add PSAs
    psas = self.ElementTree.SubElement(gurmd,'PSAs')
    self._valPSA(psas)
    # add InputGranule and InputPointer
    ig = self.ElementTree.SubElement(gurmd,'InputGranule')
    self._valInputPointer(ig)
    # TODO ADD BrowseProduct
    # write output file
    output = open(outputname, 'w')
    output.write('<?xml version="1.0" encoding="UTF-8"?>')
    output.write('<!DOCTYPE GranuleMetaDataFile SYSTEM "http://ecsinfo.gsfc.nasa.gov/ECSInfo/ecsmetadata/dtds/DPL/ECS/ScienceGranuleMetadata.dtd">')
    output.write(self.ElementTree.tostring(granule))
    output.close()

class convertModis:
  """A class to convert modis data from hdf to tif using resample (from MRT tools)
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

  def _executable(self):
    """Return the executable of resample MRT software
    """
    if sys.platform.count('linux') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'resample')):
        return os.path.join(self.mrtpathbin,'resample')
    elif sys.platform.count('win32') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'resample.exe')):
        return os.path.join(self.mrtpath,'resample.exe')

  def run(self):
    """Exec the process"""
    import subprocess
    execut = self._executable()
    if not os.path.exists(execut):
      raise IOError('The path %s not exists, could be an erroneus path or '\
                    + 'software') % execut
    else:
      subprocess.call([execut,'-p',self.conf])
    return "The hdf file %s was converted" % self.name

class createMosaic:
  """A class to convert a mosaic of different modis tiles"""
  def __init__(self,
              listfile,
              outprefix,
              mrtpath,
              subset = False
              ):
    # check if the hdf file exists
    if os.path.exists(listfile):
      self.basepath = os.path.split(listfile)[0]
      self.listfiles = listfile
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
    self.outxml = os.path.join(self.basepath, self.out + '.xml')
    self.subset = subset

  def _write_mosaic_xml(self):
    self.finalfile = open(os.path.join(self.basepath,'mosaic%i' % os.getpid()),'w')
    listHDF = []
    for i in self.HDFfiles:
      if i.find(self.basepath) == -1:
        print "Attection maybe you are not using full path in the HDF file list"
        listHDF.append(os.path.join(self.basepath,i.strip()))
        self.finalfile.write("%s\n" % os.path.join(self.basepath,i.strip()))
      else:
        listHDF.append(i.strip())
        self.finalfile.write("%s\n" % i.strip())
    self.finalfile.close()
    pmm = parseModisMulti(listHDF)
    pmm.writexml(self.outxml)

  def _executable(self):
    """Return the executable of mrtmosaic MRT software
    """
    if sys.platform.count('linux') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'mrtmosaic')):
        return os.path.join(self.mrtpathbin,'mrtmosaic')
    elif sys.platform.count('win32') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'mrtmosaic.exe')):
        return os.path.join(self.mrtpath,'mrtmosaic.exe')

  def run(self):
    """Exect the mosaic process"""
    import subprocess
    execut = self._executable()
    if not os.path.exists(execut):
      raise IOError('The path %s not exists, could be an erroneus path or '\
                    + 'software') % execut
    else:
      self._write_mosaic_xml()
      if self.subset:
        subprocess.call([execut,'-i',self.finalfile.name,'-o',self.out,'-s',self.subset], 
                        stderr = subprocess.STDOUT)
      else:
        subprocess.call([execut,'-i',self.finalfile.name,'-o',self.out], stderr = 
                        subprocess.STDOUT)
      #os.remove(self.finalfile)
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

  def _executable(self):
    """Return the executable of resample MRT software
    """
    if sys.platform.count('linux') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'swath2grid')):
        return os.path.join(self.mrtpathbin,'swath2grid')
    elif sys.platform.count('win32') != -1:
      if os.path.exists(os.path.join(self.mrtpathbin,'swath2grid.exe')):
        return os.path.join(self.mrtpath,'swath2grid.exe')

  def run(self):
    """Exec the process"""
    import subprocess
    execut = self._executable()
    if not os.path.exists(execut):
      raise IOError('The path %s not exists, could be an erroneus path or '\
                    + 'software') % execut
    else:
      subprocess.call([execut,'-pf=%s' % self.conf])
    return "The hdf file %s was converted" % self.name
