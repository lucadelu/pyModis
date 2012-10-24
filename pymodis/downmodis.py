#!/usr/bin/env python
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

from datetime import *
import os
import glob
import logging
import socket
from ftplib import FTP
import ftplib


class downModis:
  """A class to download MODIS data from NASA FTP repository"""
  def __init__(self,
                password,
                destinationFolder,
                user="anonymous",
                url="e4ftl01.cr.usgs.gov",
                tiles=None,
                path="MOLT/MOD11A1.005",
                today=None,
                enddate=None,
                delta=10,
                jpg=False,
                debug=False
              ):
    """Initialization function :

        password = is your password, usually your email address

        destinationFolder = where the files will be stored

        user = your username, by default anonymous

        url = the url where to download the MODIS data

        path = the directory where the data that you want to download are
               stored on the ftp server

        tiles = a list of tiles that you want to download, None == all tiles

        today = the day to start downloading; in order to pass a date different
                from today use the format YYYY-MM-DD

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
    if os.access(destinationFolder, os.W_OK):
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
    + self.product + '.txt'), 'w')
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
    LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, \
    format=LOGGING_FORMAT)
    self.nconnection = 0

  def removeEmptyFiles(self):
    """Check if some file has size ugual 0"""
    year = str(date.today().year)
    pref = self.product.split('.')[0]
    files = glob.glob1(self.writeFilePath, '%s.A%s*' % (pref, year))
    for f in files:
        fil = os.path.join(self.writeFilePath, f)
        if os.path.getsize(fil) == 0:
            os.remove(fil)

  def connectFTP(self, ncon=20):
    """ Set connection to ftp server, move to path where data are stored
    and create a list of directories for all days

    ncon = number maximum of test to connection at the ftp server
    """
    self.nconnection += 1
    try:
      # connect to ftp server
      self.ftp = FTP(self.url)
      self.ftp.login(self.user, self.password)
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
    except (EOFError, ftplib.error_perm), e:
      logging.error('Error in connection: %s' % e)
      if self.nconnection <= ncon:
        self.connectFTP()

  def closeFTP(self):
    """ Close ftp connection """
    self.ftp.quit()
    self.filelist.close()
    if self.debug == True:
      logging.debug("Close connection %s" % self.url)

  def setDirectoryIn(self, day):
    """ Enter in the directory of the day """
    try:
      self.ftp.cwd(day)
    except (ftplib.error_reply, socket.error), e:
      logging.error("Error %s entering in directory %s" % e, day)
      self.setDirectoryIn(day)

  def setDirectoryOver(self):
    """ Come back to old path """
    try:
      self.ftp.cwd('..')
    except (ftplib.error_reply, socket.error), e:
      logging.error("Error %s when try to come back" % e)
      self.setDirectoryOver()

  def _str2date(self, strin):
      """Return a date object from a string

      string = text string to return date (2012-10-04)
      """
      todaySplit = strin.split('-')
      return date(int(todaySplit[0]), int(todaySplit[1]), int(todaySplit[2]))

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
      """Return a list of all selected days"""
      self._getToday()

      today_s = self.today.strftime("%Y.%m.%d")
      # dirData is reverse sorted
      for i, d in enumerate(self.dirData):
        if d <= today_s:
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
        for i in range(-(len(days)), 0):
          if days[i] < enday_s:
            break
          else:
            delta = delta + 1
        # remove days outside new delta
        days = days[:delta]
      return days

  def getAllDays(self):
    """Return a list of all days"""
    return self.dirData

  def getFilesList(self):
    """ Create a list of files to download, it is possible choose to download
    also the jpeg files or only the hdf files"""
    def cicle_file(jpeg=False, tile=True):
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
      if self.debug == True:
        logging.debug("The number of file to download is: %i" % len(finalList))
      return finalList
    except (ftplib.error_reply, socket.error), e:
      logging.error("Error %s when try to receive list of files" % e)
      self.getFilesList()

  def checkDataExist(self,listNewFile, move = 0):
    """ Check if a file already exists in the directory of download

    listNewFile = list of all files, returned by getFilesList function

    move = it is useful to know if a function is called from download or move function
    """
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

  def getNewerVersion(self, oldFile, newFile):
    """ Return newer version of a file
    
    oldFile = one of the two similar file
    
    newFile = one of the two similar file
    """
    oldFileSplit = oldFile.split('.')
    newFileSplit = newFile.split('.')
    if oldFileSplit[4] > newFileSplit[4]:
      return oldFile
    else:
      return newFile

  def _downloadFile(self, filDown, filHdf):
    """Download the single file
    
    filDown = name of the file to download
    
    filSave = name of the file to write
    """
    filSave = open(filHdf, "wb")
    try:
      self.ftp.retrbinary("RETR " + filDown, filSave.write)
      self.filelist.write("%s\n" % filDown)
      if self.debug==True:
        logging.debug("File %s downloaded" % filDown)
    #if it have an error it try to download again the file
    except (ftplib.error_reply, socket.error, ftplib.error_temp, EOFError), e:
      logging.error("Cannot download %s, retry.." % filDown)
      filSave.close()
      os.remove(filSave.name)
      try:
          self.ftp.pwd()
      except (ftplib.error_temp, EOFError), e:
          self.connectFTP()
      self._downloadFile(filDown, filHdf)
    filSave.close()
    orig_size = self.ftp.size(filDown)
    transf_size = os.path.getsize(filSave.name)
    if orig_size == transf_size:
      return 0
    else:
      logging.warning("Different size for file %s - original data: %s, downloaded: %s" %
                      (filDown, orig_size, transf_size))
      os.remove(filSave.name)
      self._downloadFile(filDown,filHdf)

  def dayDownload(self, listFilesDown):
    """ Downloads tiles are in files_hdf_consider

    listFilesDown = list of the files to download, returned by checkDataExist function
    """
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
            file_hdf = os.path.join(self.writeFilePath, i)
          elif numFiles == 1:
            # check the version of file  
            fileDown = self.getNewerVersion(oldFile[0], i)
            if fileDown != oldFile[0]:
              os.remove(os.path.join(self.writeFilePath, oldFile[0]))
              file_hdf = os.path.join(self.writeFilePath, fileDown)
          elif numFiles > 1:
            logging.error("There are to much files for %s" % i)
            #raise EOFError("There are to much file with the same prefix")
          if numFiles == 0 or (numFiles == 1 and fileDown != oldFile[0]):
            self._downloadFile(i, file_hdf)

  def downloadsAllDay(self, clean=False, allDays=False):
    """ Downloads all the tiles considered """
    #return the days to download
    if clean:
        self.removeEmptyFiles()
    if allDays:
        days = self.getAllDays()
    else:
        days = self.getListDays()
    if self.debug == True:
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
    if self.debug == True:
      logging.debug("Download terminated")
    return 0

  def debugLog(self):
    """Function to create the debug file"""
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
      self.setDirectoryIn(day)
      listAllFiles = self.getFilesList()
      string = day + ": " + str(len(listAllFiles)) + "\n"
      logger.debug(string)
      self.setDirectoryOver()