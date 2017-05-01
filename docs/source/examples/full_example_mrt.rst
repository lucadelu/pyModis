Example reproject data with MRT
===============================

In this short example you can understand how to concatenate
the scripts to obtain a GeoTIFF file for each band of the
chosen product using as backend MODIS Reprojection Tools (MRT).

.. warning::

  This example is based on a Linux based system. Please if
  you use other OS change the paths where data will be saved

Downloading data
----------------

For first you need to obtain data, so you need to use :doc:`../scripts/modis_download`

.. warning::

  Remember to register in the NASA portal following the instructions at :ref:`userpw-label` session

::

  modis_download.py -I -f 2012-12-05 -O -t h28v05,h29v05,h28v04 /tmp

.. warning::

  In this example we are working on Japan extension, so please
  change the name of tiles according with your region.

  User and password are passed through standard input.

  In this example we download data for only one day (2012-12-05)
  using the option "-O".

Inside ``/tmp/`` directory you will find a file called *listfileMOD11A1.005.txt*
containing the names of files downloaded. The name of file it is related to
the product that you download.

.. warning::

  Every time that you download new files of same product it will be overwrite,
  so if you need it, you should rename the file


Mosaic data
-----------

:doc:`../scripts/modis_mosaic` is the script to use.

::

  modis_mosaic.py -m /path/to/mrt/ -o /tmp/outputfile /tmp/listfileMOD11A1.005.txt

.. warning::

  ``/path/to/mrt/`` is the directory where Modis Reprojection Tools is stored

The output of this command are *outputfile.hdf* and *outputfile.hdf.xml* inside the
directory ``/tmp``. It's reading the input files contained in *listfileMOD11A1.005.txt*

Convert data
------------

The last part of the procedure is to convert the mosaic, from HDF format and sinusoidal
projection, to GeoTIFF with several projection. You have to use :doc:`../scripts/modis_convert`

.. only:: html

  ::

    modis_convert.py -s '( 1 1 1 1 1 1 1 1 1 1 1 1 )' -m /path/to/mrt/ -o /tmp/finalfile.tif -g 250 /tmp/outputfile.hdf

.. only:: latex

  ::

    modis_convert.py -s '( 1 1 1 1 1 1 1 1 1 1 1 1 )' -m /path/to/mrt/
		     -o /tmp/finalfile.tif -g 250 /tmp/outputfile.hdf

Extract quality information
---------------------------

If necessary, you can extract specific quality type from the chosen quality layer.
In this particular case, we extract the Mandatory QA flag of the daytime temperature.
You have to use :doc:`../scripts/modis_quality`

.. only:: html

  ::

    modis_quality.py -p MOD11A1 -l 1 -t 1 /tmp/outputfile.hdf /tmp/mod11a1_daytime_qaflag.tif

.. only:: latex

  ::

    modis_quality.py -p MOD11A1 -l 1 -t 1 /tmp/outputfile.hdf
    /tmp/mod11a1_daytime_qaflag.tif
