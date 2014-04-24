#!/usr/bin/env python
# script to create mosaic from several tiles of MODIS
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

#import system library
import os
import sys
import string
from types import ListType
#import modis library
from pymodis import convertmodis, optparse_gui, optparse_required, gdal_merge

ERROR = "You have to define the name of a text file containing HDF files." \
        " (One HDF file for line)"


def main():
    """Main function"""
    #usage
    usage = "usage: %prog [options] hdflist_file"
    if 1 == len(sys.argv):
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage, description='modis_mosaic')
    groupR = OptionGroup(parser, 'Required options')
    groupG = OptionGroup(parser, 'Options for GDAL')
    groupM = OptionGroup(parser, 'Options for MRT')    
    #spatial extent
    groupR.add_option("-o", "--output", dest="output", required=True,
                      help="the name of output mosaic", metavar="OUTPUT_FILE")
    #write into file
    groupR.add_option("-s", "--subset", dest="subset",
                      help="a subset of product layers. The string should" \
                      " be similar to: 1 0 [default: all layers]")
    #options only for GDAL
    groupG.add_option("-f", "--output-format", dest="output_format",
                      metavar="OUTPUT_FORMAT", default="GTiff",
                      help="output format supported by GDAL [default=%default]")
    groupG.add_option("-e", "--epsg", dest="epsg", metavar="EPSG",
                      help="EPSG code for the output")
    groupG.add_option("-w", "--wkt_file", dest="wkt", metavar="WKT",
                      help="file or string containing projection definition" \
                      " in WKT format")
    groupG.add_option("-g", "--grain", dest="resolution",
                      type="int", help="the spatial resolution of output file")
    groupG.add_option("--formats", dest="formats", action="store_true",
                      help="print supported GDAL formats")
    #mrt path
    groupM.add_option("-m", "--mrt", dest="mrt_path", required=True,
                      help="the path to MRT software", metavar="MRT_PATH",
                      type='directory')
    (options, args) = parser.parse_args()
    parser.add_option_group(groupR)
    parser.add_option_group(groupG)
    parser.add_option_group(groupM)

    #check the number of tiles
    if not args:
        print ERROR
        sys.exit()
    else:
        if type(args) != ListType:
            print ERROR
            sys.exit()
        elif len(args) > 1:
            print ERROR
            sys.exit()

    if not os.path.isfile(args[0]):
        parser.error("You have to define the name of a text file containing HDF " \
                     "files. (One HDF file for line)")

    #check is a subset it is set
    if not options.subset:
        options.subset = False
    else:
        if string.find(options.subset, '(') != -1 or string.find(options.subset, ')') != -1:
            parser.error('ERROR: The spectral string should be similar to: "1 0"')
    if options.mrt_path:
        modisOgg = convertmodis.createMosaic(args[0], options.output,
                                             options.mrt_path,  options.subset)
    else:
        modisOgg = gdal_merge.
    modisOgg.run()

#add options
if __name__ == "__main__":
    gdal.AllRegister()
    argv = gdal.GeneralCmdLineProcessor(sys.argv)
    if argv != None:
        main()
