#!/usr/bin/env python
# script to extract specific information from MODIS Quality Masks
#
#  (c) Copyright Ingmar Nitze 2013
#  Authors: Ingmar Nitze, Luca Delucchi
#  Email: initze at ucc dot ie
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

import sys
import os
try:
    from pymodis import optparse_gui
    WXPYTHON = True
except:
    WXPYTHON = False
from pymodis import optparse_required
from pymodis import qualitymodis


def main():
    """Main function"""
    # usage
    usage = "usage: %prog [options] input_file"
    if 1 == len(sys.argv) and WXPYTHON:
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser

    parser = option_parser_class(usage=usage, description='modis_quality')

    parser.add_option("-o", "--output", dest="output", required=True,
                      help="the prefix of output file", metavar="OUTPUT_FILE")
    # type
    parser.add_option("-t", "--type", dest="type", default="1",
                      help="quality type either as number or name (e.g. 1 or "
                           "VIQuality for MOD13 products) [default=%default]")
    # quality layer
    parser.add_option("-l", "--qualitylayer", dest="layer", default="1",
                      help="quality layer of the dataset, dependent on the "
                           "used MODIS product. (e.g. 1 or QC_Day for the "
                           "Daytime QC Layer of MOD11) [default=%default]")

    # quality layer
    parser.add_option("-p", "--producttype", dest="product", default="MOD13Q1",
                      help="quality layer of the dataset, dependent on the "
                           "used MODIS product. (e.g. 1 or QC_Day for the "
                           "Daytime QC Layer of MOD11) [default=%default]")
    # return options and argument
    (options, args) = parser.parse_args()
    if len(args) == 0 and not WXPYTHON:
        parser.print_help()
        sys.exit(1)
    if len(args) > 1:
        parser.error("You have to define the name of HDF file.")
    if not os.path.isfile(args[0]):
        parser.error("You have to define the name of HDF file.")
    # set modis object
    modisQuality = qualitymodis.QualityModis(args[0], options.output,
                                             qType=options.type,
                                             qLayer=options.layer,
                                             pType=options.product)
    # run
    modisQuality.run()

if __name__ == "__main__":
    main()
