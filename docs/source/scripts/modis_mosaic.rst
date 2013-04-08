modis_mosaic.py
----------------

**modis_mosaic.py** is a script to create a mosaic of several MODIS tiles 
in HDF format.

Usage
^^^^^^
::

    modis_mosaic.py [options] hdflist_file

Options
^^^^^^^
::
    
    -h  --help      show the help
    -m  --mrt       the path to MRT software    [required]
    -o  --output    the name of output file    [required]
    -s  --subset    a subset of product's layers. The string 
                    should be similar to: 1 0 [default: all layers]

Examples
^^^^^^^^

Convert all the layers of several tiles::

    modis_mosaic.py -m "/usr/local/bin/" -o FILE_mosaik FILE1 FILE2 ...

Convert LAYERS of several LST MODIS tiles::

    modis_mosaic.py -s "1 0 1 0" -m "/usr/local/bin/" -o FILE_mosaik FILE1 FILE2 ...

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position