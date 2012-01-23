#!/usr/bin/python

#import system library
import sys, os
import optparse
import string
#import modis library
from pymodis import convertmodis


#classes for required options
strREQUIRED = 'required'

class OptionWithDefault(optparse.Option):
    ATTRS = optparse.Option.ATTRS + [strREQUIRED]

    def __init__(self, *opts, **attrs):
        if attrs.get(strREQUIRED, False):
            attrs['help'] = '(Required) ' + attrs.get('help', "")
        optparse.Option.__init__(self, *opts, **attrs)

class OptionParser(optparse.OptionParser):
    def __init__(self, **kwargs):
        kwargs['option_class'] = OptionWithDefault
        optparse.OptionParser.__init__(self, **kwargs)
    
    def check_values(self, values, args):
        for option in self.option_list:
            if hasattr(option, strREQUIRED) and option.required:
                if not getattr(values, option.dest):
                    self.error("option %s is required" % (str(option)))
        return optparse.OptionParser.check_values(self, values, args)

def main():
    """Main function"""
    #usage
    usage = "usage: %prog [options] hdflist_file"
    parser = OptionParser(usage=usage)
    #spatial extent
    #mrt path
    parser.add_option("-m", "--mrt", dest="mrt", required=True,
                      help="the path to MRT software")    
    parser.add_option("-o", "--output", dest="output", required=True,
                      help="the name of output mosaic")
    #write into file
    parser.add_option("-s", "--subset", dest="subset",
                      help="a subset of product's layers. The string should be similar to: 1 0")

    (options, args) = parser.parse_args()

    #check the number of tiles
    if len(args) > 1:
        parser.error("You have to pass the name of a file containing HDF files. (One HDF file for line)")

    if not os.path.isfile(args[0]):
        parser.error("You have to pass the name of a file containing HDF files. (One HDF file for line)")

    #check is a subset it is set
    if not options.subset:
        options.subset = False
    else:
        if string.find(options.subset, '(') != -1 or  string.find(options.subset, ')') != -1:
            print 'ERROR: The spectral string should be similar to: "1 0"'

    modisOgg = convertmodis.createMosaic(args[0], options.output, options.mrt, options.subset)
    modisOgg.run()

#add options
if __name__ == "__main__":
    main()

