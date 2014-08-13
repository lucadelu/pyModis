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
"""Module to download MODIS HDF files from NASA repository.
It support both FTP and HTTP repositories

Classes:

* :class:`modisHtmlParser`
* :class:`downModis`

Functions:

* :func:`urljoin`
* :func:`getNewerVersion`
* :func:`str2date`

"""
from __future__ import print_function

from datetime import date
from datetime import timedelta
import os
import glob
import logging
import socket
from ftplib import FTP
import ftplib
try:
    import requests
except ImportError:
    import urllib2
from HTMLParser import HTMLParser
import re

try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'


def urljoin(*args):
    """Joins given arguments into a url. Trailing but not leading slashes are
    stripped for each argument.
    http://stackoverflow.com/a/11326230

    :return: a string
    """

    return "/".join(map(lambda x: str(x).rstrip('/'), args))


def getNewerVersion(oldFile, newFile):
    """Check what is newer version of a file

       :param str oldFile: one of the two similar file
       :param str newFile: one of the two similar file

       :return: the name of newer file
    """
    oldFileSplit = oldFile.split('.')
    newFileSplit = newFile.split('.')
    if oldFileSplit[4] > newFileSplit[4]:
        return oldFile
    else:
        return newFile


def str2date(strin):
    """Convert to date object from a string

       :param str string: text string to return date (2012-10-04)

       :return: a Date object
    """
    todaySplit = strin.split('-')
    return date(int(todaySplit[0]), int(todaySplit[1]), int(todaySplit[2]))


class modisHtmlParser(HTMLParser):
    """A class to parse HTML

       :param fh: content of http request
    """
    def __init__(self, fh):
        """Function to initialize the object"""
        HTMLParser.__init__(self)
        self.fileids = []
        self.feed(fh)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrD = dict(attrs)
            self.fileids.append(attrD['href'].replace('/', ''))

    def get_all(self):
        """Return everything"""
        return self.fileids

    def get_dates(self):
        """Return a list of directories with date"""
        regex = re.compile('(\d{4})[/.-](\d{2})[/.-](\d{2})$')
        return [elem for elem in self.fileids if regex.match(elem)]

    def get_tiles(self, prod, tiles, jpeg=False):
        """Return a list of file to download

           :param str prod: the code of MODIS product that we are going to
                            analyze
           :param list tiles: the list of tiles to consider
           :param bool jpeg: check also for jpeg data
        """
        finalList = []
        for i in self.fileids:
            name = i.split('.')
            # distinguish jpeg files from hdf files by the number of index
            # where find the tile index
            if not name.count(prod):
                continue
            if not tiles and not (name.count('jpg') or name.count('BROWSE')):
                finalList.append(i)
            # is a jpeg of tiles number
            if tiles:
                if tiles.count(name[3]) == 1 and jpeg:
                    finalList.append(i)
                # is a hdf of tiles number
                elif tiles.count(name[2]) == 1:
                    finalList.append(i)
        return finalList


