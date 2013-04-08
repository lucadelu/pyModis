modis_convert.py
-----------------

**modis_convert.py** is a script to convert MODIS data to TIF formats and
different projection reference system. It is an interface to MRT mrtmosaic
software, the best application for work with HDF MODIS data.

Usage
^^^^^^
::

    modis_convert.py [options] hdf_file

Options
^^^^^^^
::

    -h  --help               show the help
    -s  --subset             a subset of product's layers. The string
                             should be similar to: 1 0    [required]
    -m  --mrt                the path to MRT software    [required]
    -o  --output             the name of output file
    -g  --grain              the spatial resolution of output file
    -d  --datum              the code of datum
    -r  --resampl            the type of resampling
    -p  --proj_parameters    a list of projection parameters
    -t  --proj_type          the output projection system
    -u  --utm                the UTM zone if projection system is UTM

.. warning::

    You can find the supported projections in the 'Appendix C' of
    `MODIS reprojection tool user's manual`_ and the datums at section
    ``Datum Conversion`` of the same manual

Examples
^^^^^^^^
Convert LAYERS from LST MODIS data with output resolution in 250 meters with
latitude and longitude reference system ::

    modis_convert.py -s "1 0 1 0" -m "/usr/local/bin/" -g 250 FILE

Convert LAYERS from NDVI MODIS data with output resolution in 500 meters with
UTM projection in the 32  zone ::

    modis_convert.py -s "1 0 1 0" -m "/usr/local/bin/" -g 500 -p UTM -u 32 FILE


.. _`MODIS reprojection tool user's manual`: https://lpdaac.usgs.gov/sites/default/files/public/mrt41_usermanual_032811.pdf

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position