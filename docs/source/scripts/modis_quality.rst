modis_quality.py
------------------

**modis_quality.pys** 

Usage
^^^^^^
::

    modis_quality.py [options] input_file destination_file

Options
^^^^^^^
::

    -h  --help     show the help
    -t TYPE, --type=TYPE  Quality type either as number or name (e.g. 1
			  or VIQuality [default=1]

Examples
^^^^^^^^

Extract VI Usefulness value from MOD13 product ::
	
	modis_quality.py -t 2 infile.hdf outfile.tif

Extract shadow mask from MOD13 product ::
	
	modis_quality.py -t 9 input_file.hdf destination_file.tif
	
.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position