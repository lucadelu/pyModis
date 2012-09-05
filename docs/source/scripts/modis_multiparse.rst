modis_multiparse.py
--------------------

**modis_multiparse.py** is a script to parse several XML metadata files 
for MODIS tiles. It is very usefull to create XML metadata file for a 
mosaic.

Usage
^^^^^^
::

    modis_multiparse.py [options] hdf_files_list

Options
^^^^^^^
::
    
    -h  --help     show the help
    -b             print the values related to the spatial max extent
    -w  --write    write the MODIS XML metadata file for MODIS mosaic

Examples
^^^^^^^^

Print values of spatial bounding box ::

    modis_multiparse.py -b FILE1 FILE2 ...

Write xml file to use with hdf file create by :doc:`modis_convert` ::

    modis_multiparse.py -w FILE_mosaic.xml FILE1 FILE2 ...
