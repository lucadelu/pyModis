modis_download.py
------------------

**modis_download.py** is a script to download MODIS data from NASA FTP servers. It can download large amounts of data and it can be profitably used with cron jobs to receive data with a fixed delay of time.

Usage
^^^^^

::

    modis_download.py [options] destination_folder

Options
^^^^^^^
::

    -h  --help        show the help   
    -P  --password    password to connect to ftp server, 
                      usually your email address  [required]
    -U  --username    username to connect to ftp server 
                      [default=anonymous]
    -u  --url         ftp server url [default=e4ftl01.cr.usgs.gov]
    -t  --tiles       string of tiles separated from comma 
                      ([default=None] for all tiles)
    -s  --source      directory on the ftp 
                      ([default=MOLT/MOD11A1.005] for Terra LST data)
    -D  --delta       delta of day from the first day [default=10]
    -f  --firstday    the day to start download, if you want change
                      data you have to use this format YYYY-MM-DD
                      ([default=None] is for today)
    -e  --enddaythe   day to finish download, if you want change
                      data you have to use this format YYYY-MM-DD
                      ([default=None] use delta option)
    -x                this is useful for debugging the download
                      [default=False]
    -j                download also the jpeg files [default=False]
    -O                download only one day, it set delta=1 [default=False]
    -A                download all days, it usefull for first download of a
                      product. It overwrite the 'firstday' and 'endday'
                      options [default=False]
    -r                remove files with size ugual to zero from
                      'destination_folder'  [default=False]


Examples
^^^^^^^^

Download Terra LST data for a month for Europe ::

    modis_download.py -P your.mail@prov.org -t TODO -f 2008-01-01 -e 2008-01-31

Download the last 15 days of Aqua LST data ::

    modis_download.py -P your.mail@prov.org -s MOLA/MYD11A1.005 -t TODO -D 15

Download all tiles of NDVI for one day (you have know the rigth day otherwise it download nothing) ::

    modis_download.py -P your.mail@prov.org -s TODO -f 2010-12-31 -O

.. only:: latex

  .. raw:: latex

    \newpage % hard pagebreak at exactly this position