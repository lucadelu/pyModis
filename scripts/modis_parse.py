#!/usr/bin/env python
# script to parse variable from xml file
#
#  (c) Copyright Luca Delucchi 2012
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at iasma dot it
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
"""Script to read metadata from a MODIS HDF file"""
from __future__ import print_function
# import system library
import sys
from types import ListType
# import modis library
try:
    from pymodis import optparse_gui
    WXPYTHON = True
except:
    WXPYTHON = False
from pymodis import parsemodis
from pymodis import optparse_required

ERROR = "You have to define the name of HDF file"


def readDict(dic):
    """Function to decode dictionary"""
    out = ""
    for k, v in dic.iteritems():
        out += "%s = %s\n" % (k, v)
    return out


def main():
    """Main function"""
    # usage
    usage = "usage: %prog [options] hdf_file"
    if 1 == len(sys.argv) and WXPYTHON:
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage, description='modis_parse')
    # write into file
    parser.add_option("-w", "--write", dest="output", metavar="OUTPUT_FILE",
                      help="write the chosen information into a file",
                      type='output')
    # all data
    parser.add_option("-a", action="store_true", dest="all", default=False,
                      help="print all possible values of metadata")
    # spatial extent
    parser.add_option("-b", action="store_true", dest="boundary",
                      default=False, help="print the values related to the "
                      "spatial max extent")
    # data files
    parser.add_option("-d", action="store_true", dest="data", default=False,
                      help="print the values related to the date files")
    # data granule
    parser.add_option("-e", action="store_true", dest="data_ecs",
                      default=False, help="print the values related to the "
                      "ECSDataGranule")
    # input files
    parser.add_option("-i", action="store_true", dest="input", default=False,
                      help="print the input layers")
    # other values
    parser.add_option("-o", action="store_true", dest="other", default=False,
                      help="print the other values")
    # platform information
    parser.add_option("-p", action="store_true", dest="platform", default=False,
                      help="print the values related to platform")
    # data quality
    parser.add_option("-q", action="store_true", dest="qa", default=False,
                      help="print the values related to quality")
    # psas
    parser.add_option("-s", action="store_true", dest="psas", default=False,
                      help="print the values related to psas")
    # time
    parser.add_option("-t", action="store_true", dest="time", default=False,
                      help="print the values related to times")

    # return options and argument
    (options, args) = parser.parse_args()
    if len(args) == 0 and not WXPYTHON:
        parser.print_help()
        sys.exit(1)
    if not args:
        parser.error(ERROR)
        sys.exit()
    else:
        if type(args) != ListType:
            parser.error(ERROR)
            sys.exit()
    # create modis object
    modisOgg = parsemodis.parseModis(args[0])
    # the output string
    outString = ""

    if options.all or options.boundary:
        outString += readDict(modisOgg.retBoundary())
    if options.all or options.time:
        outString += "InsertTime = %s\n" % modisOgg.retInsertTime()
        outString += "LastUpdate = %s\n" % modisOgg.retLastUpdate()
        outString += readDict(modisOgg.retRangeTime())
    if options.all or options.data_ecs:
        outString += readDict(modisOgg.retDataGranule())
    if options.all or options.data:
        outString += readDict(modisOgg.retDataFiles())
    if options.all or options.input:
        outString += 'InputFiles = '
        outString += ', '.join(modisOgg.retInputGranule())
        outString += '\n'
    if options.all or options.platform:
        outString += readDict(modisOgg.retPlatform())
    if options.all or options.psas:
        outString += readDict(modisOgg.retPSA())
    if options.all or options.qa:
        out = modisOgg.retMeasure()
        outString += readDict(out['QAStats'])
        outString += readDict(out['QAFlags'])
    if options.all or options.other:
        outString += readDict(modisOgg.retCollectionMetaData())
        outString += "PGEVersion = %s\n" % modisOgg.retPGEVersion()
        outString += "BrowseProduct = %s\n" % modisOgg.retBrowseProduct()
    if not outString:
        print("Please select at least one flag")
    # write option it is set write the string into file
    elif options.output:
        outFile = open(options.output, 'w')
        outFile.write(outString)
        outFile.close()
        print("{name} write correctly".format(name=outFile.name))
    # else print the string
    else:
        print(outString)

if __name__ == "__main__":
    main()
