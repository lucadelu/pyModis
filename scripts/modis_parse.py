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

#import modis library
from pymodis import parsemodis, optparse_required


def readDict(dic):
    """Function to decode dictionary"""
    out = ""
    for k, v in dic.iteritems():
        out += "%s = %s\n" % (k, v)
    return out


def main():
    """Main function"""
    #usage
    usage = "usage: %prog [options] hdf_file"
    parser = optparse_required.OptionParser(usage=usage)
    #all data
    parser.add_option("-a", action="store_true", dest="all", default=False,
                      help="print all possible values of metadata")
    #spatial extent
    parser.add_option("-b", action="store_true", dest="bound", default=False,
                      help="print the values related to the spatial max extent")
    #data files
    parser.add_option("-d", action="store_true", dest="dataf", default=False,
                      help="print the values related to the date files")
    #data granule
    parser.add_option("-e", action="store_true", dest="datae", default=False,
                      help="print the values related to the ECSDataGranule")
    #input files
    parser.add_option("-i", action="store_true", dest="input", default=False,
                      help="print the input layers")
    #other values
    parser.add_option("-o", action="store_true", dest="other", default=False,
                      help="print the other values")
    #platform information
    parser.add_option("-p", action="store_true", dest="plat", default=False,
                      help="print the values related to platform")
    #data quality
    parser.add_option("-q", action="store_true", dest="qa", default=False,
                      help="print the values related to quality")
    #psas
    parser.add_option("-s", action="store_true", dest="psas", default=False,
                      help="print the values related to psas")
    #time
    parser.add_option("-t", action="store_true", dest="time", default=False,
                      help="print the values related to times")
    #write into file
    parser.add_option("-w", "--write", dest="output", metavar="OUTPUT_FILE",
                      help="write the chosen information into a file")

    #return options and argument
    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("You have to pass the name of HDF file")
    #create modis object
    modisOgg = parsemodis.parseModis(args[0])
    #the output string
    outString = ""

    if options.all or options.bound:
        outString += readDict(modisOgg.retBoundary())
    if options.all or options.time:
        outString += "InsertTime = %s\n" % modisOgg.retInsertTime()
        outString += "LastUpdate = %s\n" % modisOgg.retLastUpdate()
        outString += readDict(modisOgg.retRangeTime())
    if options.all or options.datae:
        outString += readDict(modisOgg.retDataGranule())
    if options.all or options.dataf:
        outString += readDict(modisOgg.retDataFiles())
    if options.all or options.input:
        outString += 'InputFiles = '
        outString += ', '.join(modisOgg.retInputGranule())
    if options.all or options.plat:
        outString += readDict(modisOgg.retPlatform())
    if options.all or options.psas:
        outString += readDict(modisOgg.retPSA())
    if options.all or options.qa:
        out = modisOgg.retMeasure()
        outString += readDict(out['QAStats'])
        outString += readDict(out['QAFlags'])
    if options.all or options.plat:
        outString += readDict(modisOgg.retPlatform())
    if options.all or options.other:
        outString += readDict(modisOgg.retCollectionMetaData())
        outString += "PGEVersion = %s\n" % modisOgg.retPGEVersion()
        outString += "BrowseProduct = %s\n" % modisOgg.retBrowseProduct()
    #if write option it is set write the string into file
    if options.output:
        outFile = open(options.output, 'w')
        outFile.write(outString)
        outFile.close()
        print "%s write correctly" % options.write
    #else print the string
    else:
        print outString

#add options
if __name__ == "__main__":
    main()

