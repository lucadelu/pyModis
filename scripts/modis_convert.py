#!/usr/bin/env python
# script to convert hdf file in sinusoidal projection to another format and projection
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
import string
#import modis library
from pymodis import convertmodis, parsemodis, optparse_required


def removeBracs(s):
    s = string.replace(s, ']', '')
    s = string.replace(s, '[', '')
    return s


def main():
    """Main function"""
    #usage
    usage = "usage: %prog [options] hdf_file"
    parser = optparse_required.OptionParser(usage=usage)
    #layer subset
    parser.add_option("-s", "--subset", dest="subset", required=True,
                      help="a subset of product's layers. The string should "\
                      "be similar to: ( 1 0 )")
    #mrt path
    parser.add_option("-m", "--mrt", dest="mrt", required=True,
                      help="the path to MRT software", metavar="MRT_PATH")
    parser.add_option("-o", "--output", dest="output",
                      help="the name of output file", metavar="OUTPUT_FILE")
    parser.add_option("-g", "--grain", dest="res", type="int",
                      help="the spatial resolution of output file")
    help_datum = "the code of datum. Available: %s" % parsemodis.DATUM_LIST
    help_datum = removeBracs(help_datum)
    parser.add_option("-d", "--datum", dest="datum", default="WGS84",
                      type='choice', choices=parsemodis.DATUM_LIST,
                      help=help_datum + " [default: %default]")
    help_resampl = "the type of resampling. Available: %s" % parsemodis.RESAM_LIST
    help_resampl = removeBracs(help_resampl)
    parser.add_option("-r", "--resampl", dest="resampl",
                      help=help_resampl + " [default: %default]",
                      metavar="RESAMPLING_TYPE", default='NEAREST_NEIGHBOR',
                      type='choice', choices=parsemodis.RESAM_LIST)
    parser.add_option("-p", "--proj_parameters", dest="pp",
                      metavar="PROJECTION_PARAMETERS",
                      default='( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0' \
                      ' 0.0 0.0 0.0 0.0 )',
                      help="a list of projection parameters, for more info "\
                      "check the 'Appendix C' of MODIS reprojection tool user"\
                      "'s manual https://lpdaac.usgs.gov/content/download" \
                      "/4831/22895/file/mrt41_usermanual_032811.pdf "\
                      "[default: %default]")
    help_pt = "the output projection system. Available: %s" % parsemodis.PROJ_LIST
    help_pt = removeBracs(help_pt)
    parser.add_option("-t", "--proj_type", dest="pt", default='GEO',
                      type='choice', metavar="PROJECTION_SYSTEM",
                      choices=parsemodis.PROJ_LIST, action='store',
                      help=help_pt + " [default: %default]")
    parser.add_option("-u", "--utm", dest="utm", metavar="UTM_ZONE",
                      help="the UTM zone if projection system is UTM")
    #return options and argument
    (options, args) = parser.parse_args()
    #check the argument
    if len(args) > 1:
        parser.error("You have to pass the name of HDF file.")
    if not os.path.isfile(args[0]):
        parser.error("You have to pass the name of HDF file.")

    if string.find(options.subset, '(') == -1 or  string.find(options.subset, ')') == -1:
        parser.error('ERROR: The spectral string should be similar to: "( 1 0 )"')

    if not options.output.endswith('.tif') and \
        not options.output.endswith('.hdf') and \
        not options.output.endswith('.hdr'):
            parser.error("Valid extensions for output are .hdf, .hdr, or .tif")

    modisParse = parsemodis.parseModis(args[0])
    confname = modisParse.confResample(options.subset, options.res,
                                       options.output, options.datum,
                                       options.resampl, options.pt,
                                       options.utm, options.pp)
    modisConver = convertmodis.convertModis(args[0], confname, options.mrt)
    modisConver.run()

#add options
if __name__ == "__main__":
    main()

