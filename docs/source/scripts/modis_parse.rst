modis_parse.py
---------------

**modis_parse.pys** parses the XML metadata file for a MODIS
tile and return the requested value. It can also write the metadata information
in a text file.

Usage
^^^^^^
::

    modis_parse.py [options] hdf_file

Options
^^^^^^^

.. image:: ../_static/gui/modis_parse.png
  :scale: 35%
  :alt: GUI for modis_parse.py
  :align: left
  :class: gui

::
    
    -h  --help     show the help
    -a             print all possible values of metadata
    -b             print the values related to the spatial max extent
    -d             print the values related to the date files
    -e             print the values related to the ECSDataGranule
    -i             print the input layers
    -o             print the other values
    -p             print the values related to platform
    -q             print the values related to quality
    -s             print the values related to psas
    -t             print the values related to times
    -w  --write    write the chosen information into a file

Examples
^^^^^^^^

Return all values of metadata ::

    modis_parse.py -a FILE

Write all values to a file ::

    modis_parse.py -a -w metadata_FILE.txt FILE

Print spatial extent and quality ::

    modis_parse.py -b -q FILE

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
