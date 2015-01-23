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
"""Script to mosaic the input tiles. It is able to use MRT or GDAL as backend
"""
from __future__ import print_function

import os
import sys
import string
from types import ListType
try:
    from pymodis import optparse_gui
    WXPYTHON = True
except:
    WXPYTHON = False
from pymodis import convertmodis
from pymodis import convertmodis_gdal
from pymodis import optparse_required
from optparse import OptionGroup
try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise 'Python GDAL library not found, please install python-gdal'

ERROR = "You have to define the name of a text file containing HDF files" \
        " (One HDF file for line)."


def main():
    """Main function"""
    # usage
    usage = "usage: %prog [options] hdflist_file"
    if 1 == len(sys.argv) and WXPYTHON:
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage, description='modis_mosaic')
    groupR = OptionGroup(parser, 'General options')
    groupG = OptionGroup(parser, 'Options for GDAL')
    groupM = OptionGroup(parser, 'Options for MRT')
    # output
    groupR.add_option("-o", "--output", dest="output", required=True,
                      help="the name or prefix (for VRT) of output mosaic",
                      metavar="OUTPUT_FILE")
    # subset
    groupR.add_option("-s", "--subset", dest="subset",
                      help="a subset of product layers. The string should"
                      " be similar to: 1 0 [default: all layers]")
    # options only for GDAL
    groupG.add_option("-f", "--output-format", dest="output_format",
                      metavar="OUTPUT_FORMAT", default="GTiff",
                      help="output format supported: GTiff, HDF4Image"
                      " [default=%default]")
#    groupG.add_option("-g", "--grain", dest="grain",
#                      type="int", help="force the spatial resolution of output"
#                      " file")
    # options for set VRT
    groupG.add_option("-v", "--vrt", dest="vrt", action="store_true",
                      default=False, help="Create a GDAL VRT file. No other "
                      "GDAL options have to been set")
    # mrt path
    groupM.add_option("-m", "--mrt", dest="mrt_path", type='directory',
                      help="the path to MRT software", metavar="MRT_PATH")
    parser.add_option_group(groupR)
    parser.add_option_group(groupG)
    parser.add_option_group(groupM)
    (options, args) = parser.parse_args()
    # check the number of tiles
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
        elif len(args) > 1:
            parser.error(ERROR)
            sys.exit()

    if not os.path.isfile(args[0]):
        parser.error("You have to define the name of a text file containing "
                     "HDF files. (One HDF file for line)")

    # check is a subset it is set
    if not options.subset:
        options.subset = False
    else:
        if string.find(options.subset, '(') != -1 or string.find(options.subset, ')') != -1:
            parser.error('ERROR: The spectral string should be similar to: '
                         '"1 0" without "(" and ")"')
#    if not options.grain and options.vrt:
#        options.grain = False
#    elif not options.grain and options.vrt:
#        parser.error("You have to define the resolution of output file. Please"
#                     " set -g/--grain option")
    if options.mrt_path:
        modisOgg = convertmodis.createMosaic(args[0], options.output,
                                             options.mrt_path, options.subset)
        modisOgg.run()
    else:
        tiles = []
        with open(args[0]) as f:
            for l in f:
                name = os.path.splitext(l.strip())[0]
                if '.hdf' not in name:
                    tiles.append(l.strip())
        modisOgg = convertmodis_gdal.createMosaicGDAL(tiles, options.subset,
                                                      options.output_format)
        if options.vrt:
            modisOgg.write_vrt(options.output)
        else:
            modisOgg.run(options.output)

if __name__ == "__main__":
    gdal.AllRegister()
    argv = gdal.GeneralCmdLineProcessor(sys.argv)
    if argv is not None:
        main()
