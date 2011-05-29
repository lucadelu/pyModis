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
#  History
##################################################################
#
#  0.3.0 Fix the choosing of days, change name modisClass to downModis 
#        and add parseModis (2011-05-24)
#  0.2.1 Little change in the logging option (2011-01-21)
#  0.2.0 Add logging and change something in debug methods (2010-12-01)
#  0.1.3 Correct a little problem with "Connection timed out"
#  0.1.2 Add two debug methods (2010-13-08) 
#  0.1.1 Add moveFile method (2010-07-02)
#  0.1.0 First Version of Modis Class (2010-06-19)
#
##################################################################

# tilesUsed="h17v04,h17v05,h18v02,h18v03,h18v05,h19v04,h19v05"
# writePath="/home/luca/test_modis"

__version__ = '0.3.0'

from datetime import *
from ftplib import FTP
import string
import os
import glob
import logging
import socket
import ftplib

class downModis:
  """A class to download modis data from nasa ftp repository"""
  def __init__(self, 
                user,
                password,
                destinationFolder,
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
        user=is your username
        password=is your password
        destinationFolder=where your file are storage
        url=the url where download data
        path=the directory where the data that you want download are 
             storaged in the ftp server
        tiles=a list of tiles that you want downloads, None == all tiles
        today=the day to start download, to pass a date different to 
              today use this format year-month-day
        delta=timelag i.e. the number of days starting from today 
              (backward)

        Create ftp istance, connect user to ftp server and go to the 
        directory where data are storage
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
    self.tiles = tiles
    # set destination folder
    if os.access(destinationFolder,os.W_OK):
      self.writeFilePath = destinationFolder
    else:
      raise IOError("Folder to write downloaded files doesn't exist or is not" \
    + "writeable")
    # write a file with the name of file downloaded
    if len(self.path.split('/')) == 2:
      self.product = self.path.split('/')[1]
    elif len(self.path.split('/')) == 3:
      self.product = self.path.split('/')[2]
    self.fileslist = open(os.path.join(self.writeFilePath, 'listfile' \
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
    """ set connection to ftp server, move to path where data are storaged
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
    self.fileslist.close()
    if self.debug==True:
      logging.debug("Close connection %s" % self.url)

  def setDirectoryIn(self,day):
    """ Enter in the directory of the day """
    try:
      self.ftp.cwd(day)
    except (ftplib.error_reply,socket.error), e:
      logging.error("Error %s entering in directory %s" % e, day)
      self.setDirectoryIn(day)

  def setDirectoryOver(self):
    """ Come back to old path """
    try:
      self.ftp.cwd('..')
    except (ftplib.error_reply,socket.error), e:
      logging.error("Error %s when try to come back" % e)
      self.setDirectoryOver()

  def str2date(self,strin):
      """Return a date object from a string"""
      todaySplit = strin.split('-')
      return date(int(todaySplit[0]), int(todaySplit[1]),int(todaySplit[2]))

  def getToday(self):
    """Return the first day for start to download"""
    if self.today == None:
      # set today variable to today
      self.today = date.today()
    else:
      # set today variable to data pass from user
      self.today = self.str2date(self.today)
      # set enday variable to data
    if self.enday != None:
      self.enday = self.str2date(self.enday)
      
  def getListDays(self):
      """ Return a list of all days selected """
      self.getToday()
      
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
    """ Create a list of files to download, is possible choose if download 
    also jpeg files or only hdf"""
    finalList = []
    # return the file's list inside the directory of each day
    try:
      self.listfiles = self.ftp.nlst() 
      # finallist is ugual to all file with jpeg file
      if self.jpeg and not self.tiles:
        finalList = self.listfiles
      # finallist is ugual to files of tiles passed at initialization of modis 
      # class, jpeg and hdf file are considered
      elif self.jpeg and self.tiles != None:
        for i in self.listfiles:
          File = i.split('.')
          # distinguish jpeg files from hdf files by the number of index 
          # where find the tile index
          if self.tiles.count(File[3]) == 1: #is a jpeg of tiles number
            finalList.append(i)
          elif self.tiles.count(File[2]) == 1: #is a hdf of tiles number
            finalList.append(i)  
      # finallist is only hdf are considered
      elif self.jpeg == False:
        for i in self.listfiles:
          File = i.split('.')
          if not self.tiles or self.tiles.count(File[2]) == 1:
          #if self.tiles == None or \
          #    (self.tiles != None and self.tiles.count(File[2])) == 1:
            finalList.append(i)
      if self.debug==True:
        logging.debug("The number of file to download is: %i" % len(finalList))
      return finalList
    except (ftplib.error_reply,socket.error), e:
      logging.error("Error %s when try to receive list of files" % e)
      self.getFilesList()

  def checkDataExist(self,listNewFile, move = 0):
    """ Check if a data already exist in the directory of download 
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

  def getNewerVersion(self,oldFile,newFile):
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
          # check data exist in the return directory, if it doesn't exist
          oldFile = glob.glob1(self.writeFilePath, filePrefix + "*" \
          + fileSplit[-1])
          numFiles = len(oldFile)
          if numFiles == 0:
            file_hdf = open(os.path.join(self.writeFilePath,i), "wb")
          elif numFiles == 1:
            # check the version of file  
            fileDown = self.getNewerVersion(oldFile[0],i)
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
      self.setDirectoryIn(day)
      #obtain list of all files
      listAllFiles = self.getFilesList()
      #obtain list of files to download
      listFilesDown = self.checkDataExist(listAllFiles)
      #download files for a day
      self.dayDownload(listFilesDown)
      self.setDirectoryOver()
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
    fil = open('listfile.txt', 'w')
    for day in days:
      self.setDirectoryIn(day)
      listAllFiles = self.getFilesList()
      string = day + ": " + str(len(listAllFiles)) + "\n"
      logger.debug(string)
      self.setDirectoryOver()   

class parseModis:
  def __init__(self, filename):

    from xml.etree import ElementTree

    self.hdfname = filename
    self.xmlname = self.hdfname + '.xml'
    with open(self.xmlname) as f:
      self.tree = ElementTree.parse(f)
      
      
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
    
  def getRoot(self):
    """Return the root element"""
    self.rootree = self.tree.getroot()
    
  def getGranule(self):
    """Return the GranuleURMetaData element"""
    self.getRoot()
    self.granule = self.rootree.find('GranuleURMetaData')
    
  def getDataGranule(self):
    """Return the ECSDataGranule element"""
    self.getGranule()
    self.DataGranule = self.granule.find('ECSDataGranule')
    
  def getDayNight(self):
    """Return the DayNightFlag element"""
    self.getDataGranule()
    return self.DataGranule.find('DayNightFlag').text
    
  def getRangeTime(self):
    """Return the RangeDateTime elements inside a dictionary with the element
       name like dictionary key
    """
    self.getGranule()
    rangeTime = {}
    for i in self.granule.find('RangeDateTime').getiterator():
      if i.text.strip() != '':
        rangeTime[i.tag] = i.text      
    return rangeTime

  def getPGEVersion(self):
    """Return the PGEVersion element"""
    self.getGranule()
    return self.granule.find('PGEVersionClass').find('PGEVersion').text

  def getBoundary(self):
    """Return the maximum extend of the MODIS file inside a dictionary"""
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
      self.boundary.append({'lat': la, 'lon':lo})
    extent = {'min_lat':min(lat),'max_lat':max(lat),'min_lon':min(lon),
                'max_lon':max(lon)}
    return extent
    
  def getPSA(self):
    """Return the PSA values inside a dictionary, the PSAName is he key and
       and PSAValue is the value
    """
    psaValue = {}
    self.getGranule()
    psas = self.granule.find('PSAs')
    for i in psas.findall('PSA'):
      psaValue[i.find('PSAName').text] = i.find('PSAValue').text
    return psaValue
    
  def getMeasure(self):
    """Return statistics inside a dictionary"""
    mesValue = {}
    self.getGranule()
    mes = self.granule.find('MeasuredParameter')
    meStat = mes.find('MeasuredParameterContainer').find('QAStats')
    for i in meStat.getiterator():
      mesValue[i.tag] = i.text
