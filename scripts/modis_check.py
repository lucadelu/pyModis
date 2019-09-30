#!/usr/bin/env python
# script to check which tiles are missing
#
#  (c) Copyright Luca Delucchi 2018
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
"""script to check which tiles are missing"""

import glob
import os
import sys
import calendar
import copy
from datetime import datetime

from collections import OrderedDict

try:
    from pymodis import optparse_gui
    WXPYTHON = True
except:
    WXPYTHON = False
from pymodis import optparse_required

def main():
    """Main function"""
    # usage
    usage = "usage: %prog [options] destination_folder"
    if 1 == len(sys.argv) and WXPYTHON:
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage, description='modis_check')
    # output
    parser.add_option("-o", "--outputs", dest="outs", default="stdout",
                      help="the output where write "
                      "[default=%default]")
    # tiles
    parser.add_option("-t", "--tiles", dest="tiles", default=None,
                      help="string of tiles separated with comma "
                      "[default=%default for all tiles]")
    # the product
    parser.add_option("-p", "--product", dest="prod", default="MOD11A1",
                      help="product name as on the http/ftp server "
                      "[default=%default]")
    # the MODIS version
    parser.add_option("-m", "--modis_version", dest="mver", default="006",
                      help="the version of MODIS product "
                      "[default=%default]")

    # first day
    parser.add_option("-f", "--firstday", dest="today", default=None,
                      help="the day to start download [default=%default is for"
                      " today]; if you want change data you must use "
                      "this format YYYY-MM-DD", metavar="FIRST_DAY")
    # last day
    parser.add_option("-e", "--endday", dest="enday", default=None,
                      metavar="LAST_DAY", help="the day to stop download "
                      "[default=%default]; if you want change"
                      " data you must use this format YYYY-MM-DD")

    # number of days
    parser.add_option("-d", "--days", dest="days", default=1, metavar="DAYS",
                      help="The temporal resolution of the dataset, "
                      "[default=%default]")

    # return options and argument
    (options, args) = parser.parse_args()
    # test if args[0] it is set
    if len(args) == 0 and not WXPYTHON:
        parser.print_help()
        sys.exit(1)
    if len(args) == 0:
        parser.error("You have to define the destination folder for HDF file")
    if not os.path.isdir(args[0]):
        parser.error("The destination folder is not a dir or not exists")

    sday = 1
    if options.today:
        sday = int(datetime.strptime(options.today, "%Y-%m-%d").strftime("%j"))
    eday = 366
    if options.enday:
        eday = int(datetime.strptime(options.enday, "%Y-%m-%d").strftime("%j"))
    tres = int(options.days)

    if options.outs == "stdout":
        write = sys.stdout
    else:
        write = open(options.outs, 'w')

    files = glob.glob(os.path.join(args[0], '*.hdf'))
    tiles = options.tiles.split(',')
    output = OrderedDict()
    missing_dates = {}
    for fi in files:
        if fi.startswith('./'):
            fi = fi.lstrip('./')
        if fi.count('.') != 5:
            print("Error with file {fi}, to many dots, skipping it. Please " \
                  "to be sure run it for the same folder containing the HDF" \
                  " file".format(fi=fi))
            continue
        fisplit = fi.split('.')
        dat = fisplit[1]
        year = int(dat[1:5])
        if year not in missing_dates.keys():
            if eday == 366 and calendar.isleap(year):
                eday = 367
            missing_dates[year] = list(range(sday, eday, tres))
        doy = int(dat[5:8])
        try:
            missing_dates[year].remove(doy)
        except ValueError:
            pass
        if dat not in output.keys():
            output[dat] = copy.deepcopy(tiles)
        try:
            output[dat].remove(fisplit[2])
        except ValueError:
            continue
    for k, v in missing_dates.items():
        for dat in v:
            for ti in tiles:
                yd = "A{ye}{do}".format(ye=k, do=str(dat).zfill(3))
                write.write("{co}\n".format(co=".".join((options.prod, yd, ti,
                                                         options.mver, '*',
                                                         'hdf*'))))
    for k, v in output.items():
        if len(v) != 0:
            for ti in v:
                write.write("{co}\n".format(co=".".join((options.prod, k,
                                                         ti, options.mver,
                                                         '*', 'hdf*'))))
    if options.outs != "stdout":
        write.close()

if __name__ == "__main__":
    main()
