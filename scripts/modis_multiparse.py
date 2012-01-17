#!/usr/bin/python

#import system library
import sys
import optparse
#import modis library
from pymodis import parsemodis

def readDict(dic):
    """Function to decode dictionary"""
    out=""
    for k,v in dic.iteritems():
        out += "%s = %s\n" % (k, v)
    return out

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
    usage = "usage: %prog [options] hdf_files_list"
    parser = OptionParser(usage=usage)
    #spatial extent
    parser.add_option("-b", action="store_true", dest="bound", default=False,
                      help="print the values releated to the spatial max extent")
    #write into file
    parser.add_option("-w", "--write", dest="write",
                      help="the path where write a file containing the choosen information")

    (options, args) = parser.parse_args()
    #create modis object
    if len(args) == 0:
        parser.error("You have to pass the name of HDF files")
    modisOgg = parsemodis.parseModisMulti(args)

    if options.bound:
        print readDict(modisOgg.retBoundary())
    if options.write:
        modisOgg.writexml(options.write)
        print "%s write correctly" % options.write

#add options
if __name__ == "__main__":
    main()
