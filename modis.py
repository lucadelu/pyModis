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
#  0.3.0 Fix the choosing of days (2011-05-22)
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

class modisClass:
  """A class to download modis data from nasa ftp repository"""
  def __init__(self, 
                user,
                password,
                destinationFolder,
                url = "e4ftl01u.ecs.nasa.gov",
                tiles = None,
                path = "MOLT/MOD11A1.005",
                today = None,
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
      raise IOError("Folder to write downloaded files doesn't exist or is not"
    + "writeable")
    # set jpg download
    self.jpeg = jpg
    # today
    self.today = today
    # delta of days
    self.delta = delta
    # status of tile download
    self.status = True
    # for debug, you can download only xml files
    self.debug = debug
    # for logging
    LOG_FILENAME = os.path.join(self.writeFilePath, 'modis' \
    + self.path.split('/')[1] + '.log')
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

  def getToday(self):
    """Return the first day for start to download"""
    if self.today == None:
      # set today variable to today
      self.today = date.today()
      # variable to determinate where start the cicle 
      self.numDay = 0
    else:
      # set today variable to data pass from user
      todaySplit = self.today.split('-')
      self.today = date(int(todaySplit[0]), int(todaySplit[1]),
      int(todaySplit[2]))
      #self.getNumberToday()
      
      
  def getListDays(self):
      days = set()
      self.getToday()
      self.today   #data di partenza
      self.delta   # giorni indietro
      self.dirData # giorni disponibili
      
      today_s = self.today.strftime("%Y.%m.%d")
      # dirData is reverse sorted
      for i, d in enumerate(self.dirData):
          if d <= today_s:
              today_avail = d
              today_index = i
              break
      else:
          print "no data available for requested days"
          import sys
          sys.exit()
      days = self.dirData[today_index:][:self.delta]
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
          numFiles = len(glob.glob1(self.writeFilePath, filePrefix + "*" \
          + fileSplit[-1]))
          if numFiles == 0:
            file_hdf = open(self.writeFilePath + i, "wb")
          elif numFiles == 1:
            files = glob.glob(self.writeFilePath + "*" + filePrefix + "*" \
            + fileSplit[-1])
            # check the version of file
            fileDown = self.getNewerVersion(files[0],i).split('/')
            if fileDown[-1] != files[0].split('/')[-1]:
              os.remove(files[0])
              file_hdf = open(self.writeFilePath + fileDown[-1], "wb")
          elif len(glob.glob1(self.writeFilePath, "*" + filePrefix + "*" \
          + fileSplit[-1])) > 1:
            logging.error("There are to much files for %s" % i)
            #raise EOFError("There are to much file with the same prefix")
          if numFiles == 0 or \
              (numFiles == 1 and fileDown[-1] != files[0].split('/')[-1]):
            self.downloadFile(i,file_hdf)

  def downloadsAllDay(self):
    """ Downloads all the tiles considered """
    #return the days to download
    days = self.getListDays()
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
    
  #def moveFile(self,newDirectory):
    #""" Move files from a directory to another. First read the data from old 
    #directory, after control different version and remove old version, at the 
    #finish it move files into the new directory"""
    #fileInPath = []
    ## check if directory is writable
    #if os.access(newDirectory,os.W_OK):
      #newDirectory = newDirectory
    #else:
      #raise IOError("Folder to move downloaded files doesn't exist or is not"
    #+ "writeable")
    ## add all files found in the directory where we want move the new files
    #for f in os.listdir(newDirectory):
      #if os.path.isfile(os.path.join(newDirectory, f)):
        #fileInPath.append(f)
    ## check wich data already exist
    #listFilesMove = self.checkDataExist(fileInPath,move = 1)
    ## for all files
    #for i in listFilesMove:
      #fileSplit = i.split('.')
      #filePrefix = fileSplit[0] + '.' + fileSplit[1] + '.' + fileSplit[2] \
      #+ '.' + fileSplit[3]
      #if len(glob.glob1(newDirectory, filePrefix + "*" \
      #+ fileSplit[-1])) == 0:
        #file_hdf = self.writeFilePath + i
        #os.system ("mv"+ " " + file_hdf + " " + newDirectory)
      #elif len(glob.glob1(newDirectory, filePrefix + "*" \
      #+ fileSplit[-1])) == 1:
        #files = glob.glob(newDirectory + "*" + filePrefix + "*" \
        #+ fileSplit[-1])
        #fileDown = self.getNewerVersion(files[0],i).split('/')
        #if fileDown[-1] != files[0].split('/')[-1]:        
          #print ""
