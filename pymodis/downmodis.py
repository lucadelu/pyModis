#!/usr/bin/env python
#  class to download modis data
#
#  (c) Copyright Luca Delucchi 2010-2016
#  (c) Copyright Logan C Byers 2014
#  Authors: Luca Delucchi
#           Logan C Byers
#  Email: luca dot delucchi at fmach dot it
#         loganbyers@ku.edu
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
It supports both FTP and HTTP repositories

Classes:

* :class:`modisHtmlParser`
* :class:`downModis`

Functions:

* :func:`urljoin`
* :func:`getNewerVersion`
* :func:`str2date`

"""

# python 2 and 3 compatibility
from __future__ import print_function
from builtins import dict

from datetime import date
from datetime import timedelta
import os
import sys
import glob
import logging
import socket
from ftplib import FTP
import ftplib
import requests
# urllib in python 2 and 3
try:
    from future.standard_library import install_aliases
    install_aliases()
except ImportError:
    raise ImportError("Future library not found, please install it")
# urlparse in python 2 and 3
try:
    from urlparse import urlparse
    URLPARSE = True
except ImportError:
    try:
        from urllib.parse import urlparse
        URLPARSE = True
    except ImportError:
        URLPARSE = False
        print('WARNING: urlparse not found, it is not possible to use'
              ' netrc file')
from urllib.request import urlopen
import urllib.request
import urllib.error
from base64 import b64encode
from html.parser import HTMLParser
import re
import netrc
global GDAL

try:
    import osgeo.gdal as gdal
    GDAL = True
except ImportError:
    try:
        import gdal
        GDAL = True
    except ImportError:
        GDAL = False
        print('WARNING: Python GDAL library not found, please install it to'
              ' check data downloaded with pyModis')
# setup gdal
if GDAL:
    gdal.UseExceptions()
    gdalDriver = gdal.GetDriverByName('HDF4')
    if not gdalDriver:
        GDAL = False
        print("GDAL installation has no support for HDF4, please update GDAL")


def urljoin(*args):
    """Joins given arguments into a url. Trailing but not leading slashes are
    stripped for each argument.
    http://stackoverflow.com/a/11326230

    :return: a string
    """

    return "/".join([str(x).rstrip('/') for x in args])


def getNewerVersion(oldFile, newFile):
    """Check two files to determine which is newer

       :param str oldFile: one of the two similar files
       :param str newFile: one of the two similar files

       :return: the name of newer file
    """
    # get the processing date (YYYYDDDHHMMSS) from the file strings
    if oldFile.split('.')[4] > newFile.split('.')[4]:
        return oldFile
    else:
        return newFile


def str2date(datestring):
    """Convert to datetime.date object from a string

       :param str datestring string with format (YYYY-MM-DD)
       :return: a datetime.date object representing datestring
    """
    if '-' in datestring:
        stringSplit = datestring.split('-')
    elif '.' in datestring:
        stringSplit = datestring.split('.')
    elif ' ' in datestring:
        stringSplit = datestring.split(' ')
    return date(int(stringSplit[0]), int(stringSplit[1]), int(stringSplit[2]))


class ModisHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)


class modisHtmlParser(HTMLParser):
    """A class to parse HTML

       :param fh: content of http request
    """
    def __init__(self, fh):
        """Function to initialize the object"""
        HTMLParser.__init__(self)
        self.fileids = []
        self.feed(str(fh))

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
        """Return a list of files to download

           :param str prod: the code of MODIS product that we are going to
                            analyze
           :param list tiles: the list of tiles to consider
           :param bool jpeg: True to also check for jpeg data
        """
        finalList = []
        for i in self.fileids:
            # distinguish jpg from hdf by where the tileID is within the string
            # jpgs have the tileID at index 3, hdf have tileID at index 2
            name = i.split('.')
            # if product is not in the filename, move to next filename in list
            if not name.count(prod):
                continue
            # if tiles are not specified and the file is not a jpg, add to list
            if not tiles and not (name.count('jpg') or name.count('BROWSE')):
                finalList.append(i)
            # if tiles are specified
            if tiles:
                # if a tileID is at index 3 and jpgs are to be downloaded
                if tiles.count(name[3]) == 1 and jpeg:
                    finalList.append(i)
                # if a tileID is at in index 2, it is known to be HDF
                elif tiles.count(name[2]) == 1:
                    finalList.append(i)
        return finalList


class downModis:
    """A class to download MODIS data from NASA FTP or HTTP repositories

       :param str destinationFolder: where the files will be stored
       :param str password: the password required by NASA authentication system
       :param str user: the user namerequired by NASA authentication system
       :param str url: the base url from where to download the MODIS data,
                       it can be FTP or HTTP but it has to start with
                       'ftp://' or 'http://' or 'https://'
       :param str path: the directory where the data that you want to
                        download are stored on the FTP server. For HTTP
                        requests, this is the part of the url between the 'url'
                        parameter and the 'product' parameter.
       :param str product: the code of the product to download, the code
                           should be idential to the one of the url
       :param str tiles: a set of tiles to be downloaded, None == all tiles.
                         This can be passed as a string of tileIDs separated
                         by commas, or as a list of individual tileIDs
       :param str today: the day to start downloading; in order to pass a
                         date different from today use the format YYYY-MM-DD
       :param str enddate: the day to end downloading; in order to pass a
                           date use the format YYYY-MM-DD. This day must be
                           before the 'today' parameter. Downloading happens
                           in reverse order (currently)

       :param int delta: timelag i.e. the number of days starting from
                         today backwards. Will be overwritten if
                         'enddate' is specifed during instantiation
       :param bool jpeg: set to True if you want to download the JPG overview
                         file in addition to the HDF
       :param bool debug: set to True if you want to obtain debug information
       :param int timeout: Timeout value for HTTP server (seconds)
       :param bool checkgdal: variable to set the GDAL check
    """

    def __init__(self, destinationFolder, password=None, user=None,
                 url="https://e4ftl01.cr.usgs.gov", tiles=None, path="MOLT",
                 product="MOD11A1.005", today=None, enddate=None, delta=10,
                 jpg=False, debug=False, timeout=30, checkgdal=True):
        """Function to initialize the object"""

        # prepare the base url and set the url type (ftp/http)
        if 'ftp://' in url:
            self.url = url.replace('ftp://', '').rstrip('/')
            self.urltype = 'ftp'
        elif 'http://' in url:
            self.url = url
            self.urltype = 'http'
        elif 'https://' in url:
            self.url = url
            self.urltype = 'http'
        else:
            raise IOError("The url should contain 'ftp://' or 'http://'")
        if not user and not password and not URLPARSE:
            raise IOError("Please use 'user' and 'password' parameters")
        elif not user and not password and URLPARSE:
            self.domain = urlparse(self.url).hostname
            try:
                nt = netrc.netrc()
            except:
                raise IOError("Please set 'user' and 'password' parameters"
                              ", netrc file does not exist")
            try:
                account = nt.hosts[self.domain]
            except:
                try:
                    account = nt.hosts['urs.earthdata.nasa.gov']
                except:
                    raise IOError("Please set 'user' and 'password' parameters"
                                  ", netrc file does not contain parameter "
                                  "for NASA url")
            # user for download
            self.user = account[0]
            # password for download
            self.password = account[2]
        else:
            # user for download
            self.user = user
            # password for download
            self.password = password
        self.userpwd = "{us}:{pw}".format(us=self.user,
                                          pw=self.password)
        userAndPass = b64encode(str.encode(self.userpwd)).decode("ascii")
        self.http_header = { 'Authorization' : 'Basic %s' %  userAndPass }
        cookieprocessor = urllib.request.HTTPCookieProcessor()
        opener = urllib.request.build_opener(ModisHTTPRedirectHandler, cookieprocessor)
        urllib.request.install_opener(opener)
        # the product (product_code.004 or product_cod.005)
        self.product = product
        self.product_code = product.split('.')[0]
        # url directory where data are located
        self.path = urljoin(path, self.product)
        # tiles to downloads
        if type(tiles) == str:
            self.tiles = tiles.split(',')
        else:  # tiles are list, tuple, or None
            self.tiles = tiles
        # set destination folder
        if not os.path.isdir(destinationFolder):
            os.makedirs(destinationFolder)
            self.writeFilePath = destinationFolder
        elif os.access(destinationFolder, os.W_OK):
            self.writeFilePath = destinationFolder
        else:
            try:
                os.mkdir(destinationFolder)
                self.writeFilePath = destinationFolder
            except:
                raise Exception("Folder to store downloaded files does not exist"
                                " or is not writeable")
        # return the name of product
        if len(self.path.split('/')) == 2:
            self.product = self.path.split('/')[1]
        elif len(self.path.split('/')) == 3:
            self.product = self.path.split('/')[2]
        # write a file with the name of file to be downloaded
        self.filelist = open(os.path.join(self.writeFilePath,
                                          'listfile{pro}.txt'.format(pro=self.product)),
                                          'w')
        # set if to download jpgs
        self.jpeg = jpg
        # today, or the last day in the download series chronologically
        self.today = today
        # chronologically the first day in the download series
        self.enday = enddate
        # default number of days to consider if enddate not specified
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
        logging.captureWarnings(True)
        # global connection attempt counter
        self.nconnection = 0
        # timeout for HTTP connection before failing (seconds)
        self.timeout = timeout
        # files within the directory where data will be saved
        self.fileInPath = []
        for f in os.listdir(self.writeFilePath):
            if os.path.isfile(os.path.join(self.writeFilePath, f)):
                self.fileInPath.append(f)
        global GDAL
        if not GDAL and checkgdal:
            logging.warning("WARNING: Python GDAL library not found")
        elif GDAL and not checkgdal:
            GDAL = False
        self.dirData = []

    def removeEmptyFiles(self):
        """Function to remove files in the download directory that have
           filesize equal to 0
        """
        year = str(date.today().year)
        prefix = self.product.split('.')[0]
        files = glob.glob1(self.writeFilePath, '%s.A%s*' % (prefix, year))
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
        if len(self.dirData) == 0:
            raise Exception("There are some troubles with the server. "
                            "The directory seems to be empty")

    def _connectHTTP(self, ncon=20):
        """Connect to HTTP server, create a list of directories for all days

           :param int ncon: maximum number of attempts to connect to the HTTP
                            server before failing. If ncon < 0, connection
                            attempts are unlimited in number
        """
        self.nconnection += 1
        try:
            url = urljoin(self.url, self.path)
            try:
                http = requests.get(url, timeout=self.timeout)
                self.dirData = modisHtmlParser(http.content).get_dates()
            except:
                http = urlopen(url, timeout=self.timeout)
                self.dirData = modisHtmlParser(http.read()).get_dates()
            self.dirData.reverse()
        except:
            logging.error('Error in connection')
            if self.nconnection <= ncon or ncon < 0:
                self._connectHTTP()

    def _connectFTP(self, ncon=20):
        """Set connection to ftp server, move to path where data are stored,
           and create a list of directories for all days

           :param int ncon: maximum number of attempts to connect to the FTP
                            server before failing.

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
            # ensure dirData contains only directories, remove all references to files
            self.dirData = [elem.split()[-1] for elem in self.dirData if elem.startswith("d")]
            if self.debug:
                logging.debug("Open connection {url}".format(url=self.url))
        except (EOFError, ftplib.error_perm) as e:
            logging.error('Error in connection: {err}'.format(err=e))
            if self.nconnection <= ncon:
                self._connectFTP()

    def closeFTP(self):
        """Close ftp connection and close the file list document"""
        self.ftp.quit()
        self.closeFilelist()
        if self.debug:
            logging.debug("Close connection {url}".format(url=self.url))

    def closeFilelist(self):
        """Function to close the file list of where the files are downloaded"""
        self.filelist.close()

    def setDirectoryIn(self, day):
        """Enter into the file directory of a specified day

           :param str day: a string representing a day in format YYYY.MM.DD
        """
        try:
            self.ftp.cwd(day)
        except (ftplib.error_reply, socket.error) as e:
            logging.error("Error {err} entering in directory "
                          "{name}".format(err=e, name=day))
            self.setDirectoryIn(day)

    def setDirectoryOver(self):
        """Move up within the file directory"""
        try:
            self.ftp.cwd('..')
        except (ftplib.error_reply, socket.error) as e:
            logging.error("Error {err} when trying to come back".format(err=e))
            self.setDirectoryOver()

    def _getToday(self):
        """Set the dates for the start and end of downloading"""
        if self.today is None:
            # set today variable from datetime.date method
            self.today = date.today()
        elif type(self.today) == str:
            # set today variable from string data passed by user
            self.today = str2date(self.today)
        # set enday variable to data passed by user
        if type(self.enday) == str:
            self.enday = str2date(self.enday)
        # set delta
        if self.today and self.enday:
            if self.today < self.enday:
                self.today, self.enday = self.enday, self.today
            delta = self.today - self.enday
            self.delta = abs(delta.days) + 1

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
            # make a full cycle from the last index and find
            # it make a for cicle from the last value and find the internal
            # delta to remove file outside temporaly range
            for i in range(0, len(days)):
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
        """Returns a list of files to download. HDF and XML files are
           downloaded by default. JPG files will be downloaded if
           self.jpeg == True.

           :param str day: the date of data in format YYYY.MM.DD

           :return: a list of files to download for the day
        """
        if self.urltype == 'http':
            return self._getFilesListHTTP(day)
        elif self.urltype == 'ftp':
            return self._getFilesListFTP()

    def _getFilesListHTTP(self, day):
        """Returns a list of files to download from http server, which will
           be HDF and XML files, and optionally JPG files if specified by
           self.jpeg

           :param str day: the date of data in format YYYY.MM.DD
        """
        # return the files list inside the directory of each day
        try:
            url = urljoin(self.url, self.path, day)
            if self.debug:
                logging.debug("The url is: {url}".format(url=url))
            try:
                http = modisHtmlParser(requests.get(url,
                                       timeout=self.timeout).content)
            except:
                http = modisHtmlParser(urlopen(url,
                                       timeout=self.timeout).read())
            # download JPG files also
            if self.jpeg:
                # if tiles not specified, download all files
                if not self.tiles:
                    finalList = http.get_all()
                # if tiles specified, download all files with jpegs
                else:
                    finalList = http.get_tiles(self.product_code,
                                               self.tiles, jpeg=True)
            # if JPG files should not be downloaded, get only HDF and XML
            else:
                finalList = http.get_tiles(self.product_code, self.tiles)
            if self.debug:
                logging.debug("The number of file to download is: "
                              "{num}".format(num=len(finalList)))

            return finalList
        except (socket.error) as e:
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
        except (ftplib.error_reply, socket.error) as e:
            logging.error("Error {err} when trying to receive list of "
                          "files".format(err=e))
            self._getFilesListFTP()

    def checkDataExist(self, listNewFile, move=False):
        """Check if a file already exists in the local download directory

           :param list listNewFile: list of all files, returned by getFilesList
                                    function
           :param bool move: it is useful to know if a function is called from
                             download or move function
           :return: list of files to download
        """
        # different return if this method is used from downloadsAllDay() or
        # moveFile()
        if not listNewFile and not self.fileInPath:
            logging.error("checkDataExist both lists are empty")
        elif not listNewFile:
            listNewFile = list()
        elif not self.fileInPath:
            self.fileInPath = list()
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
        except (RuntimeError) as e:
            logging.error(e)
            return 1

    def downloadFile(self, filDown, filHdf, day):
        """Download a single file

           :param str filDown: name of the file to download
           :param str filHdf: name of the file to write to
           :param str day: the day in format YYYY.MM.DD
        """
        if self.urltype == 'http':
            self._downloadFileHTTP(filDown, filHdf, day)
        elif self.urltype == 'ftp':
            self._downloadFileFTP(filDown, filHdf)

    def _downloadFileHTTP(self, filDown, filHdf, day):
        """Download a single file from the http server

           :param str filDown: name of the file to download
           :param str filHdf: name of the file to write to
           :param str day: the day in format YYYY.MM.DD
        """
        filSave = open(filHdf, "wb")
        url = urljoin(self.url, self.path, day, filDown)
        orig_size = None
        try:  # download and write the file
            req = urllib.request.Request(url, headers = self.http_header)
            http = urllib.request.urlopen(req)
            orig_size = http.headers['Content-Length']
            filSave.write(http.read())
        # if local file has an error, try to download the file again
        except:
            logging.warning("Tried to downlaod with urllib but got this "
                            "error {ex}".format(ex=sys.exc_info()))
            try:
                http = requests.get(url, timeout=self.timeout)
                orig_size = http.headers['Content-Length']
                filSave.write(http.content)
            except:
                logging.warning("Tried to downlaod with requests but got this "
                                "error {ex}".format(ex=sys.exc_info()))
                logging.error("Cannot download {name}. "
                              "Retrying...".format(name=filDown))
                filSave.close()
                os.remove(filSave.name)
                import time
                time.sleep(5)
                self._downloadFileHTTP(filDown, filHdf, day)
        filSave.close()
        transf_size = os.path.getsize(filSave.name)
        if not orig_size:
            self.filelist.write("{name}\n".format(name=filDown))
            self.filelist.flush()
            if self.debug:
                logging.debug("File {name} downloaded but not "
                              "check the size".format(name=filDown))
            return 0
        if int(orig_size) == int(transf_size):
            # if no xml file, delete the HDF and redownload
            if filHdf.find('.xml') == -1:
                test = False
                if GDAL:
                    test = self.checkFile(filHdf)
                if test:
                    os.remove(filSave.name)
                    self._downloadFileHTTP(filDown, filHdf, day)
                else:
                    self.filelist.write("{name}\n".format(name=filDown))
                    self.filelist.flush()
                    if self.debug:
                        logging.debug("File {name} downloaded "
                                      "correctly".format(name=filDown))
                    return 0
            else:  # xml exists
                self.filelist.write("{name}\n".format(name=filDown))
                self.filelist.flush()
                if self.debug:
                    logging.debug("File {name} downloaded "
                                  "correctly".format(name=filDown))
                return 0
        # if filesizes are different, delete and try again
        else:
            logging.warning("Different size for file {name} - original data: "
                            "{orig}, downloaded: {down}".format(name=filDown,
                                                                orig=orig_size,
                                                                down=transf_size))
            os.remove(filSave.name)
            self._downloadFileHTTP(filDown, filHdf, day)

    def _downloadFileFTP(self, filDown, filHdf):
        """Download a single file from ftp server

           :param str filDown: name of the file to download
           :param str filHdf: name of the file to write to
        """
        filSave = open(filHdf, "wb")
        try:  # transfer file from ftp
            self.ftp.retrbinary("RETR " + filDown, filSave.write)
            self.filelist.write("{name}\n".format(name=filDown))
            self.filelist.flush()
            if self.debug:
                logging.debug("File {name} downloaded".format(name=filDown))
        # if error during download process, try to redownload the file
        except (ftplib.error_reply, socket.error, ftplib.error_temp,
                EOFError) as e:
            logging.error("Cannot download {name}, the error was '{err}'. "
                          "Retrying...".format(name=filDown, err=e))
            filSave.close()
            os.remove(filSave.name)
            try:
                self.ftp.pwd()
            except (ftplib.error_temp, EOFError) as e:
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

            # check if this file already exists in the save directory
            oldFile = glob.glob1(self.writeFilePath, filePrefix + "*"
                                 + fileSplit[-1])
            numFiles = len(oldFile)
            # if it doesn't exist
            if numFiles == 0:
                file_hdf = os.path.join(self.writeFilePath, i)
            # if one does exist
            elif numFiles == 1:
                # check the version of file, delete local file if it is older
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
           :param bool allDays: download all passable days
        """
        if clean:
            self.removeEmptyFiles()
        # get the days to download
        if allDays:
            days = self.getAllDays()
        else:
            days = self.getListDays()
        # log the days to download
        if self.debug:
            logging.debug("The number of days to download is: "
                          "{num}".format(num=len(days)))
        # download the data
        if self.urltype == 'http':
            self._downloadAllDaysHTTP(days)
        elif self.urltype == 'ftp':
            self._downloadAllDaysFTP(days)

    def _downloadAllDaysHTTP(self, days):
        """Downloads all the tiles considered from HTTP server

           :param list days: the list of days to download
        """
        # for each day
        for day in days:
            # obtain list of all files
            listAllFiles = self.getFilesList(day)
            # filter files based on local files in save directory
            listFilesDown = self.checkDataExist(listAllFiles)
            # download files for a day
            self.dayDownload(day, listFilesDown)
        self.closeFilelist()
        if self.debug:
            logging.debug("Download terminated")
        return 0

    def _downloadAllDaysFTP(self, days):
        """Downloads all the tiles considered from FTP server

           :param list days: the list of days to download
        """
        # for each day
        for day in days:
            # enter in the directory of day
            self.setDirectoryIn(day)
            # obtain list of all files
            listAllFiles = self.getFilesList()
            # filter files based on local files in save directory
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
        # add formatter to console handler
        ch.setFormatter(formatter)
        # add console handler to logger
        logger.addHandler(ch)
        return logger

    def debugDays(self):
        """This function is useful to debug the number of days"""
        logger = self.debugLog()
        days = self.getListDays()
        # if length of list of days and the delta of days are different
        if len(days) != self.delta:
            # for each day
            for i in range(1, self.delta + 1):
                # calculate the current day using datetime.timedelta
                delta = timedelta(days=i)
                day = self.today - delta
                day = day.strftime("%Y.%m.%d")
                # check if day is in the days list
                if day not in days:
                    logger.critical("This day {day} is not present on "
                                    "list".format(day=day))
        # the length of list of days and delta are equal
        else:
            logger.info("debugDays() : getListDays() and self.delta are same "
                        "length")

    def debugMaps(self):
        """ Prints the files to download to the debug stream"""
        logger = self.debugLog()
        days = self.getListDays()
        for day in days:
            listAllFiles = self.getFilesList(day)
            string = day + ": " + str(len(listAllFiles)) + "\n"
            logger.debug(string)
