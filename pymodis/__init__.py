import downmodis
import parsemodis
import convertmodis
import optparse_required
import qualitymodis
import convertmodis_gdal
try:
    import optparse_gui
except ImportError:
    print "WxPython missing, no GUI enabled"
__version__ = '1.0.0'
