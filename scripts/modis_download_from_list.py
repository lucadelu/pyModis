#!/usr/bin/env python
# Script to download massive MODIS data from a text file containing a list of
# MODIS file name
#
#  (c) Copyright Luca Delucchi 2013
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at fmach dot it
#
##################################################################
#
#  This MODIS Python script is licensed under the terms of GNU GPL 2.
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
"""Script to download massive MODIS data from a text file containing a list of
MODIS file name"""
from datetime import date
try:
    from pymodis import optparse_gui
    WXPYTHON = True
except:
    WXPYTHON = False
from pymodis import downmodis
from pymodis import optparse_required
import sys
import os
import getpass


def write_out(out, ts, options, day):
    """Write the missing files"""
    opts = options.prod.split('.')
    for ti in ts:
        out.write("{co}\n".format(co=".".join((opts[0], "A{da}".format(da=day),
                                               ti, opts[1], '*', 'hdf*'))))


def main():
    """Main function"""
    # usage
    usage = "usage: %prog [options] destination_folder"
    if 1 == len(sys.argv) and WXPYTHON:
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage,
                                 description='modis_download_from_list')
    # file
    parser.add_option("-f", "--file", dest="file", type='file',
                      help="Input file containing data to download")
    # url
    parser.add_option("-u", "--url", default="https://e4ftl01.cr.usgs.gov",
                      help="http/ftp server url [default=%default]",
                      dest="url")
    # username and password from stdin
    parser.add_option("-I", "--input", dest="input", action="store_true",
                      help="insert user and password from standard input")
    # password
    parser.add_option("-P", "--password", dest="password",
                      help="password to connect to the server")
    # username
    parser.add_option("-U", "--username", dest="user",
                      help="username to connect to the server ")
    # path to add the path in the server
    parser.add_option("-s", "--source", dest="path", default="MOLT",
                      help="directory on the http/ftp server "
                      "[default=%default]")
    # path to add the url
    parser.add_option("-p", "--product", dest="prod", default="MOD11A1.006",
                      help="product name as on the http/ftp server "
                      "[default=%default]")
    # path to file with server missing tiles
    parser.add_option("-o", "--outputs", dest="outs", default=None,
                      help="the output where write the missing files in the"
                      " server [default=%default]. Use 'stdout' to write to "
                      " STDOUT")
    # use netrc file
    parser.add_option("-n", action="store_true", dest="netrc", default=False,
                      help="use netrc file to read user and password")
    # debug
    parser.add_option("-x", action="store_true", dest="debug", default=False,
                      help="this is useful for debugging the "
                      "download [default=%default]")
    # jpg
    parser.add_option("-j", action="store_true", dest="jpg", default=False,
                      help="download also the jpeg overview files "
                      "[default=%default]")
    # return options and argument
    (options, args) = parser.parse_args()
    if len(args) == 0 and not WXPYTHON:
        parser.print_help()
        sys.exit(1)
    if len(args) > 1:
        parser.error("You have to define the destination folder for HDF file")
    if not os.path.isdir(args[0]):
        parser.error("The destination folder is not a dir or not exists")

    if options.netrc:
        user = None
        password = None
    elif options.input:
        if sys.version_info.major == 3:
            user = input("Username: ")
        else:
            user = raw_input("Username: ")
        password = getpass.getpass()
    else:
        user = options.user
        password = options.password

    f = open(options.file)

    lines = [elem for elem in f.readlines()]

    vals = {}
    for elem in lines:
        if elem != '\n':
            dat = elem.split('.')[1].replace('A', '')
            fisplit = elem.strip().split('.')
            if dat not in vals.keys():
                vals[dat] = [fisplit[2]]
            else:
                vals[dat].append(fisplit[2])

    if not options.outs:
        write = None
    elif options.outs == "stdout":
        write = sys.stdout
    else:
        write = open(options.outs, 'w')

    for d, tiles in sorted(vals.items(), reverse=True):
        year = int(d[0:4])
        doy = int(d[4:7])
        fdate = date.fromordinal(date(year, 1, 1).toordinal() + doy - 1).isoformat()
        modisOgg = downmodis.downModis(url=options.url, user=user,
                                       password=password,
                                       destinationFolder=args[0],
                                       tiles=','.join(sorted(set(tiles))),
                                       path=options.path, product=options.prod,
                                       delta=1, today=fdate,
                                       debug=options.debug, jpg=options.jpg)

        modisOgg.connect()
        day = modisOgg.getListDays()[0]
        if modisOgg.urltype == 'http':
            listAllFiles = modisOgg.getFilesList(day)
        else:
            listAllFiles = modisOgg.getFilesList()
        if not listAllFiles:
            if write:
                write_out(write, tiles, options, d)
            continue
        listFilesDown = modisOgg.checkDataExist(listAllFiles)

        if listFilesDown:
            if options.debug:
                print(listFilesDown)
            modisOgg.dayDownload(day, listFilesDown)
            for fi in listFilesDown:
                if 'xml' not in fi:
                    try:
                        tiles.remove(fi.split('.')[2])
                    except ValueError:
                        pass
            if write:
                write_out(write, tiles, options, d)
        if modisOgg.urltype == 'http':
            modisOgg.closeFilelist()
        else:
            modisOgg.closeFTP()

if __name__ == "__main__":
    main()
