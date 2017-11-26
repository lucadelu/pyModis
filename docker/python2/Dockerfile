FROM ubuntu:16.04

# http://www.pymodis.org/ docker image

MAINTAINER Luca Delucchi

# system environment
ENV DEBIAN_FRONTEND noninteractive

# fetch dependencies
RUN apt-get update \
    && apt-get install -y \
    gdal-bin \
    python-numpy \
    python \
    python-gdal \
    ipython \
    python-pip \
    python-future \
    python-requests

RUN apt-get autoremove && apt-get clean

# Install pyModis
RUN pip install pyModis

# make scripts available as dockerized applications
ADD modis_download.py /modis_download.py
ADD modis_download_from_list.py /modis_download_from_list.py
ADD modis_convert.py /modis_convert.py
ADD modis_mosaic.py /modis_mosaic.py
ADD modis_parse.py /modis_parse.py
ADD modis_multiparse.py /modis_multiparse.py
ADD modis_quality.py /modis_quality.py

RUN chmod +x modis_download.py modis_download_from_list.py modis_convert.py modis_mosaic.py modis_parse.py modis_multiparse.py modis_quality.py

WORKDIR /

