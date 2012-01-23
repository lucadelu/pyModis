#!/usr/bin/python

#import system library
import sys, os
import optparse
import string
#import modis library
from pymodis import convertmodis, parsemodis


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

def removeBracs(s):
    s=string.replace(s,']','')
    s=string.replace(s,'[','')
    return s

def main():
    """Main function"""
    #usage
    usage = "usage: %prog [options] hdf_file"
    parser = OptionParser(usage=usage)
    #layer subset
    parser.add_option("-s", "--subset", dest = "subset", required = True,
                      help = "a subset of product's layers. The string should be similar to: 1 0")
    #mrt path
    parser.add_option("-m", "--mrt", dest = "mrt", required = True,
                      help = "the path to MRT software") 
    parser.add_option("-o", "--output", dest = "output",
                      help = "the name of output mosaic")                      
    parser.add_option("-g", "--grain", dest = "res", type = "int",
                      help = "the spatial resolution of output file")
    help_datum = "the code of datum. Available: %s"  % parsemodis.DATUM_LIST
    help_datum = removeBracs(help_datum)
    parser.add_option("-d", "--datum", dest = "datum", default = "WGS84", 
                      type='choice', choices = parsemodis.DATUM_LIST,
                      help = help_datum + " [default: %default]")
    help_resampl = "the type of resampling. Available: %s"  % parsemodis.RESAM_LIST
    help_resampl = removeBracs(help_resampl)
    parser.add_option("-r", "--resampl", dest = "resampl", default = 'NEAREST_NEIGHBOR',
                      help = help_resampl + " [default: %default]", 
                      type='choice', choices = parsemodis.RESAM_LIST)                      
    parser.add_option("-p", "--proj_parameters", dest="pp",
                      default = '( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 )',        
                      help="a list of projection parameters, for more info check the "\
                      + "'Appendix C' of MODIS reprojection tool user's manual" \
                      + "https://lpdaac.usgs.gov/content/download/4831/22895/file/mrt41_usermanual_032811.pdf [default: %default]")
    help_pt = "the output projection system. Available: %s" % parsemodis.PROJ_LIST
    help_pt = removeBracs(help_pt)
    parser.add_option("-t", "--proj_type", dest="pt", default='GEO', type='choice',
                      choices = parsemodis.PROJ_LIST, action='store',
                      help = help_pt + " [default: %default]")
    parser.add_option("-u", "--utm", dest = "utm",
                      help = "the UTM zone if projection system is UTM")
    #return options and argument
    (options, args) = parser.parse_args()
    #check the argument
    if len(args) > 1:
        parser.error("You have to pass the name of HDF file.")
    if not os.path.isfile(args[0]):    
        parser.error("You have to pass the name of HDF file.")

    if string.find(options.subset, '(') == -1 or  string.find(options.subset, ')') == -1:
        parser.error('ERROR: The spectral string should be similar to: "( 1 0 )"')

    modisParse = parsemodis.parseModis(args[0])
    confname = modisParse.confResample(options.subset, options.res, options.output,
                            options.datum, options.resampl, options.pt, 
                            options.utm, options.pp)
    modisConver = convertmodis.convertModis(args[0], confname, options.mrt)
    modisConver.run()

#add options
if __name__ == "__main__":
    main()    
