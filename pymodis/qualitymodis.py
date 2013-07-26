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

from datetime import *
import os
import sys
import numpy as np
from osgeo import gdal, gdal_array


VALIDTYPES = {'13' : map(str,range(1,10)), '11' : map(str,range(1,6))}


QAindices = {QAGrp1 : (8, [[-2, None],[-6, -2],[-8, -6],[-9, -8],[-10, -9],[-11, -10],[-14, -11],[-15, -14], [-16, -15]]),\\ # MOD13
			 QAGrp2 : (7, [[-2, None],[-3, -2],[-4, -3],[-6, -4],[-8, -6]],\\
			 QAGrp3 : (7, [[-3, None],[-6, -3],[-7, -6]])
 
class QualityModis():
	"""A Class for the extraction and transformation of MODIS 
	quality layers to specific information"""
	def __init__(self, infile, outfile, qType = None, qaLayer = None):
		"""Initialization function :

		   infile = the full path to the hdf file

		   outfile = the full path to the paramater file

		   mrtpath = the full path to mrt directory where inside you have bin and
		   data directories
		"""
		self.infile = infile
		self.outfile = outfile
		self.qType = qType
		self.qaLayer = qaLayer
		
	def loadData(self):
		"""loads the input file to the object"""
		os.path.isfile(self.infile)
		self.ds = gdal.Open(self.infile)
		
	def setProductType(self):
		"""reads productType from Metadata of hdf file"""
		self.productType = self.ds.GetMetadata()['SHORTNAME']
	
	def setProductGroup(self):
		"""reads productType from Metadata of hdf file"""
		self.productGroup = self.productType[3:5]
	
	def setDSversion(self):
		""""""
		self.productType = self.ds.GetMetadata()['VERSIONID']
	
	def getQAIndex(self):
		
	
	def loadQaArray(self):
		"""loads the QA layer to the object"""
		self.qaArray = gdal_array.LoadFile(self.ds.GetSubDatasets()[2][0])
	
	def exportData(self):
		"""writes calculated QA values to physical .tif file"""
		qaDS = gdal.Open(self.ds.GetSubDatasets()[2][0])
		dr = gdal.GetDriverByName('GTiff')
		outds = dr.Create(self.outfile, self.ncols, self.nrows, 1, gdal.GDT_Byte)
		outds.SetProjection(qaDS.GetProjection())
		outds.SetGeoTransform(qaDS.GetGeoTransform())
		outds.GetRasterBand(1).WriteArray(self.qaOut)
		outds = None
		qaDS = None
			
	def qualityConvertMOD13(self, modisQaValue, type = '1'):
		"""
		This function returns binary values for MOD13 products according to [1]
		
		Input: decimal value of VI Quality layer
		
		Output: list of nine binary quality parameters
		1: VI Quality
		2: VI Usefulness
		3: Aerosol Quantity
		4: Adjacent cloud detected
		5: Atmosphere BRDF Correction
		6: Mixed Clouds
		7: Land/Water mask
		8: Possible snow/ice
		9: Possible Shadow
		
		[1] Solano, R. et al., 2010. MODIS Vegetation Indices (MOD13) C5 Users Guide. 
		
		"""
		if type in ['VIQuality', '1', None]:
			return np.binary_repr(modisQaValue, 16)[-2:]
		elif type in ['VIUsefulness', '2', None]:
			return np.binary_repr(modisQaValue, 16)[-6:-2]
		elif type in ['aerosolQuantity', '3', None]:
			return np.binary_repr(modisQaValue, 16)[-8:-6]
		elif type in ['adjacentCloudDetected', '4', None]:
			return np.binary_repr(modisQaValue, 16)[-9:-8]
		elif type in ['atmosphericBRDFCorr', '5', None]:
			return np.binary_repr(modisQaValue, 16)[-10:-9]
		elif type in ['mixedClouds', '6', None]:
			return np.binary_repr(modisQaValue, 16)[-11:-10]
		elif type in ['landWaterMask', '7', None]:
			return np.binary_repr(modisQaValue, 16)[-14:-11]
		elif type in ['iceSnow', '8', None]:
			return np.binary_repr(modisQaValue, 16)[-15:-14]
		elif type in ['shadow', '9', None]:
			return np.binary_repr(modisQaValue, 16)[-16:-15]
		else:
			print "This type is not supported"

	def qualityConvertMOD11(self, modisQaValue, productType, type = '1', layer = '1'):
		"""This function returns binary values for MOD11 products"""
		if productType in ['MOD11C1','MOD11C2','MOD11C3', 'MYD11C1','MYD11C2','MYD11C3']:
			if layer in ['1','2']:
				if type in ['1']:
					return np.binary_repr(modisQaValue, 7)[-2:]
				elif type in ['2']:
					return np.binary_repr(modisQaValue, 7)[-3]
				elif type in ['3']:
					return np.binary_repr(modisQaValue, 7)[-4]
				elif type in ['4']:
					return np.binary_repr(modisQaValue, 7)[-6:-4]
				elif type in ['5']:
					return np.binary_repr(modisQaValue, 7)[-8:-6]
				else:
					"This type is not supported"
			if layer in ['3']:
				if type in ['1']:
					return np.binary_repr(modisQaValue, 7)[-3:]
				elif type in ['2']:
					return np.binary_repr(modisQaValue, 7)[-6:-3]
				elif type in ['3']:
					return np.binary_repr(modisQaValue, 7)[-7]			
		"""		
		#Version4
		else:
			if type in ['MandatoryQAFlag', '1', None]:
				return np.binary_repr(modisQaValue, 8)[-2:]
			elif type in ['DataQualityFlag', '2', None]:
				return np.binary_repr(modisQaValue, 8)[-4:-2]
			elif type in ['EmissivityErrorFlag', '3', None]:
				return np.binary_repr(modisQaValue, 8)[-6:-4]
			elif type in ['LSTErrorFlag', '4', None]:
				return np.binary_repr(modisQaValue, 8)[:-6]
			else:
				print "This type is not supported"
		"""
	def run(self):
		"""Function defines the entire process"""
		self.loadData()
		self.setProductType()
		self.setProductGroup()
		print self.productGroup
		self.setDSversion()
		self.loadQaArray()
		self.nrows, self.ncols = self.qaArray.shape
		print "type:", self.qType
		self.qaOut = np.zeros_like(self.qaArray, dtype = np.int8)
		print "Conversion started !"
		
		if self.productGroup == '13' and self.qType in VALIDTYPES[self.productGroup]:
			for val in np.unique(self.qaArray):
				ind = np.where(self.qaArray == val)
				self.qaOut[ind] = int(self.qualityConvertMOD13(self.qaArray[ind][0], self.qType),2)
		else:
			print "This MODIS type is currently not supported."
		self.exportData()
		print "Export finished!"