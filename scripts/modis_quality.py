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
from pymodis import optparse_required, qualitymodis, optparse_gui

def main():
    """Main function"""
    #usage
    usage = "usage: %prog [options] input_file destination_file"

    option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage, description='modis_quality')
    #type
    parser.add_option("-t", "--type", dest="type", default="1",
                      help="Quality type either as number or name (e.g. 1 or VIQuality for MOD13 products) [default=%default]")
	# quality layer				  
	parser.add_option("-ql", "--qualitylayer", dest="ql", default="1",
                      help="Quality layer of the dataset, dependent on the used MODIS product. (e.g. 1 or QC_Day for the Daytime QC Layer of MOD11)[default=%default]")
    #return options and argument
    (options, args) = parser.parse_args()
    #test if args[0] it is set
    if len(args) != 2:
        parser.error("You have to pass the destination folder for HDF file")
    #set modis object
    modisQuality = qualitymodis.QualityModis(args[0], args[1], qType = options.type)
    #run 
    modisQuality.run()

#add options
if __name__ == "__main__":
    main()