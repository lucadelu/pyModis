modis_download
--------------

**modis_download** is a script to download MODIS data. It can download large amount of data and it's very useful to use with cron jobs to receive data with a fixed delay of time.::
    
Options
^^^^^^^
::
    
    -P  --password    password for connect to ftp server, 
                      usually your email address  [required]
    -U  --username    username for connect to ftp server 
                      [default=anonymous]
    -u  --url         ftp server url [default=]
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
    -x                this is useful for debug the download
    -j                download also the jpeg files [default=True]
    -O                download only one day, it set delta=1

Examples
^^^^^^^^

