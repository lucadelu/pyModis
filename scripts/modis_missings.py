#!/usr/bin/env python
# script to check if some data are missing
#
#  (c) Copyright Luca Delucchi 2016
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at fmach dot it
#
##################################################################

import calendar
import glob
import sys
import os
from pymodis import optparse_required
from datetime import date

try:
    from pymodis import optparse_gui
    WXPYTHON = True
except:
    WXPYTHON = False


def search_day(d, year):
    """Function to search data inside folder

    :param d: the julian day
    :param year: the year to search
    """
    day = "%03d" % (d,)
    searchday = "*.A{ye}{da}.*.hdf".format(ye=year, da=day)
    return glob.glob(searchday)


def main():
    """Main function"""
    # usage
    usage = "usage: %prog [options] destination_folder"
    if 1 == len(sys.argv) and WXPYTHON:
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage, description='modis_missings')

    # tiles
    parser.add_option("-t", "--tiles", dest="tiles", default=None,
                      help="string of tiles separated with comma "
                      "[default=%default for all tiles]")
    # year
    parser.add_option("-y", "--year", dest="year", default=date.today().year,
                      help="year to check")
    # increment days
    parser.add_option("-i", "--increment", dest="incr", help="Number of days"
                      "[default=%default]",
                      default=1)
    # increment days
    parser.add_option("-o", "--output", dest="output", help="Output file "
                      "[default=STDOUT]")

    # return options and argument
    (options, args) = parser.parse_args()
    # test if args[0] it is set
    if len(args) == 0 and not WXPYTHON:
        parser.print_help()
        sys.exit(1)
    if len(args) == 0:
        parser.error("You have to define the destination folder for HDF file")

    year = int(options.year)
    today = date.today()
    if year < today.year:
        if calendar.isleap(year):
            days = 367
        else:
            days = 366
    elif year == today.year:
        days = int(today.strftime('%j'))
    else:
        parser.error("The year is in advance")

    tiles = options.tiles
    orpath = os.path.abspath(os.curdir)
    os.chdir(args[0])
    files = []
    startday = 0
    outString = ""
    while len(files) == 0:
        startday += 1
        files = search_day(startday, year)

    for d in range(startday, days, options.incr):
        files = search_day(d, year)
        if len(tiles) != len(files):
            outString += "{day}, {leng}\n".format(day=d, leng=len(files))
    os.chdir(orpath)
    if options.output:
        outFile = open(options.output, 'w')
        outFile.write(outString)
        outFile.close()
        print("{name} write correctly".format(name=outFile.name))
    # else print the string
    else:
        print(outString)

# add options
if __name__ == "__main__":
    main()
