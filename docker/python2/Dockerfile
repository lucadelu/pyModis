FROM ubuntu:16.04

# http://www.pymodis.org/ docker image

MAINTAINER Luca Delucchi

# system environment
ENV DEBIAN_FRONTEND noninteractive
#### ENV CPLUS_INCLUDE_PATH=/usr/include/gdal \
####    C_INCLUDE_PATH=/usr/include/gdal

# ??     && apt-get install -y --install-recommends \

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

#    && apt-get autoremove \
#    && apt-get clean

# Install pyModis
#####? RUN pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')
RUN pip install pyModis
