from __future__ import print_function

from . import downmodis
from . import parsemodis
from . import convertmodis
from . import optparse_required
try:
    from . import qualitymodis
    from . import convertmodis_gdal
except ImportError:
    print("qualitymodis and convertmodis_gdal modules not enabled, "
          "maybe Python GDAL is missing")
    pass
from . import productmodis
try:
    from . import optparse_gui
except:
    print("WxPython missing, no GUI enabled")
__version__ = '2.0.3'
