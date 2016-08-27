.. pyModis documentation master file, created by
   sphinx-quickstart on Thu Jun 28 10:50:11 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyModis
==================

``pyModis`` is a Free and Open Source Python based library to work with MODIS data.
It offers bulk-download for user selected time ranges, mosaicking of MODIS tiles,
and the reprojection from Sinusoidal to other projections, convert HDF format to
other formats and the extraction of data quality information.

``pyModis`` library was developed to replace old bash scripts developed by Markus
Neteler to download MODIS data from NASA FTP server. It is very useful for
`GIS and Remote Sensing Platform`_ of `Fondazione Edmund Mach`_ to update
its large collection of MODIS data.

It has several features:

* for downloading large numbers of MODIS HDF/XML files and for using
  it in a cron job for continuous automated updating; it
  supports both FTP and HTTP NASA repositories

* parses the XML file to obtain information about the HDF files

* converts a HDF MODIS file to GEOTIFF format by either using `MODIS Reprojection Tool`_
  or `GDAL`_ (pyModis >= 1.0)

* creates a mosaic of several tiles by either using `MODIS Reprojection Tool`_ or
  `GDAL`_ (pyModis >=  1.0)

* creates the XML metadata file with the information of all tiles used for the mosaic

* extracts specific information from bit-encoded MODIS quality assessment layers
  of different product types

* Graphical User Interface for each script written in `wxPython`_ (pyModis >=  1.0)

* it support Python 2 and Python 3 (pyModis >= 2.0)

.. only:: latex

   We acknowledge the `Fondazione Edmund Mach`_ for promoting the development of
   free and open source software.

.. only:: html

   Contents:

.. toctree::
   :maxdepth: 2

   info
   scripts/software
   examples/examples
   pymodis/modules

.. only:: html

   We acknowledge the `Fondazione Edmund Mach`_ for promoting the development of
   free and open source software.

.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`

.. _GIS and Remote Sensing Platform: http://gis.cri.fmach.it
.. _Fondazione Edmund Mach: http://www.fmach.it
.. _MODIS Reprojection Tool: https://lpdaac.usgs.gov/lpdaac/tools/modis_reprojection_tool
.. _GDAL: http://www.gdal.org
.. _wxPython: http://www.wxpython.org/
