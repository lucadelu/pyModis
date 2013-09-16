modis_download_from_list.py
------------------------------

**modis_download_from_list.py** is a script to download MODIS data from NASA servers,
the name of file to download has to be contained into a text file.

Usage
^^^^^

::

    modis_download_from_list.py [options] destination_folder

Options
^^^^^^^
::

    -h  --help        show the help message and exit
    -f  --file        Input file containing data to donwload
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
    -x                this is useful for debugging the download
                      [default=False]
    -j                download also the jpeg files [default=False]


Examples
^^^^^^^^

The following text should be in your *MODTilesToDownload.txt* file ::

  MOD11A1.A2012279.h19v11.005.*.hdf*
  MOD11A1.A2012279.h19v12.005.*.hdf*
  MOD11A1.A2012279.h20v11.005.*.hdf*
  MOD11A1.A2012279.h20v12.005.*.hdf*
  MOD11A1.A2012279.h21v11.005.*.hdf*


Download Terra LST data from the above text file ::

    modis_download_from_list.py -f /tmp/MODTilesToDownload.txt /tmp

The following text should be in your *MYDTilesToDownload.txt* file ::

  MYD11A1.A2012279.h19v11.005.*.hdf*
  MYD11A1.A2012279.h19v12.005.*.hdf*
  MYD11A1.A2012279.h20v11.005.*.hdf*
  MYD11A1.A2012279.h20v12.005.*.hdf*
  MYD11A1.A2012279.h21v11.005.*.hdf*

Download Aqua LST data from the above text file ::

    modis_download_from_list.py -s MOLA -p MYD11A1.005 -f /tmp/MYDTilesToDownload.txt /tmp