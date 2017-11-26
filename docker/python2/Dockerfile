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

# where to store the MODIS data, run the container using -v /path/on/host:/export to access directory
VOLUME ["/export"]
ENTRYPOINT ["python", "/usr/local/bin/modis_download.py", "/export"]
