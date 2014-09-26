modis_download.py
------------------
**modis_download.py** downloads MODIS data from NASA FTP servers.
It can download large amounts of data and it can be profitably
used with cron jobs to receive data with a fixed delay of time.

Usage
^^^^^

::

    modis_download.py [options] destination_folder

Options
^^^^^^^

.. image:: ../_static/gui/modis_download.png
  :scale: 60%
  :alt: GUI for modis_download.py
  :align: left
  :class: gui

::

    -h  --help        show the help message and exit
    -u  --url         http/ftp server url [default=http://e4ftl01.cr.usgs.gov]
    -P  --password    password to connect only if ftp server
    -U  --username    username to connect only if ftp server
                      [default=anonymous]
    -t  --tiles       string of tiles separated from comma 
                      [default=none] for all tiles
    -s  --source      directory on the http/ftp 
                      [default=MOLT]
    -p  --product     product name as on the http/ftp server
                      [default=MOD11A1.005]
    -D  --delta       delta of day from the first day [default=10]
    -f  --firstday    the day to start download, if you want change
                      data you have to use this format YYYY-MM-DD
                      ([default=none] is for today)
    -e  --enddaythe   day to finish download, if you want change
                      data you have to use this format YYYY-MM-DD
                      ([default=none] use delta option)
    -x                this is useful for debugging the download
                      [default=False]
    -j                download also the jpeg files [default=False]
    -O                download only one day, it set delta=1 [default=False]
    -A                download all days, it useful for first download of a
                      product. It overwrite the 'firstday' and 'endday'
                      options [default=False]
    -r                remove files with size same to zero from
                      'destination_folder'  [default=False]


Examples
^^^^^^^^

.. warning
  The target directory needs to be created beforehand.

Download Terra LST data for a month for two tiles from HTTP server ::

    modis_download.py -r -t h18v03,h18v04 -f 2008-01-01 -e 2008-01-31 lst_terra/

Download the last 15 days of Aqua LST data ::

    modis_download.py -r -s MOLA -p MYD11A1.005 -t h18v03,h18v04 -D 15 lst_aqua/

Download all tiles of NDVI for one day (you have know the right day otherwise it download nothing) ::

    modis_download.py -r -p MOD13Q1.005 -f 2010-12-31 -O

Download Snow product from FTP server

.. only:: html

  ::

    modis_download.py -u ftp://n4ftl01u.ecs.nasa.gov -p mail@pymodis.com -s SAN/MOST -p MOD10A1.005

.. only:: latex

  ::

    modis_download.py -u ftp://n4ftl01u.ecs.nasa.gov -p mail@pymodis.com
    -s SAN/MOST -p MOD10A1.005

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position
