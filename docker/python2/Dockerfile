FROM ubuntu:16.04

# Dockerfile by M Neteler and L Delucchi

# http://www.pymodis.org/
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
ADD /usr/local/bin/modis_download.py /
ADD /usr/local/bin/modis_download_from_list.py /
ADD /usr/local/bin/modis_convert.py /
ADD /usr/local/bin/modis_mosaic.py /
ADD /usr/local/bin/modis_parse.py /
ADD /usr/local/bin/modis_multiparse.py /
ADD /usr/local/bin/modis_quality.py /

WORKDIR /
RUN chmod +x modis_download.py modis_download_from_list.py modis_convert.py modis_mosaic.py modis_parse.py modis_multiparse.py modis_quality.py

