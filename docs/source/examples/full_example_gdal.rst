Example of a full process with GDAL library
=====================================================

In this short example you can understand how to concatenate
the scripts to obtain a GeoTIFF file for each band of the
chosen product using as backend GDAL library.

.. warning::

  This example is based on a Linux based system. Please if
  you use other OS change the paths where data will be saved

.. _download-data:

Downloading data
-------------------

For first you need to obtain data, so you need to use :doc:`../scripts/modis_download`

::

  modis_download.py -f 2012-12-05 -O -t h28v05,h29v05,h28v04 /tmp

.. warning::

  In this example we are working on Italian extension, so please
  change the name of tiles according with your region.

  In this example we download data for only one day (2012-12-05)
  using the option "-O".

Inside ``/tmp/`` directory you will find a file called *listfileMOD11A1.005.txt*
containing the names of files downloaded. The name of file it is related to
the product that you download.

.. warning::

  Every time that you download new files of same product it will be overwrite,
  so if you need it, you should rename the file

Mosaic data
--------------

At this point you need to create the mosaic of the tiles downloaded.
:doc:`../scripts/modis_mosaic` is the script to use. We create a *VRT*
file (``flag -v``) to improve the speed of analysis, without lose any data
only for the first layer ::

    modis_mosaic.py -s "1" -o /tmp/mosaik -v /tmp/listfileMOD11A1.005.txt

The command will create a file called ``mosaik_LST_Day_1km.vrt`` in /tmp/
directory

Convert data
---------------

The last part of the procedure is to convert the mosaic using
:doc:`../scripts/modis_convert`. Using *VRT* format it create dataset
of only one later, so you are forced to use ``-s "( 1 )"``. The
following command create a GeoTIFF file called
final_mosaik_LST_Day_1km.vrt.tif ::

    modis_convert.py -v -s "( 1 )" -o /tmp/final -e 4326 /tmp/mosaik_LST_Day_1km.vrt
