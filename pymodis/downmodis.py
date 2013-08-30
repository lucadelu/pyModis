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

from datetime import date, timedelta
import os
import glob
import logging
import socket
from ftplib import FTP
import ftplib
import urllib2
from HTMLParser import HTMLParser
import re

try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise('Python GDAL library did not find, please install it')


def urljoin(*args):
    """
    Joins given arguments into a url. Trailing but not leading slashes are
    stripped for each argument.
    http://stackoverflow.com/a/11326230
    """

    return "/".join(map(lambda x: str(x).rstrip('/'), args))


def getNewerVersion(oldFile, newFile):
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


def str2date(strin):
    """Return a date object from a string

       string = text string to return date (2012-10-04)

    """
    todaySplit = strin.split('-')
    return date(int(todaySplit[0]), int(todaySplit[1]), int(todaySplit[2]))


class modisHtmlParser(HTMLParser):
    """A class to parse HTML"""
    def __init__(self, fh):
        """
        {fh} must be an input stream returned by open() or urllib2.urlopen()
        """
        HTMLParser.__init__(self)
        self.fileids = []
        self.feed(fh.read())

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrD = dict(attrs)
            self.fileids.append(attrD['href'].replace('/', ''))

    def get_all(self):
        """ Return everything """
        return self.fileids

    def get_dates(self):
        """ Return a list of directories with date """
        regex = re.compile('(\d{4})[/.-](\d{2})[/.-](\d{2})$')
        return [elem for elem in self.fileids if regex.match(elem)]

    def get_tiles(self, prod, tiles, jpeg=False):
        """ Return a list of file to download """
        finalList = []
        for i in self.fileids:
            name = i.split('.')
            # distinguish jpeg files from hdf files by the number of index
            # where find the tile index
            if not name.count(prod):
                continue
            if not tiles and not (name.count('jpg') or name.count('BROWSE')):
                finalList.append(i)
            #is a jpeg of tiles number
            if tiles:
                if tiles.count(name[3]) == 1 and jpeg:
                    finalList.append(i)
            #is a hdf of tiles number
                elif tiles.count(name[2]) == 1:
                    finalList.append(i)
        return finalList


