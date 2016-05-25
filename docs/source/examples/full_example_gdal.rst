Example of a full process with GDAL library
=====================================================

In this short example you will learn how to run a series of
scripts to obtain a GeoTIFF file for each band of the
chosen product using as backend GDAL library.

.. warning::

  This example is based on a Linux based system. If you use
  another operating system you need to change the paths where data will be saved

.. _download-data:

Downloading data
-------------------

For first you need to obtain data, so you need to use :doc:`../scripts/modis_download`

::

  mkdir $HOME/tmp
  modis_download.py -f 2012-12-05 -O -t h28v05,h29v05,h28v04 $HOME/tmp

.. warning::

  In this example we are working on the spatial extent of Italy:
  for your area of interest, change the tile name(s) according to your region.

  In this example we download data for only one day (2012-12-05)
  using the option "-O".

Inside the ``$HOME/tmp/`` directory you will find a file called *listfileMOD11A1.005.txt*
containing the names of downloaded files. The name of file is related to
the product that you want to download.

.. warning::

  Every time that you download new files of the same product they will be overwritten,
  so if you need them, you must rename the file before.

Mosaic data
--------------

At this point you need to create the mosaic of the tiles downloaded.
:doc:`../scripts/modis_mosaic` is the script to use. We create a *VRT*
file (``flag -v``) to improve the speed of analysis, without losing any data
only for the first layer ::

    modis_mosaic.py -s "1" -o $HOME/tmp/mosaik -v $HOME/tmp/listfileMOD11A1.005.txt

The command will create a file called ``mosaik_LST_Day_1km.vrt`` in $HOME/tmp/
directory

Convert data
---------------

The last part of the procedure is to convert the mosaic using
:doc:`../scripts/modis_convert`. Using *VRT* format it create dataset
of only one later, so you are forced to use ``-s "( 1 )"``. The
following command create a GeoTIFF file called
final_mosaik_LST_Day_1km.vrt.tif ::

    modis_convert.py -v -s "( 1 )" -o $HOME/tmp/final -e 4326 $HOME/tmp/mosaik_LST_Day_1km.vrt
