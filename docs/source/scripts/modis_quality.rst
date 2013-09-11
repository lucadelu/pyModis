modis_quality.py
------------------

**modis_quality.py**

Usage
^^^^^^
::

    modis_quality.py [options] input_file destination_file

Options
^^^^^^^
::

    -h  --help               show the help
    -t  --type               quality type either as number or name (e.g. 1 [default=1])
    -l  --qualitylayer       index of qualitylayer (if more than one existent) ordered from 1..n.
                             (e.g. 2 for Nighttime LSTE QC from MOD11C1 products. [default=1])
    -p  --producttype        name of producttype, if working on a mosaic. Not necessary for raw datasets.

Examples
^^^^^^^^

Extract VI Usefulness value from MOD13 product ::

    modis_quality.py -t 2 infile.hdf outfile.tif

Extract shadow mask from MOD13 product ::

    modis_quality.py -t 9 input_file.hdf destination_file.tif

Extract Emissitivity error flag of Nighttime LSTE quality control from MOD11C1 product ::

    modis_quality.py -t 4 -l 2 infile.hdf outfile.tif

Extract MODLAND QA value from MOD13Q1 mosaic ::

    modis_quality.py -t 1 -p MOD13Q1 input_file.hdf destination_file.tif

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position