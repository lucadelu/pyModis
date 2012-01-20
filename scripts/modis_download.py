#!/usr/bin/python
# -*- coding: utf-8 -*-

#import system library
import sys
import optparse
#import modis library
from pymodis import downmodis

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
    usage = "usage: %prog [options] destination_folder"
    parser = OptionParser(usage=usage)
    #password
    parser.add_option("-P", "--password", dest="password",
                      help="password for connect to ftp server", required=True)
    #username
    parser.add_option("-U", "--username", dest="user", default = "anonymous",
                      help="username for connect to ftp server")
    #url
    parser.add_option("-u", "--url", default = "e4ftl01u.ecs.nasa.gov",
                      help="ftp server url [default=%default]", dest="url")
    #tiles
    parser.add_option("-t", "--tiles", dest="tiles", default="None",
                      help="string of tiles separated from comma, " \
                      + "[default=%default for all tiles]")
    #path to add the url
    parser.add_option("-s", "--source", dest="path", default="MOLT/MOD11A1.005"
                      , help="directory on the ftp like, " \
                      + "[default=%default]")
    #delta
    parser.add_option("-D", "--delta", dest="delta", default=10,
                      help="delta of day from the first day, " \
                      + "[default=%default]")
    #first day
    parser.add_option("-f", "--firstday", dest="today", default=None,
                      help="the day to start download, " \
                      + "[default=%default is for today]; if you want change" \
                      " data you must use this format YYYY-MM-DD")
    #first day
    parser.add_option("-e", "--endday", dest="enday", default=None,
                      help="the day to start download, " \
                      + "[default=%default]; if you want change" \
                      " data you must use this format YYYY-MM-DD")
    #debug
    parser.add_option("-x", action="store_true", dest="debug", default=True,
                      help="this is useful for debug the download")
    #jpg
    parser.add_option("-j", action="store_true", dest="jpg", default=True,
                      help="download also the jpeg files, [default=%default]")
    #only one day
    parser.add_option("-O", dest="oneday", action="store_true", default=True, 
                      help="download only one day, it set delta=1")
    #parser.add_option("-A", dest="alldays", action="store_true", default=True,
                      #help="download all days from the first")

    #set false several options
    parser.set_defaults(oneday=False)
    parser.set_defaults(debug=False)
    parser.set_defaults(jpg=False)

    #return options and argument
    (options, args) = parser.parse_args()
    #test if args[0] it is set
    if len(args) == 0:
        parser.error("You have to pass the destination folder for HDF file")
    #check if oneday option it is set
    if options.oneday:
        options.delta = 1;

    #set modis object
    modisOgg = downmodis.downModis(url = options.url, user = options.user, 
        password = options.password, destinationFolder = args[0], 
        tiles = options.tiles, path = options.path, today = options.today, 
        enddate = options.enday, delta = int(options.delta), jpg = options.jpg,
        debug = options.debug)
    #connect to ftp
    modisOgg.connectFTP()
    #download data
    modisOgg.downloadsAllDay()
    

#add options
if __name__ == "__main__":
    main()
