modis_convert
-------------

**modis_convert** is a script to convert MODIS data to TIF file.
    
Options
^^^^^^^
::

    -h  --help               show the help
    -s  --subset             a subset of product's layers. The string
                             should be similar to: 1 0    [required]
    -m  --mrt                the path to MRT software    [required]
    -o  --output             the name of output file                  
    -g  --grain              the spatial resolution of output file    
    -d  --datum              the code of datum [#datum]_              
    -r  --resampl            the type of resampling
    -p  --proj_parameters    a list of projection parameters [#proj]_
    -t  --proj_type          the output projection system
    -u  --utm                the UTM zone if projection system is UTM

..
    +--------+-------------------+------------------------------------------+----------+
    | Option |   Long Option     |                    Help                  | Required |
    +--------+-------------------+------------------------------------------+----------+
    |   -s   | --subset          | a subset of product's layers. The        |   True   |
    |        |                   | string should be similar to: 1 0         |          |
    +--------+-------------------+------------------------------------------+----------+
    |   -m   | --mrt             | the path to MRT software                 |   True   |
    +--------+-------------------+------------------------------------------+----------+
    |   -o   | --output          | the name of output file                  |          |
    +--------+-------------------+------------------------------------------+----------+
    |   -g   | --grain           | the spatial resolution of output file    |          |
    +--------+-------------------+------------------------------------------+----------+
    |   -d   | --datum           | the code of datum [#datum]_              |          |
    +--------+-------------------+------------------------------------------+----------+
    |   -r   | --resampl         | the type of resampling                   |          |
    +--------+-------------------+------------------------------------------+----------+
    |   -p   | --proj_parameters | a list of projection parameters [#proj]_ |          |
    +--------+-------------------+------------------------------------------+----------+
    |   -t   | --proj_type       | the output projection system             |          |
    +--------+-------------------+------------------------------------------+----------+
    |   -u   | --utm             | the UTM zone if projection system is UTM |          |
    +--------+-------------------+------------------------------------------+----------+

Examples
^^^^^^^^
Qua di sotto ci saranno gli esempi
    
.. rubric:: Footnotes

.. [#datum] Check the 
.. [#proj] For more info check the 'Appendix C' of MODIS reprojection tool user's `manual`_

.. _manual: https://lpdaac.usgs.gov/content/download/4831/22895/file/mrt41_usermanual_032811.pdf