class downModis:
    """A class to download MODIS data from NASA FTP repository

       :param str destinationFolder: where the files will be stored
       :param str password: the password, it should be your email address
                            to connect to a FTP server. Do not use this
                            variable if the server is a HTTP server
       :param str user: the user name, by default 'anonymous', used to
                        connect to a FTP server. Do not use this variable
                        if the server is a HTTP server
       :param str url: the url from where to download the MODIS data, it
                       can be FTP or HTTP and it has to start with
                       http:// or ftp://
       :param str path: the directory where the data that you want to
                        download are stored on the FTP server
       :param str product: the code of product to download, the code
                           should be idential to the one of the url
       :param str tiles: a list of tiles to be downloaded, None == all
                         tiles
       :param str today: the day to start downloading; in order to pass a
                         date different from today use the format
                         YYYY-MM-DD
       :param str enddate: the day to end downloading; in order to pass a
                           date use the format YYYY-MM-DD
       :param int delta: timelag i.e. the number of days starting from
                         today backwards
       :param bool jpeg: set to True if you want to download also the JPG
                         overview file
       :param bool debug: set to True if you want to obtain debug
                          information
       :param int timeout: Timeout value for HTTP server
    """
    def __init__(self, destinationFolder, password=None, user="anonymous",
                 url="http://e4ftl01.cr.usgs.gov", tiles=None, path="MOLT",
                 product="MOD11A1.005", today=None, enddate=None, delta=10,
                 jpg=False, debug=False, timeout=30):
        """Function to initialize the object"""

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
            raise IOError("Folder to store downloaded files does not exist"
                          " or is not writeable")
        # return the name of product
        if len(self.path.split('/')) == 2:
            self.product = self.path.split('/')[1]
        elif len(self.path.split('/')) == 3:
            self.product = self.path.split('/')[2]
        # write a file with the name of file downloaded
        self.filelist = open(os.path.join(self.writeFilePath,
                                          'listfile{pro}.txt'.format(pro=self.product)), 'w')
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
        log_filename = os.path.join(self.writeFilePath,
                                    'modis{pro}.log'.format(pro=self.product))
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename=log_filename, level=logging.DEBUG,
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
            raise IOError("GDAL installation has no support for HDF4, please"
                          " update GDAL")

    def removeEmptyFiles(self):
        """Check if some file has size equal to 0"""
        year = str(date.today().year)
        pref = self.product.split('.')[0]
        files = glob.glob1(self.writeFilePath, '%s.A%s*' % (pref, year))
        for f in files:
            fil = os.path.join(self.writeFilePath, f)
            if os.path.getsize(fil) == 0:
                os.remove(fil)

    def connect(self, ncon=20):
        """Connect to the server and fill the dirData variable

           :param int ncon: maximum number of attempts to connect to the HTTP
                            server before failing
        """
        if self.urltype == 'ftp':
            self._connectFTP(ncon)
        elif self.urltype == 'http':
            self._connectHTTP(ncon)

    def _connectHTTP(self, ncon=20):
        """Connect to HTTP server, create a list of directories for all days

           :param int ncon: maximum number of attempts to connect to the HTTP
                            server before failing
        """
        self.nconnection += 1
        try:
            try:
                http = requests.get(urljoin(self.url, self.path),
                                    timeout=self.timeout)
                self.dirData = modisHtmlParser(http.content).get_dates()
            except:
                http = urllib2.urlopen(urljoin(self.url, self.path),
                                       timeout=self.timeout)
                self.dirData = modisHtmlParser(http.read()).get_dates()
            self.dirData.reverse()
        except:
            logging.error('Error in connection')
            if self.nconnection <= ncon:
                self._connectHTTP()

    def _connectFTP(self, ncon=20):
        """Set connection to ftp server, move to path where data are stored
           and create a list of directories for all days

           :param int ncon: maximum number of attempts to connect to the HTTP
                            server before failing

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
            if self.debug:
                logging.debug("Open connection {url}".format(name=self.url))
        except (EOFError, ftplib.error_perm), e:
            logging.error('Error in connection: {err}'.format(err=e))
            if self.nconnection <= ncon:
                self._connectFTP()

    def closeFTP(self):
        """Close ftp connection"""
        self.ftp.quit()
        self.closeFilelist()
        if self.debug:
            logging.debug("Close connection {url}".format(self.url))

    def closeFilelist(self):
        """Function to close the file where write the downloaded files"""
        self.filelist.close()

    def setDirectoryIn(self, day):
        """Enter in the directory of the day

           :param str day: a string rappresenting a day in format YYYY.MM.DD
        """
        try:
            self.ftp.cwd(day)
        except (ftplib.error_reply, socket.error), e:
            logging.error("Error {err} entering in directory "
                          "{name}".format(err=e, name=day))
            self.setDirectoryIn(day)

    def setDirectoryOver(self):
        """Come back to old path"""
        try:
            self.ftp.cwd('..')
        except (ftplib.error_reply, socket.error), e:
            logging.error("Error {err} when try to come back".format(err=e))
            self.setDirectoryOver()

    def _getToday(self):
        """Return the first day for start to download"""
        if self.today is None:
            # set today variable to today
            self.today = date.today()
        else:
            # set today variable to data pass from user
            self.today = str2date(self.today)
            # set enday variable to data
        if self.enday is not None:
            self.enday = str2date(self.enday)
        if self.today and self.enday:
            if self.today < self.enday:
                raise IOError("The first day should be newer then end date")
            delta = self.today - self.enday
            self.delta = delta.days

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
        if self.enday is not None:
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
        """Creates a list of files to download, it is possible to choose to
           download also the JPG overview files or only the HDF files

           :param str day: the date of data

           :return: a list of file to download
        """
        if self.urltype == 'http':
            return self._getFilesListHTTP(day)
        elif self.urltype == 'ftp':
            return self._getFilesListFTP()

    def _getFilesListHTTP(self, day):
        """Creates a list of files to download from http server, it is
           possible to choose to download also the JPG overview files or
           only the HDF files

           :param str day: the date of data
        """
    # return the file's list inside the directory of each day
        try:
            url = urljoin(self.url, self.path, day)
            if self.debug:
                logging.debug("The url is: {url}".format(url=url))
            try:
                http = modisHtmlParser(requests.get(url,
                                       timeout=self.timeout).content)
            except:
                http = modisHtmlParser(urllib2.urlopen(url,
                                       timeout=self.timeout).read())
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
            if self.debug:
                logging.debug("The number of file to download is: "
                              "{num}".format(num=len(finalList)))
            return finalList
        except (socket.error), e:
            logging.error("Error {err} when try to receive list of "
                          "files".format(err=e))
            self._getFilesListHTTP(day)

    def _getFilesListFTP(self):
        """Create a list of files to download from FTP server, it is possible
           choose to download also the JPG overview files or only the HDF files
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
                # is a jpeg of tiles number
                if self.tiles:
                    if self.tiles.count(name[3]) == 1 and jpeg:
                        finalList.append(i)
                # is a hdf of tiles number
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
            if self.debug:
                logging.debug("The number of file to download is: "
                              "{num}".format(num=len(finalList)))
            return finalList
        except (ftplib.error_reply, socket.error), e:
            logging.error("Error {err} when trying to receive list of "
                          "files".format(err=e))
            self._getFilesListFTP()

    def checkDataExist(self, listNewFile, move=False):
        """Check if a file already exists in the directory of download

           :param list listNewFile: list of all files, returned by getFilesList
                                    function
           :param bool move: it is useful to know if a function is called from
                             download or move function
           :return: list of files to download
        """
        # different return if this method is used from downloadsAllDay() or
        # moveFile()
        if not move:
            listOfDifferent = list(set(listNewFile) - set(self.fileInPath))
        elif move:
            listOfDifferent = list(set(self.fileInPath) - set(listNewFile))
        return listOfDifferent

    def checkFile(self, filHdf):
        """Check by using GDAL to be sure that the download went ok

           :param str filHdf: name of the HDF file to check

           :return: 0 if file is correct, 1 for error
        """
        try:
            gdal.Open(filHdf)
            return 0
        except (RuntimeError), e:
            logging.error(e)
            return 1

    def downloadFile(self, filDown, filHdf, day):
        """Download the single file

           :param str filDown: name of the file to download
           :param str filHdf: name of the file to write to
           :param str day: the day in format YYYY.MM.DD
        """
        if self.urltype == 'http':
            self._downloadFileHTTP(filDown, filHdf, day)
        elif self.urltype == 'ftp':
            self._downloadFileFTP(filDown, filHdf)

    def _downloadFileHTTP(self, filDown, filHdf, day):
        """Download the single file from http server

           :param str filDown: name of the file to download
           :param str filHdf: name of the file to write to
           :param str day: the day in format YYYY.MM.DD
        """
        filSave = open(filHdf, "wb")
        try:
            try:
                http = requests.get(urljoin(self.url, self.path, day, filDown))
                orig_size = http.headers['content-length']
                filSave.write(http.content)
            except:
                http = urllib2.urlopen(urljoin(self.url, self.path, day,
                                               filDown))
                orig_size = http.headers['content-length']
                filSave.write(http.read())
            filSave.close()
        # if it have an error it try to download again the file
        except:
            logging.error("Cannot download {name}. "
                          "Retrying..".format(name=filDown))
            filSave.close()
            os.remove(filSave.name)
            self._downloadFileHTTP(filDown, filHdf, day)
        transf_size = os.path.getsize(filSave.name)
        if int(orig_size) == int(transf_size):
            if filHdf.find('.xml') == -1:
                if self.checkFile(filHdf):
                    os.remove(filSave.name)
                    self._downloadFileHTTP(filDown, filHdf, day)
                else:
                    self.filelist.write("{name}\n".format(name=filDown))
                    if self.debug:
                        logging.debug("File {name} downloaded "
                                      "correctly".format(name=filDown))
                    return 0
            else:
                self.filelist.write("{name}\n".format(name=filDown))
                if self.debug:
                    logging.debug("File {name} downloaded "
                                  "correctly".format(name=filDown))
                return 0
        else:
            logging.warning("Different size for file {name} - original data: "
                            "{orig}, downloaded: {down}".format(name=filDown,
                                                                orig=orig_size,
                                                                down=transf_size))
            os.remove(filSave.name)
            self._downloadFileHTTP(filDown, filHdf, day)

    def _downloadFileFTP(self, filDown, filHdf):
        """Download the single file from ftp server

           :param str filDown: name of the file to download
           :param str filHdf: name of the file to write to
        """
        filSave = open(filHdf, "wb")
        try:
            self.ftp.retrbinary("RETR " + filDown, filSave.write)
            self.filelist.write("{name}\n".format(name=filDown))
            if self.debug:
                logging.debug("File {name} downloaded".format(name=filDown))
        # if it have an error it try to download again the file
        except (ftplib.error_reply, socket.error, ftplib.error_temp,
                EOFError), e:
            logging.error("Cannot download {name}, the error was '{err}'. "
                          "Retrying...".format(name=filDown, err=e))
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
            logging.warning("Different size for file {name} - original data: "
                            "{orig}, downloaded: {down}".format(name=filDown,
                                                                orig=orig_size,
                                                                down=transf_size))
            os.remove(filSave.name)
            self._downloadFileFTP(filDown, filHdf)

    def dayDownload(self, day, listFilesDown):
        """Downloads tiles for the selected day

           :param str day: the day in format YYYY.MM.DD
           :param list listFilesDown: list of the files to download, returned
                                      by checkDataExist function
        """
        # for each file in files' list
        for i in listFilesDown:
            fileSplit = i.split('.')
            filePrefix = "{a}.{b}.{c}.{d}".format(a=fileSplit[0],
                                                  b=fileSplit[1],
                                                  c=fileSplit[2],
                                                  d=fileSplit[3])

            # check data exists in the return directory
            oldFile = glob.glob1(self.writeFilePath, filePrefix + "*"
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
                logging.error("There are to many files for "
                              "{name}".format(name=i))
            if numFiles == 0 or (numFiles == 1 and fileDown != oldFile[0]):
                self.downloadFile(i, file_hdf, day)

    def downloadsAllDay(self, clean=False, allDays=False):
        """Download all requested days

           :param bool clean: if True remove the empty files, they could have
                              some problems in the previous download
           :param bool allDays: download all passible days
        """
        # return the days to download
        if clean:
            self.removeEmptyFiles()
        if allDays:
            days = self.getAllDays()
        else:
            days = self.getListDays()
        if self.debug:
            logging.debug("The number of days to download is: "
                          "{num}".format(num=len(days)))
        if self.urltype == 'http':
            self._downloadsAllDayHTTP(days)
        elif self.urltype == 'ftp':
            self._downloadsAllDayFTP(days)

    def _downloadsAllDayHTTP(self, days):
        """Downloads all the tiles considered from HTTP server

           :param list days: the list of days to download
        """
        # for each day
        for day in days:
            # obtain list of all files
            listAllFiles = self.getFilesList(day)
            # obtain list of files to download
            listFilesDown = self.checkDataExist(listAllFiles)
            # download files for a day
            self.dayDownload(day, listFilesDown)
        self.closeFilelist()
        if self.debug:
            logging.debug("Download terminated")
        return 0

    def _downloadsAllDayFTP(self, days):
        """Downloads all the tiles considered from FTP server

           :param list days: the list of days to download
        """
        # for each day
        for day in days:
            # enter in the directory of day
            self.setDirectoryIn(day)
            # obtain list of all files
            listAllFiles = self.getFilesList()
            # obtain list of files to download
            listFilesDown = self.checkDataExist(listAllFiles)
            # download files for a day
            self.dayDownload(day, listFilesDown)
            self.setDirectoryOver()
        self.closeFTP()
        if self.debug:
            logging.debug("Download terminated")
        return 0

    def debugLog(self):
        """Function to create the debug file

        :return: a Logger object to use to write debug info
        """
        # create logger
        logger = logging.getLogger("PythonLibModis debug")
        logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - "
                                      "%(levelname)s - %(message)s")
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
                    logger.critical("This day {day} is not present on "
                                    "list".format(day=day))
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
