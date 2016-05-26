#!/usr/bin/env python
#  class to convert/process modis data
#
#  (c) Copyright Ingmar Nitze 2013
#  Authors: Ingmar Nitze, Luca Delucchi
#  Email: initze at ucc dot ie
#  Email: luca dot delucchi at iasma dot it
#
##################################################################
#
#  This MODIS Python class is licensed under the terms of GNU GPL 2.
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
##################################################################
"""A class for the extraction and transformation of MODIS quality layers to
specific information

Classes:

* :class:`QualityModis`

"""

# python 2 and 3 compatibility
from __future__ import print_function
from builtins import dict

import os
try:
    import numpy as np
except ImportError:
    raise ImportError('Numpy library not found, please install it')

try:
    import osgeo.gdal as gdal
    import osgeo.gdal_array as gdal_array
except ImportError:
    try:
        import gdal
        import gdal_array
    except ImportError:
        raise ImportError('Python GDAL library not found, please install '
                          'python-gdal')


VALIDTYPES = dict({'13': list(map(str, list(range(1, 10)))), '11': list(map(str, list(range(1, 6))))})

PRODUCTPROPS = dict({
    'MOD13Q1': ([2], ['QAGrp1']),
    'MYD13Q1': ([2], ['QAGrp1']),
    'MOD13A1': ([2], ['QAGrp1']),
    'MYD13A1': ([2], ['QAGrp1']),
    'MOD13A2': ([2], ['QAGrp1']),
    'MYD13A2': ([2], ['QAGrp1']),
    'MOD13A3': ([2], ['QAGrp1']),
    'MYD13A3': ([2], ['QAGrp1']),
    'MOD13C1': ([2], ['QAGrp1']),
    'MYD13C1': ([2], ['QAGrp1']),
    'MOD13C2': ([2], ['QAGrp1']),
    'MYD13C2': ([2], ['QAGrp1']),
    'MOD11A1': ([1, 5], ['QAGrp2', 'QAGrp2']),
    'MYD11A1': ([1, 5], ['QAGrp2', 'QAGrp2']),
    'MOD11A2': ([1, 5], ['QAGrp4', 'QAGrp4']),
    'MYD11A2': ([1, 5], ['QAGrp4', 'QAGrp4']),
    'MOD11B1': ([1, 5, -2], ['QAGrp2', 'QAGrp2', 'QAGrp3']),
    'MYD11B1': ([1, 5, -2], ['QAGrp2', 'QAGrp2', 'QAGrp3']),
    'MOD11C1': ([1, 5, -2], ['QAGrp2', 'QAGrp2', 'QAGrp3']),
    'MYD11C1': ([1, 5, -2], ['QAGrp2', 'QAGrp2', 'QAGrp3']),
    'MOD11C2': ([1, 6], ['QAGrp2', 'QAGrp2']),
    'MYD11C2': ([1, 6], ['QAGrp2', 'QAGrp2']),
    'MOD11C3': ([1, 6], ['QAGrp2', 'QAGrp2']),
    'MYD11C3': ([1, 6], ['QAGrp2', 'QAGrp2'])
})


QAindices = dict({
    'QAGrp1': (16, [[-2, None], [-6, -2], [-8, -6], [-9, -8],
               [-10, -9], [-11, -10], [-14, -11], [-15, -14],
               [-16, -15]]),
    'QAGrp2': (7, [[-2, None], [-3, -2], [-4, -3], [-6, -4],
               [-8, -6]]),
    'QAGrp3': (7, [[-3, None], [-6, -3], [-7, -6]]),
    'QAGrp4': (8, [[-2, None], [-4, -2], [-6, -4], [-8, -6]])
})


class QualityModis():
    """A Class for the extraction and transformation of MODIS
    quality layers to specific information

    :param str infile: the full path to the hdf file
    :param str outfile: the full path to the parameter file
    """

    def __init__(self, infile, outfile, qType=None, qLayer=None, pType=None):
        """Function to initialize the object"""
        self.infile = infile
        self.outfile = outfile
        self.qType = qType
        self.qLayer = qLayer
        self.qaGroup = None
        self.pType = pType

    def loadData(self):
        """loads the input file to the object"""
        os.path.isfile(self.infile)
        self.ds = gdal.Open(self.infile)

    def setProductType(self):
        """read productType from Metadata of hdf file"""
        if self.pType == None:
            self.productType = self.ds.GetMetadata()['SHORTNAME']
        else:
            self.productType = self.pType

    def setProductGroup(self):
        """read productGroup from Metadata of hdf file"""
        self.productGroup = self.productType[3:5]

    def setQAGroup(self):
        """set QA dataset group type"""
        if self.productType in list(PRODUCTPROPS.keys()):
            self.qaGroup = PRODUCTPROPS[self.productType][1][int(self.qLayer)-1]
        else:
            print("Product version is currently not supported!")

    def setQALayer(self):
        """function sets the input path of the designated QA layer"""
        self.qaLayer = self.ds.GetSubDatasets()[PRODUCTPROPS[self.productType][0][int(self.qLayer)-1]][0]

    def loadQAArray(self):
        """loads the QA layer to the object"""
        self.qaArray = gdal_array.LoadFile(self.qaLayer)

    def qualityConvert(self, modisQaValue):
        """converts encoded Bit-Field values to designated QA information"""
        startindex = QAindices[self.qaGroup][1][int(self.qType)-1][0]
        endindex = QAindices[self.qaGroup][1][int(self.qType)-1][1]
        return int(np.binary_repr(modisQaValue, QAindices[self.qaGroup][0])[startindex: endindex], 2)

    def exportData(self):
        """writes calculated QA values to physical .tif file"""
        qaDS = gdal.Open(self.qaLayer)
        dr = gdal.GetDriverByName('GTiff')
        outds = dr.Create(self.outfile, self.ncols, self.nrows, 1, gdal.GDT_Byte)
        outds.SetProjection(qaDS.GetProjection())
        outds.SetGeoTransform(qaDS.GetGeoTransform())
        outds.GetRasterBand(1).WriteArray(self.qaOut)
        outds = None
        qaDS = None

    def run(self):
        """Function defines the entire process"""
        self.loadData()
        self.setProductType()
        self.setProductGroup()
        #self.setDSversion()
        self.setQAGroup()
        self.setQALayer()
        self.loadQAArray()
        self.nrows, self.ncols = self.qaArray.shape
        print("Conversion started !")
        self.qaOut = np.zeros_like(self.qaArray, dtype=np.int8)
        if self.productGroup in ['11', '13'] and self.qType in VALIDTYPES[self.productGroup] and self.qaGroup != None:
            for val in np.unique(self.qaArray):
                ind = np.where(self.qaArray == val)
                self.qaOut[ind] = self.qualityConvert(self.qaArray[ind][0])
            self.exportData()
            print("Export finished!")
        else:
            print("This MODIS type is currently not supported.")
