FROM ubuntu:16.04

# http://www.pymodis.org/ docker image

MAINTAINER Luca Delucchi

# system environment
ENV DEBIAN_FRONTEND noninteractive

# fetch dependencies
RUN apt-get update \
    && apt-get install -y \
    gdal-bin \
    python3-numpy \
    python3 \
    python3-gdal \
    ipython3 \
    python3-pip \
    python3-future \
    python3-requests

RUN apt-get autoremove && apt-get clean

# Install pyModis
RUN pip3 install pyModis
