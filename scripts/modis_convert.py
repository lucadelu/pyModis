#!/usr/bin/env python
# script to convert hdf file in sinusoidal projection to another format and
# projection
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
"""Script to convert the input file HDF or VRT in different projection and
format. It is able to use MRT or GDAL as backend
"""

import os
import sys
try:
    from pymodis import optparse_gui
    WXPYTHON = True
except:
    WXPYTHON = False
from pymodis import optparse_required
from pymodis import parsemodis
from pymodis import convertmodis_gdal
from optparse import OptionGroup

try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise Exception('Python GDAL library not found, please install python-gdal')


def removeBracs(stri):
    """Remove brackets from string"""
    return stri.replace(']', '').replace('[', '')


def main():
    """Main function"""
    # usage
    usage = "usage: %prog [options] hdf_file"
    if 1 == len(sys.argv) and WXPYTHON:
        option_parser_class = optparse_gui.OptionParser
    else:
        option_parser_class = optparse_required.OptionParser
    parser = option_parser_class(usage=usage, description='modis_convert')
    groupR = OptionGroup(parser, 'General options')
    groupG = OptionGroup(parser, 'Options for GDAL')
    groupM = OptionGroup(parser, 'Options for MRT')
    # options used by both methos
    groupR.add_option("-s", "--subset", dest="subset", required=True,
                      help="a subset of product's layers. The string should "
                      "be similar to: ( 1 0 )")
    groupR.add_option("-o", "--output", dest="output", required=True,
                      help="the prefix of output file", metavar="OUTPUT_FILE")
    groupR.add_option("-g", "--grain", dest="resolution", type="float",
                      help="the spatial resolution of output file")
    help_resampl = "the method of resampling."
    help_resampl += " -- mrt methods: {res}".format(res=parsemodis.RESAM_LIST)
    help_resampl += " -- gdal methods: {res}".format(res=convertmodis_gdal.RESAM_GDAL)
    help_resampl = removeBracs(help_resampl)
    res_choice = parsemodis.RESAM_LIST + convertmodis_gdal.RESAM_GDAL
    groupR.add_option("-r", "--resampl", dest="resampling",
                      help=help_resampl + " [default=%default]",
                      metavar="RESAMPLING_TYPE", default='NEAREST_NEIGHBOR',
                      type='choice', choices=res_choice)
    # options only for GDAL
    groupG.add_option("-f", "--output-format", dest="output_format",
                      metavar="OUTPUT_FORMAT", default="GTiff",
                      help="output format supported by GDAL [default=%default]")
    groupG.add_option("-e", "--epsg", dest="epsg", metavar="EPSG",
                      help="EPSG code for the output")
    groupG.add_option("-w", "--wkt_file", dest="wkt", metavar="WKT",
                      help="file or string containing projection definition"
                      " in WKT format")
    groupG.add_option("-v", "--vrt", dest="vrt", action="store_true",
                      default=False, help="Read from a GDAL VRT file.")
    groupG.add_option("--formats", dest="formats", action="store_true",
                      help="print supported GDAL formats")
    # options only for MRT
    groupM.add_option("-m", "--mrt", dest="mrt_path", type='directory',
                      help="the path to MRT software", metavar="MRT_PATH")
    help_datum = "the code of datum. Available: {dat}".format(dat=parsemodis.DATUM_LIST)
    help_datum = removeBracs(help_datum)
    groupM.add_option("-d", "--datum", dest="datum", default="WGS84",
                      type='choice', choices=parsemodis.DATUM_LIST,
                      help=help_datum + " [default=%default]")
    help_pt = "the output projection system. Available: {proj}".format(proj=parsemodis.PROJ_LIST)
    help_pt = removeBracs(help_pt)
    groupM.add_option("-t", "--proj_type", dest="projection_type",
                      type='choice', metavar="PROJECTION_SYSTEM",
                      choices=parsemodis.PROJ_LIST, action='store',
                      help=help_pt + " [default=%default]", default='GEO')
    groupM.add_option("-p", "--proj_parameters", dest="projection_parameter",
                      metavar="PROJECTION_PARAMETERS",
                      default='( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
                      ' 0.0 0.0 0.0 0.0 )',
                      help="a list of projection parameters, for more info "
                      "check the 'Appendix C' of MODIS reprojection tool user"
                      "'s manual https://lpdaac.usgs.gov/content/download"
                      "/4831/22895/file/mrt41_usermanual_032811.pdf "
                      "[default=%default]")
    groupM.add_option("-u", "--utm", dest="utm_zone", metavar="UTM_ZONE",
                      help="the UTM zone if projection system is UTM")
    parser.add_option_group(groupR)
    parser.add_option_group(groupG)
    parser.add_option_group(groupM)
    # return options and argument
    (options, args) = parser.parse_args()
    # check the argument
    if len(args) == 0 and not WXPYTHON:
        parser.print_help()
        sys.exit(1)
    if len(args) > 1:
        parser.error("You have to define the name of HDF file.")
    if not os.path.isfile(args[0]):
        parser.error("You have to define the name of HDF file.")
    if not (options.subset.strip().startswith('(') and options.subset.strip().endswith(')')):
        parser.error('ERROR: The spectral string should be similar to: "( 1 0 )"')

    if options.mrt_path:
        if not options.output.endswith('.tif') and \
           not options.output.endswith('.hdf') and \
           not options.output.endswith('.hdr'):
            parser.error("Valid extensions for output are .hdf, .hdr, or .tif")
        from pymodis import convertmodis
        modisParse = parsemodis.parseModis(args[0])
        confname = modisParse.confResample(options.subset, options.resolution,
                                           options.output, options.datum,
                                           options.resampling,
                                           options.projection_type,
                                           options.utm_zone,
                                           options.projection_parameter)
        modisConver = convertmodis.convertModis(args[0], confname,
                                                options.mrt_path)
    else:
        modisConver = convertmodis_gdal.convertModisGDAL(args[0],
                                                         options.output,
                                                         options.subset,
                                                         options.resolution,
                                                         options.output_format,
                                                         options.epsg,
                                                         options.wkt,
                                                         options.resampling,
                                                         options.vrt)
    modisConver.run()

if __name__ == "__main__":
    gdal.AllRegister()
    argv = gdal.GeneralCmdLineProcessor(sys.argv)
    if argv is not None:
        main()
