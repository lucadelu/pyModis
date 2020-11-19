from __future__ import print_function
import warnings

from . import downmodis
from . import parsemodis
from . import convertmodis
from . import optparse_required
try:
    from . import qualitymodis
    from . import convertmodis_gdal
except ImportError:
    warnings.warn("qualitymodis and convertmodis_gdal modules not enabled, "
                  "maybe Python GDAL is missing", ImportWarning)
    pass
from . import productmodis
try:
    from . import optparse_gui
except:
    warnings.warn("WxPython missing, no GUI enabled", ImportWarning)
__version__ = '2.2.0'