class downModis:
    """A class to download MODIS data from NASA FTP repository"""
    def __init__(self,
                destinationFolder,
                password=None,
                user="anonymous",
                url="http://e4ftl01.cr.usgs.gov",
                tiles=None,
                path="MOLT",
                product="MOD11A1.005",
                today=None,
                enddate=None,
                delta=10,
                jpg=False,
                debug=False,
                timeout=30
              ):
        """Initialization function :

            destinationFolder = where the files will be stored

            password = the password, should be your email address to use to
                       connect to FTP server.
                       Not use this variable if the server is HTPP

            password = the user, by  default is anonymous, to use to connect
                       to FTP server.
                       Not use this variable if the server is HTPP

            url = the url where download the MODIS data, it can be FTP or
                  HTTP and it have to start with http:// or ftp://

            path = the directory where the data that you want to download are
                   stored on the ftp server

            product = the code of product to download, che code should be
                      ugual to the one of the url

            tiles = a list of tiles to download, None == all tiles

            today = the day to start downloading; in order to pass a date
                    different from today use the format YYYY-MM-DD

            enddate = the day to finish downloading; in order to pass a date
                      use the format YYYY-MM-DD

            delta = timelag i.e. the number of days starting from today
                    backwards

            jpeg = set True if you want to download also the jpg file

            debug = set True if you want to obtain debug information

            timeout = Timeout value for http server
        """

        # url modis
        if 'ftp' in url:
            self.url = url.replace('ftp://', '').rstrip('/')
            self.urltype = 'ftp'
        elif 'http' in url:
            self.url = url
            self.urltype = 'http'
        else:
            raise IOError("The url should contain 'ftp://' or 'http://'")
        # user for download using ftp
        self.user = user
        # password for download using ftp
        self.password = password
        # the product
        self.product = product
        self.product_code = product.split('.')[0]
        # directory where data are collected
        self.path = urljoin(path, self.product)
        # tiles to downloads
        if tiles:
            self.tiles = tiles.split(',')
        else:
            self.tiles = tiles
        # set destination folder
        if os.access(destinationFolder, os.W_OK):
            self.writeFilePath = destinationFolder
        else:
            raise IOError("Folder to store downloaded files does not exist" \
                          + " or is not writeable")
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
        log_filename = os.path.join(self.writeFilePath, 'modis' \
        + self.product + '.log')
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename=log_filename, level=logging.DEBUG, \
        format=log_format)
        self.nconnection = 0
        self.timeout = timeout
        self.fileInPath = []
        # add all files in the directory where we will save new modis data
        for f in os.listdir(self.writeFilePath):
            if os.path.isfile(os.path.join(self.writeFilePath, f)):
                self.fileInPath.append(f)
        gdal.UseExceptions()
        gdalDriver = gdal.GetDriverByName('HDF4')
        if not gdalDriver:
            raise IOError("GDAL has no support for HDF4, please update GDAL")

    def removeEmptyFiles(self):
        """Check if some file has size ugual 0"""
        year = str(date.today().year)
        pref = self.product.split('.')[0]
        files = glob.glob1(self.writeFilePath, '%s.A%s*' % (pref, year))
        for f in files:
            fil = os.path.join(self.writeFilePath, f)
            if os.path.getsize(fil) == 0:
                os.remove(fil)

    def connect(self, ncon=20):
        """Connect to the server and fill the dirData variable

           ncon = number maximum of test to connection at the server
        """
        if self.urltype == 'ftp':
            self._connectFTP(ncon)
        elif self.urltype == 'http':
            self._connectHTTP(ncon)

    def _connectHTTP(self, ncon=20):
        """ Connect to http server, create a list of directories for all days

            ncon = number maximum of test to connection at the ftp server
        """
        self.nconnection += 1
        try:
            http = urllib2.urlopen(urljoin(self.url, self.path),
                                   timeout=self.timeout)
        except:
            logging.error('Error in HTTP connection')
            if self.nconnection <= ncon:
                self._connectHTTP()
        try:
            self.dirData = modisHtmlParser(http).get_dates()
            self.dirData.reverse()
        except (EOFError, urllib2.URLError), e:
            logging.error('Error in connection: %s' % e)
            self.closeHTTP(http)
            if self.nconnection <= ncon:
                self._connectHTTP()

    def _connectFTP(self, ncon=20):
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
            if self.debug == True:
                logging.debug("Open connection %s" % self.url)
        except (EOFError, ftplib.error_perm), e:
            logging.error('Error in connection: %s' % e)
            if self.nconnection <= ncon:
                self._connectFTP()

    def closeFTP(self):
        """ Close ftp connection """
        self.ftp.quit()
        self.closeFilelist()
        if self.debug == True:
            logging.debug("Close connection %s" % self.url)

    def closeHTTP(self, http):
        """ Close http connection

            http = the http concention object created by urlib2.open         
        """
        http.close()
        self.closeFilelist()
        if self.debug == True:
            logging.debug("Close connection %s" % self.url)

    def closeFilelist(self):
        """ Function to close the file where write the downloaded files """
        self.filelist.close()

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

    def _getToday(self):
        """Return the first day for start to download"""
        if self.today == None:
            # set today variable to today
            self.today = date.today()
        else:
            # set today variable to data pass from user
            self.today = str2date(self.today)
            # set enday variable to data
        if self.enday != None:
            self.enday = str2date(self.enday)
        if self.today and self.enday:
            if self.today < self.enday:
                raise IOError("The first day should be newer then end date")
            D = self.today - self.enday
            self.delta = D.days

    def getListDays(self):
        """Return a list of all selected days"""
        self._getToday()

        today_s = self.today.strftime("%Y.%m.%d")
        # dirData is reverse sorted
        for i, d in enumerate(self.dirData):
            if d <= today_s:
                today_index = i
                break
#            else:
#                logging.error("No data available for requested days")
#                import sys
#                sys.exit()
        days = self.dirData[today_index:][:self.delta]
        # this is useful for 8/16 days data, delta could download more images
        # that you want
        if self.enday != None:
            enday_s = self.enday.strftime("%Y.%m.%d")
            delta = 0
            # it make a for cicle from the last value and find the internal
            # delta to remove file outside temporaly range
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

    def getFilesList(self, day=None):
        """ Create a list of files to download, it is possible choose to
            download also the jpeg files or only the hdf files

            day = the date of data

        """
        if self.urltype == 'http':
            return self._getFilesListHTTP(day)
        elif self.urltype == 'ftp':
            return self._getFilesListFTP()

    def _getFilesListHTTP(self, day):
        """ Create a list of files to download from http server, it is possible
            choose to download also the jpeg files or only the hdf files

            day = the date of data

        """
    # return the file's list inside the directory of each day
        try:
            url = urljoin(self.url, self.path, day)
            if self.debug == True:
                logging.debug("The url is: %s" % url)
            conn = urllib2.urlopen(url)
            http = modisHtmlParser(conn)
            # download also jpeg
            if self.jpeg:
                # finallist is ugual to all file with jpeg file
                if not self.tiles:
                    finalList = http.get_all()
                # finallist is ugual to tiles file with jpeg file
                else:
                    finalList = http.get_tiles(self.product_code,
                                               self.tiles, jpeg=True)
            # not download jpeg
            else:
                finalList = http.get_tiles(self.product_code, self.tiles)
            if self.debug == True:
                logging.debug("The number of file to download is: %i" % len(finalList))
            return finalList
        except (socket.error), e:
            self.closeHTTP(conn)
            logging.error("Error %s when try to receive list of files" % e)
            self._getFilesListHTTP(day)

    def _getFilesListFTP(self):
        """ Create a list of files to download from ftp server, it is possible
            choose to download also the jpeg files or only the hdf files
        """
        def cicle_file(jpeg=False):
            """Check the type of file"""
            finalList = []
            for i in self.listfiles:
                name = i.split('.')
                # distinguish jpeg files from hdf files by the number of index
                # where find the tile index
                if not self.tiles and not (name.count('jpg') or
                                           name.count('BROWSE')):
                    finalList.append(i)
                #is a jpeg of tiles number
                if self.tiles:
                    if self.tiles.count(name[3]) == 1 and jpeg:
                        finalList.append(i)
                #is a hdf of tiles number
                    elif self.tiles.count(name[2]) == 1:
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
                finalList = cicle_file()
            if self.debug == True:
                logging.debug("The number of file to download is: %i" % len(finalList))
            return finalList
        except (ftplib.error_reply, socket.error), e:
            logging.error("Error %s when try to receive list of files" % e)
            self._getFilesListFTP()

    def checkDataExist(self, listNewFile, move=0):
        """ Check if a file already exists in the directory of download

            listNewFile = list of all files, returned by getFilesList function

            move = it is useful to know if a function is called from download
                   or move function
        """
        # different return if this method is used from downloadsAllDay() or
        # moveFile()
        if move == 0:
            listOfDifferent = list(set(listNewFile) - set(self.fileInPath))
        elif move == 1:
            listOfDifferent = list(set(self.fileInPath) - set(listNewFile))
        if self.debug == True:
                logging.debug("The number of file to download after check of" \
                              "existing file is: %i" % len(listOfDifferent))
        return listOfDifferent

    def checkFile(self, filHdf):
        """Check using GDAL to be sure that download was fine

        filHdf = name of the HDF file to check
        """
        try:
            gdal.Open(filHdf)
            return 0
        except (RuntimeError), e:
            logging.error(e)
            return 1

    def downloadFile(self, filDown, filHdf, day):
        """Download the single file

        filDown = name of the file to download

        filHdf = name of the file to write

        day = the day in format YYYY.MM.DD
        """
        if self.urltype == 'http':
            self._downloadFileHTTP(filDown, filHdf, day)
        elif self.urltype == 'ftp':
            self._downloadFileFTP(filDown, filHdf)

    def _downloadFileHTTP(self, filDown, filHdf, day):
        """Download the single file from http server

        filDown = name of the file to download

        filSave = name of the file to write

        day = the day in format YYYY.MM.DD
        """
        filSave = open(filHdf, "wb")
        try:
            http = urllib2.urlopen(urljoin(self.url, self.path, day, filDown))
            orig_size = http.headers['content-length']
            filSave.write(http.read())
            filSave.close()
        #if it have an error it try to download again the file
        except (EOFError), e:
            logging.error("Cannot download %s, the error was '%s'. Retry.." % (
                          filDown, e))
            filSave.close()
            os.remove(filSave.name)
            self.closeHTTP(http)
            self._downloadFileHTTP(filDown, filHdf, day)
        transf_size = os.path.getsize(filSave.name)
        if int(orig_size) == int(transf_size):
            if filHdf.find('.xml') == -1:
                if self.checkFile(filHdf):
                    os.remove(filSave.name)
                    self.closeHTTP(http)
                    self._downloadFileHTTP(filDown, filHdf, day)
                else:
                    self.filelist.write("%s\n" % filDown)
                    if self.debug == True:
                        logging.debug("File %s downloaded correctly" % filDown)
                    return 0
            else:
                self.filelist.write("%s\n" % filDown)
                if self.debug == True:
                    logging.debug("File %s downloaded correctly" % filDown)
                return 0
        else:
            logging.warning("Different size for file %s - original data: %s,"\
                            " downloaded: %s" % (filDown, orig_size,
                                                 transf_size))
            os.remove(filSave.name)
            self._downloadFileHTTP(filDown, filHdf, day)

    def _downloadFileFTP(self, filDown, filHdf):
        """Download the single file from ftp server

           filDown = name of the file to download

           filSave = name of the file to write
        """
        filSave = open(filHdf, "wb")
        try:
            self.ftp.retrbinary("RETR " + filDown, filSave.write)
            self.filelist.write("%s\n" % filDown)
            if self.debug == True:
                logging.debug("File %s downloaded" % filDown)
        #if it have an error it try to download again the file
        except (ftplib.error_reply, socket.error, ftplib.error_temp, EOFError), e:
            logging.error("Cannot download %s, the error was '%s'. Retry.." % (
                          filDown, e))
            filSave.close()
            os.remove(filSave.name)
            try:
                self.ftp.pwd()
            except (ftplib.error_temp, EOFError), e:
                self._connectFTP()
            self._downloadFileFTP(filDown, filHdf)
        filSave.close()
        orig_size = self.ftp.size(filDown)
        transf_size = os.path.getsize(filSave.name)
        if orig_size == transf_size:
            return 0
        else:
            logging.warning("Different size for file %s - original data: %s," \
                            " downloaded: %s" % (filDown, orig_size,
                                                 transf_size))
            os.remove(filSave.name)
            self._downloadFileFTP(filDown, filHdf)

    def dayDownload(self, day, listFilesDown):
        """ Downloads tiles are in files_hdf_consider

        listFilesDown = list of the files to download, returned by
                        checkDataExist function
        """
        # for each file in files' list
        for i in listFilesDown:
            fileSplit = i.split('.')
            filePrefix = "%s.%s.%s.%s" % (fileSplit[0], fileSplit[1],
                                          fileSplit[2], fileSplit[3])

            # check data exists in the return directory
            oldFile = glob.glob1(self.writeFilePath, filePrefix + "*" \
            + fileSplit[-1])
            numFiles = len(oldFile)
            if numFiles == 0:
                file_hdf = os.path.join(self.writeFilePath, i)
            elif numFiles == 1:
                # check the version of file
                fileDown = getNewerVersion(oldFile[0], i)
                if fileDown != oldFile[0]:
                    os.remove(os.path.join(self.writeFilePath, oldFile[0]))
                    file_hdf = os.path.join(self.writeFilePath, fileDown)
            elif numFiles > 1:
                logging.error("There are to much files for %s" % i)
            if numFiles == 0 or (numFiles == 1 and fileDown != oldFile[0]):
                if self.debug == True:
                    logging.debug("Start to download file %s" % i)
                self.downloadFile(i, file_hdf, day)

    def downloadsAllDay(self, clean=False, allDays=False):
        """Download the single file

        filDown = name of the file to download

        filSave = name of the file to write
        """
        #return the days to download
        if clean:
            self.removeEmptyFiles()
        if allDays:
            days = self.getAllDays()
        else:
            days = self.getListDays()
        if self.debug == True:
            logging.debug("The number of days to download is: %i" % len(days))
        if self.urltype == 'http':
            self._downloadsAllDayHTTP(days)
        elif self.urltype == 'ftp':
            self._downloadAllDayFTP(days)

    def _downloadsAllDayHTTP(self, days):
        """ Downloads all the tiles considered from HTTP server"""

        #for each day
        for day in days:
            #obtain list of all files
            listAllFiles = self.getFilesList(day)
            #obtain list of files to download
            listFilesDown = self.checkDataExist(listAllFiles)
            #download files for a day
            self.dayDownload(day, listFilesDown)
        self.closeFilelist()
        if self.debug == True:
            logging.debug("Download terminated")
        return 0

    def _downloadsAllDayFTP(self, days):
        """ Downloads all the tiles considered from FTP server"""
        #for each day
        for day in days:
            #enter in the directory of day
            self.setDirectoryIn(day)
            #obtain list of all files
            listAllFiles = self.getFilesList()
            #obtain list of files to download
            listFilesDown = self.checkDataExist(listAllFiles)
            #download files for a day
            self.dayDownload(day, listFilesDown)
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
        logger = self.debugLog()
        days = self.getListDays()
        # if lenght of list of days and the delta of day they are different
        if len(days) != self.delta:
            # for each day
            for i in range(1, self.delta + 1):
                # calculate the current day
                delta = timedelta(days=i)
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
        logger = self.debugLog()
        days = self.getListDays()
        for day in days:
            listAllFiles = self.getFilesList(day)
            string = day + ": " + str(len(listAllFiles)) + "\n"
            logger.debug(string)
