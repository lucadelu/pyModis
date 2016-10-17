#!/usr/bin/env python
#  class to parse modis data
#
#  (c) Copyright Luca Delucchi 2010
#  Authors: Luca Delucchi
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
"""Simple class to parse MODIS metadata file, it can also write the XML
metadata file for a mosaic.

Classes:

* :class:`parseModis`
* :class:`parseModisMulti`

"""

# python 2 and 3 compatibility
from builtins import dict
import os

# lists of parameters accepted by resample MRT software
# projections
PROJ_LIST = ['AEA', 'GEO', 'HAM', 'IGH', 'ISIN', 'LA', 'LCC', 'MOL', 'PS',
             'SIN', 'TM', 'UTM', 'MERCAT']
# resampling
RESAM_LIST = ['NEAREST_NEIGHBOR', 'BICUBIC', 'CUBIC_CONVOLUTION', 'NONE']
RESAM_LIST_SWATH = ['NN', 'BI', 'CC']

# datum
DATUM_LIST = ['NODATUM', 'NAD27', 'NAD83', 'WGS66', 'WGS72', 'WGS84']
SPHERE_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
               19, 20]


class parseModis:
    """Class to parse MODIS xml files, it can also create the parameter
       configuration file for resampling MODIS DATA with the MRT software or
       convertmodis Module

       :param str filename: the name of MODIS hdf file
    """

    def __init__(self, filename):
        """Function to initialize the object"""
        from xml.etree import ElementTree
        if os.path.exists(filename):
            # hdf name
            self.hdfname = filename
        else:
            raise Exception('{name} does not exist'.format(name=filename))

        if os.path.exists(self.hdfname + '.xml'):
            # xml hdf name
            self.xmlname = self.hdfname + '.xml'
        else:
            raise Exception('{name}.xml does not exist'.format(name=self.hdfname))

        # tif name for the output file for resample MRT software
        self.tifname = self.hdfname.replace('.hdf', '.tif')
        with open(self.xmlname) as f:
            self.tree = ElementTree.parse(f)
        # return the code of tile for conf file
        self.code = os.path.split(self.hdfname)[1].split('.')[-2]
        self.path = os.path.split(self.hdfname)[0]

    def __str__(self):
        """Print the file without xml tags"""
        retString = ""
        try:
            for node in self.tree.iter():
                if node.text.strip() != '':
                    retString = "{tag} = {val}\n".format(tag=node.tag,
                                                         val=node.text)
        except:
            for node in self.tree.getiterator():
                if node.text.strip() != '':
                    retString = "{tag} = {val}\n".format(tag=node.tag,
                                                         val=node.text)
        return retString

    def getRoot(self):
        """Set the root element"""
        self.rootree = self.tree.getroot()

    def retDTD(self):
        """Return the DTDVersion element"""
        self.getRoot()
        return self.rootree.find('DTDVersion').text

    def retDataCenter(self):
        """Return the DataCenterId element"""
        self.getRoot()
        return self.rootree.find('DataCenterId').text

    def getGranule(self):
        """Set the GranuleURMetaData element"""
        self.getRoot()
        self.granule = self.rootree.find('GranuleURMetaData')

    def retGranuleUR(self):
        """Return the GranuleUR element"""
        self.getGranule()
        return self.granule.find('GranuleUR').text

    def retDbID(self):
        """Return the DbID element"""
        self.getGranule()
        return self.granule.find('DbID').text

    def retInsertTime(self):
        """Return the InsertTime element"""
        self.getGranule()
        return self.granule.find('InsertTime').text

    def retLastUpdate(self):
        """Return the LastUpdate element"""
        self.getGranule()
        return self.granule.find('LastUpdate').text

    def retCollectionMetaData(self):
        """Return the CollectionMetaData element as dictionary"""
        self.getGranule()
        collect = dict()
        for i in self.granule.find('CollectionMetaData').getiterator():
            if i.text.strip() != '':
                collect[i.tag] = i.text
        return collect

    def retDataFiles(self):
        """Return the DataFiles element as dictionary"""
        self.getGranule()
        collect = dict()
        datafiles = self.granule.find('DataFiles')
        for i in datafiles.find('DataFileContainer').getiterator():
            if i.text.strip() != '':
                collect[i.tag] = i.text
        return collect

    def retDataGranule(self):
        """Return the ECSDataGranule elements as dictionary"""
        self.getGranule()
        datagran = dict()
        for i in self.granule.find('ECSDataGranule').getiterator():
            if i.text.strip() != '':
                datagran[i.tag] = i.text
        return datagran

    def retPGEVersion(self):
        """Return the PGEVersion element"""
        self.getGranule()
        return self.granule.find('PGEVersionClass').find('PGEVersion').text

    def retRangeTime(self):
        """Return the RangeDateTime elements as dictionary"""
        self.getGranule()
        rangeTime = dict()
        for i in self.granule.find('RangeDateTime').getiterator():
            if i.text.strip() != '':
                rangeTime[i.tag] = i.text
        return rangeTime

    def retBoundary(self):
        """Return the maximum extend (Bounding Box) of the MODIS file as
           dictionary"""
        self.getGranule()
        self.boundary = []
        lat = []
        lon = []
        spatialContainer = self.granule.find('SpatialDomainContainer')
        horizontal = spatialContainer.find('HorizontalSpatialDomainContainer')
        boundary = horizontal.find('GPolygon').find('Boundary')
        for i in boundary.findall('Point'):
            la = float(i.find('PointLongitude').text)
            lo = float(i.find('PointLatitude').text)
            lon.append(la)
            lat.append(lo)
            self.boundary.append({'lat': la, 'lon': lo})
        extent = dict({'min_lat': min(lat), 'max_lat': max(lat),
                       'min_lon': min(lon), 'max_lon': max(lon)})
        return extent

    def retMeasure(self):
        """Return statistics of QA as dictionary"""
        value = dict()
        self.getGranule()
        mes = self.granule.find('MeasuredParameter')
        mespcs = mes.findall('MeasuredParameterContainer')
        ind = 1
        for me in mespcs:
            value[ind] = dict()
            value[ind]['ParameterName'] = me.find('ParameterName').text
            meStat = me.find('QAStats')
            qastat = dict()
            for i in meStat.getiterator():
                if i.tag != 'QAStats':
                    qastat[i.tag] = i.text
            value[ind]['QAStats'] = qastat
            meFlag = me.find('QAFlags')
            flagstat = dict()
            for i in meFlag.getiterator():
                if i.tag != 'QAFlags':
                    flagstat[i.tag] = i.text
            value[ind]['QAFlags'] = flagstat
            ind += 1
        return value

    def getMeasureName(self, output=None):
        """Return the names of measure names

        :param str output: the path of the file where write the output
        """
        names = list()
        measures = self.retMeasure()
        for k, v in measures.items():
            names.append("{id}\t{na}".format(id=k,
                                             na=v['ParameterName']))
        if output:
            out = open(output,  'w')
            out.write("{ns}\n".format(ns='\n'.join(names)))
            out.close()
            return 0
        else:
            return "{ns}".format(ns='\n'.join(names))

    def getLayersName(self, output=None):
        """Return the names of layers using GDAL

        :param str output: the path of the file where write the output
        """
        try:
            import osgeo.gdal as gdal
        except ImportError:
            try:
                import gdal as gdal
            except ImportError:
                print('WARNING: Python GDAL library not found, please'
                      ' install it to get layers list')
        names = list()
        gd = gdal.Open(self.hdfname)
        subs = gd.GetSubDatasets()
        num = 1
        for sub in subs:
            names.append("{id}\t{na}".format(id=num,
                                             na=sub[0].split(':')[-1]))
            num += 1
        if output:
            out = open(output,  'w')
            out.write("{ns}\n".format(ns='\n'.join(names)))
            out.close()
            return 0
        else:
            return "{ns}".format(ns='\n'.join(names))

    def retPlatform(self):
        """Return the platform values as dictionary."""
        value = dict()
        self.getGranule()
        plat = self.granule.find('Platform')
        value['PlatformShortName'] = plat.find('PlatformShortName').text
        instr = plat.find('Instrument')
        value['InstrumentShortName'] = instr.find('InstrumentShortName').text
        sensor = instr.find('Sensor')
        value['SensorShortName'] = sensor.find('SensorShortName').text
        return value

    def retPSA(self):
        """Return the PSA values as dictionary, the PSAName is the key and
        and PSAValue is the value
        """
        value = dict()
        self.getGranule()
        psas = self.granule.find('PSAs')
        for i in psas.findall('PSA'):
            value[i.find('PSAName').text] = i.find('PSAValue').text
        return value

    def retInputGranule(self):
        """Return the input files (InputGranule) used to process the considered
        file"""
        value = []
        self.getGranule()
        for i in self.granule.find('InputGranule').getiterator():
            if i.tag != 'InputGranule':
                value.append(i.text)
        return value

    def retBrowseProduct(self):
        """Return the BrowseProduct element"""
        self.getGranule()
        try:
            value = self.granule.find('BrowseProduct').find('BrowseGranuleId').text
        except:
            value = None
        return value

    def confResample(self, spectral, res=None, output=None, datum='WGS84',
                     resample='NEAREST_NEIGHBOR', projtype='GEO', utm=None,
                     projpar='( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 '
                     '0.0 0.0 0.0 0.0 )', bound=None):
        """Create the parameter file to use with resample MRT software to
        create tif (geotiff) file

        :param str spectral: the spectral subset to be used, see the product
                             table to understand the layer that you want use.
                             For example:

                             * NDVI ( 1 1 1 0 0 0 0 0 0 0 0 0) copy only layer
                               NDVI, EVI and QA VI the other layers are not used
                             * LST ( 1 1 0 0 1 1 0 0 0 0 0 0 ) copy only layer
                               daily and nightly temperature and QA

        :param int res: the resolution for the output file, it must be set in
                        the map unit of output projection system. The software
                        will use the original resolution of input file if res
                        not set

        :param str output: the output name, if not set if not set the prefix
                           name of input hdf file will be used

        :param utm: the UTM zone if projection system is UTM

        :param str resample: the type of resampling, the valid values are:

                             * NN (nearest neighbor)
                             * BI (bilinear)
                             * CC (cubic convolution)

        :param str projtype: the output projection system, valid values are:

                             * AEA (Albers Equal Area)
                             * ER (Equirectangular)
                             * GEO (Geographic Latitude/Longitude)
                             * HAM (Hammer)
                             * ISIN (Integerized Sinusoidal)
                             * IGH (Interrupted Goode Homolosine)
                             * LA (Lambert Azimuthal)
                             * LCC (LambertConformal Conic)
                             * MERCAT (Mercator)
                             * MOL (Mollweide)
                             * PS (Polar Stereographic)
                             * SIN (Sinusoidal)
                             * UTM (Universal TransverseMercator)

        :param str datum: the datum to use, the valid values are:

                          * NAD27
                          * NAD83
                          * WGS66
                          * WGS76
                          * WGS84
                          * NODATUM

        :param str projpar: a list of projection parameters, for more info
                            check the Appendix C of MODIS reprojection tool
                            user manual https://lpdaac.usgs.gov/content/download/4831/22895/file/mrt41_usermanual_032811.pdf

        :param dict bound: dictionary with the following keys:

                           * max_lat
                           * max_lon
                           * min_lat
                           * min_lon
        """
        # check if spectral it's write with correct construct ( value )
        if not (spectral.strip().startswith('(') and spectral.strip().endswith(')')):
            raise Exception('ERROR: The spectral string should be similar to:'
                            ' ( 1 0 )')
        # output name
        if not output:
            fileout = self.tifname
        else:
            fileout = output
        # the name of the output parameters files for resample MRT software
        filename = os.path.join(self.path, '{cod}_mrt_resample.conf'.format(cod=self.code))
        # if the file already exists it remove it
        if os.path.exists(filename):
            os.remove(filename)
        # open the file
        conFile = open(filename, 'w')
        conFile.write("INPUT_FILENAME = {name}\n".format(name=self.hdfname))
        conFile.write("SPECTRAL_SUBSET = {spec}\n".format(spec=spectral))
        conFile.write("SPATIAL_SUBSET_TYPE = INPUT_LAT_LONG\n")
        if not bound:
            # return the boundary from the input xml file
            bound = self.retBoundary()
        else:
            if 'max_lat' not in bound or 'min_lat' not in bound or \
               'min_lon' not in bound or 'max_lon' not in bound:
                raise Exception('bound variable is a dictionary with the '
                                'following keys: max_lat, min_lat, min_lon,'
                                ' max_lon')
        # Order:  UL: N W  - LR: S E
        conFile.write("SPATIAL_SUBSET_UL_CORNER = ( {mala} {milo} )"
                      "\n".format(mala=bound['max_lat'], milo=bound['min_lon']))
        conFile.write("SPATIAL_SUBSET_LR_CORNER = ( {mila} {malo} )"
                      "\n".format(mila=bound['min_lat'], malo=bound['max_lon']))
        conFile.write("OUTPUT_FILENAME = {out}\n".format(out=fileout))
        # if resample is in resam_list set it otherwise return an error
        if resample in RESAM_LIST:
            conFile.write("RESAMPLING_TYPE = {res}\n".format(res=resample))
        else:
            raise Exception('The resampling type {res} is not supportet.\n'
                            'The resampling type supported are '
                            '{reslist}'.format(res=resample, reslist=RESAM_LIST))
        # if projtype is in proj_list set it otherwise return an error
        if projtype in PROJ_LIST:
            conFile.write("OUTPUT_PROJECTION_TYPE = {typ}\n".format(typ=projtype))
        else:
            raise Exception('The projection type {typ} is not supported.\n'
                            'The projections supported are '
                            '{proj}'.format(typ=projtype, proj=PROJ_LIST))
        conFile.write("OUTPUT_PROJECTION_PARAMETERS = {proj}\n".format(proj=projpar))
        # if datum is in datum_list set the parameter otherwise return an error
        if datum in DATUM_LIST:
            conFile.write("DATUM = {dat}\n".format(dat=datum))
        else:
            raise Exception('The datum {dat} is not supported.\n'
                            'The datum supported are '
                            '{datum}'.format(dat=datum, datum=DATUM_LIST))
        # if utm is not None write the UTM_ZONE parameter in the file
        if utm:
            conFile.write("UTM_ZONE = {zone}\n".format(zone=utm))
        # if res is not None write the OUTPUT_PIXEL_SIZE parameter in the file
        if res:
            conFile.write("OUTPUT_PIXEL_SIZE = {pix}\n".format(pix=res))
        conFile.close()
        return filename

    def confResample_swath(self, sds, geoloc, res, output=None,
                           sphere='8', resample='NN', projtype='GEO', utm=None,
                           projpar='0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 '
                           '0.0 0.0 0.0 0.0 0.0', bound=None):
        """Create the parameter file to use with resample MRT software to
           create tif (geotiff) file

        :param str sds: Name of band/s (Science Data Set) to resample
        :param str geoloc: Name geolocation file (example MOD3, MYD3)
        :param int res: the resolution for the output file, it must be set in
                        the map unit of output projection system. The software
                        will use the original resolution of input file if res
                        not set

        :param str output: the output name, if not set the prefix name of
                           input hdf file will be used

        :param int sphere: Output sphere number. Valid options are:

                           * 0=Clarke 1866
                           * 1=Clarke 1880
                           * 2=Bessel
                           * 3=International 1967
                           * 4=International 1909
                           * 5=WGS 72
                           * 6=Everest
                           * 7=WGS 66
                           * 8=GRS1980/WGS 84
                           * 9=Airy
                           * 10=Modified Everest
                           * 11=Modified Airy
                           * 12=Walbeck
                           * 13=Southeast Asia
                           * 14=Australian National
                           * 15=Krassovsky
                           * 16=Hough
                           * 17=Mercury1960
                           * 18=Modified Mercury1968
                           * 19=Sphere 19 (Radius 6370997)
                           * 20=MODIS Sphere (Radius 6371007.181)

        :param str resample: the type of resampling, the valid values are:

                             * NN (nearest neighbor)
                             * BI (bilinear)
                             * CC (cubic convolution)

        :param str projtype: the output projection system, valid values are:

                             * AEA (Albers Equal Area)
                             * ER (Equirectangular)
                             * GEO (Geographic Latitude/Longitude)
                             * HAM (Hammer)
                             * ISIN (Integerized Sinusoidal)
                             * IGH (Interrupted Goode Homolosine)
                             * LA (Lambert Azimuthal)
                             * LCC (LambertConformal Conic)
                             * MERCAT (Mercator)
                             * MOL (Mollweide)
                             * PS (Polar Stereographic),
                             * SIN ()Sinusoidal)
                             * UTM (Universal TransverseMercator)

        :param utm: the UTM zone if projection system is UTM

        :param str projpar: a list of projection parameters, for more info
                            check the Appendix C of MODIS reprojection tool
                            user manual https://lpdaac.usgs.gov/content/download/4831/22895/file/mrt41_usermanual_032811.pdf

        :param dict bound: dictionary with the following keys:

                           * max_lat
                           * max_lon
                           * min_lat
                           * min_lon
        """
        # output name
        if not output:
            fileout = self.tifname
        else:
            fileout = output
        # the name of the output parameters files for resample MRT software
        filename = os.path.join(self.path,
                                '{cod}_mrt_resample.prm'.format(cod=self.code))
        # if the file already exists it remove it
        if os.path.exists(filename):
            os.remove(filename)
        # open the file
        conFile = open(filename, 'w')
        conFile.write("INPUT_FILENAME = {name}\n".format(name=self.hdfname))
        conFile.write("GEOLOCATION_FILENAME = {name}\n".format(name=geoloc))
        conFile.write("INPUT_SDS_NAME = {name}\n".format(name=sds))
        conFile.write("OUTPUT_SPATIAL_SUBSET_TYPE = LAT_LONG\n")
        if not bound:
            # return the boundary from the input xml file
            bound = self.retBoundary()
        else:
            if 'max_lat' not in bound or 'min_lat' not in bound or \
               'min_lon' not in bound or 'max_lon' not in bound:
                raise Exception('bound variable is a dictionary with the '
                                'following keys: max_lat, min_lat, min_lon,'
                                ' max_lon')
        # Order:  UL: N W  - LR: S E
        conFile.write("OUTPUT_SPACE_UPPER_LEFT_CORNER (LONG LAT) = {milo} "
                      "{mala}\n".format(mala=bound['max_lat'],
                                        milo=bound['min_lon']))
        conFile.write("OUTPUT_SPACE_LOWER_RIGHT_CORNER (LONG LAT) = {mila} "
                      "{malo}\n".format(mila=bound['min_lat'],
                                        malo=bound['max_lon']))
        conFile.write("OUTPUT_FILENAME = {name}\n".format(name=fileout))
        conFile.write("OUTPUT_FILE_FORMAT = GEOTIFF_FMT\n")
        # if resample is in resam_list set it otherwise return an error
        if resample in RESAM_LIST_SWATH:
            conFile.write("KERNEL_TYPE (CC/BI/NN) = {res}"
                          "\n".format(res=resample))
        else:
            raise Exception('The resampling type {typ} is not supportet.\n'
                            'The resampling type supported are '
                            '{swa}'.format(typ=resample, swa=RESAM_LIST_SWATH))
        # if projtype is in proj_list set it otherwise return an error
        if projtype in PROJ_LIST:
            conFile.write("OUTPUT_PROJECTION_NUMBER = {typ}\n".format(typ=projtype))
        else:
            raise Exception('The projection type {typ} is not supported.\n'
                            'The projections supported are '
                            '{proj}'.format(typ=projtype, proj=PROJ_LIST))
        conFile.write("OUTPUT_PROJECTION_PARAMETER = {prj}\n".format(prj=projpar))
        # if sphere is in sphere_list set it otherwise return an error
        if int(sphere) in SPHERE_LIST:
            conFile.write("OUTPUT_PROJECTION_SPHERE = {sph}\n".format(sph=sphere))
        else:
            raise Exception('The sphere {sph} is not supported.\nThe spheres'
                            'supported are {sphere}'.format(sph=sphere,
                                                            sphere=SPHERE_LIST))
        # if utm is not None write the UTM_ZONE parameter in the file
        if utm:
            if utm < '-60' or utm > '60':
                raise Exception('The valid UTM zone are -60 to 60')
            else:
                conFile.write("OUTPUT_PROJECTION_ZONE = {utm}\n".format(utm=utm))
        # if res is not None write the OUTPUT_PIXEL_SIZE parameter in the file
        if res:
            conFile.write("OUTPUT_PIXEL_SIZE = {res}\n".format(res=res))
        conFile.close()
        return filename


class parseModisMulti:
    """A class to obtain some variables for the xml file of several MODIS
       tiles. It can also create the xml file

       :param list hdflist: python list containing the hdf files
    """

    def __init__(self, hdflist):
        """Function to initialize the object"""
        from xml.etree import ElementTree
        self.ElementTree = ElementTree
        self.hdflist = hdflist
        self.parModis = []
        self.nfiles = 0
        # for each hdf files create a parseModis object
        for i in hdflist:
            self.parModis.append(parseModis(i))
            self.nfiles += 1

    def _most_common(self, lst):
        """Return the most common value of a list"""
        return max(set(lst), key=lst.count)

    def _checkval(self, vals):
        """Internal function to return values from list

        :param list vals: list of values
        """
        if vals.count(vals[0]) == self.nfiles:
            return [vals[0]]
        else:
            outvals = []
            for i in vals:
                if outvals.count(i) == 0:
                    outvals.append(i)
        return outvals

    def _checkvaldict(self, vals):
        """Internal function to return values from dictionary

        :param dict vals: dictionary of values
        """
        keys = list(vals[0].keys())
        outvals = dict()
        for k in keys:
            valtemp = []
            for v in vals:
                valtemp.append(v[k])
            if valtemp.count(valtemp[0]) == self.nfiles:
                outvals[k] = valtemp[0]
            elif len(valtemp) == self.nfiles:
                outvals[k] = self._most_common(valtemp)
            else:
                raise Exception('Something wrong reading XML files')

        return outvals

    def _minval(self, vals):
        """Internal function to return the minimum value

        :param list vals: list of values
        """
        outval = vals[0]
        for i in range(1, len(vals)):
            if outval > i:
                outval = i
        return outval

    def _maxval(self, vals):
        """Internal function to return the maximum value

        :param list vals: list of values
        """
        outval = vals[0]
        for i in range(1, len(vals)):
            if outval < i:
                outval = i
        return outval

    def _cicle_values(self, obj, values):
        """Internal function to add values from a dictionary

        :param obj: element to add values

        :param values: dictionary containing keys and values
        """
        for k, v in values.items():
            elem = self.ElementTree.SubElement(obj, k)
            elem.text = v

    def _addPoint(self, obj, lon, lat):
        """Internal function to add a point in boundary xml tag

        :param obj: element to add point
        :param lon: longitude of point
        :param lat: latitude of point
        """
        pt = self.ElementTree.SubElement(obj, 'Point')
        ptlon = self.ElementTree.SubElement(pt, 'PointLongitude')
        ptlon.text = str(self.boundary[lon])
        ptlat = self.ElementTree.SubElement(pt, 'PointLatitude')
        ptlat.text = str(self.boundary[lat])

    def valDTD(self, obj):
        """Function to add DTDVersion

        :param obj: element to add DTDVersion
        """
        values = []
        for i in self.parModis:
            values.append(i.retDTD())
        for i in set(values):
            dtd = self.ElementTree.SubElement(obj, 'DTDVersion')
            dtd.text = i

    def valDataCenter(self, obj):
        """Function to add DataCenter

        :param obj: element to add DataCenter
        """
        values = []
        for i in self.parModis:
            values.append(i.retDataCenter())
        for i in set(values):
            dci = self.ElementTree.SubElement(obj, 'DataCenterId')
            dci.text = i

    def valGranuleUR(self, obj):
        """Function to add GranuleUR

        :param obj: element to add GranuleUR
        """
        values = []
        for i in self.parModis:
            values.append(i.retGranuleUR())
        for i in set(values):
            gur = self.ElementTree.SubElement(obj, 'GranuleUR')
            gur.text = i

    def valDbID(self, obj):
        """Function to add DbID

        :param obj: element to add DbID
        """
        values = []
        for i in self.parModis:
            values.append(i.retDbID())
        for i in set(values):
            dbid = self.ElementTree.SubElement(obj, 'DbID')
            dbid.text = i

    def valInsTime(self, obj):
        """Function to add the minimum of InsertTime

        :param obj: element to add InsertTime
        """
        values = []
        for i in self.parModis:
            values.append(i.retInsertTime())
        obj.text = self._minval(values)

    def valCollectionMetaData(self, obj):
        """Function to add CollectionMetaData

        :param obj: element to add CollectionMetaData
        """
        values = []
        for i in self.parModis:
            values.append(i.retCollectionMetaData())
        self._cicle_values(obj, self._checkvaldict(values))

    def valDataFiles(self, obj):
        """Function to add DataFileContainer

        :param obj: element to add DataFileContainer
        """
        values = []
        for i in self.parModis:
            values.append(i.retDataFiles())
        for i in values:
            dfc = self.ElementTree.SubElement(obj, 'DataFileContainer')
            self._cicle_values(dfc, i)

    def valPGEVersion(self, obj):
        """Function to add PGEVersion

        :param obj: element to add PGEVersion
        """
        values = []
        for i in self.parModis:
            values.append(i.retPGEVersion())
        for i in set(values):
            pge = self.ElementTree.SubElement(obj, 'PGEVersion')
            pge.text = i

    def valRangeTime(self, obj):
        """Function to add RangeDateTime

        :param obj: element to add RangeDateTime
        """
        values = []
        for i in self.parModis:
            values.append(i.retRangeTime())
        self._cicle_values(obj, self._checkvaldict(values))

    def valBound(self):
        """Function return the Bounding Box of mosaic"""
        boundary = self.parModis[0].retBoundary()
        for i in range(1, len(self.parModis)):
            bound = self.parModis[i].retBoundary()
            if bound['min_lat'] < boundary['min_lat']:
                boundary['min_lat'] = bound['min_lat']
            if bound['min_lon'] < boundary['min_lon']:
                boundary['min_lon'] = bound['min_lon']
            if bound['max_lat'] > boundary['max_lat']:
                boundary['max_lat'] = bound['max_lat']
            if bound['max_lon'] > boundary['max_lon']:
                boundary['max_lon'] = bound['max_lon']
        self.boundary = boundary

    def valMeasuredParameter(self, obj):
        """Function to add ParameterName

        :param obj: element to add ParameterName
        """
        valuesQAStats = []
        valuesQAFlags = []
        valuesParameter = []
        for i in self.parModis:
            for val in i.retMeasure().values():
                valuesQAStats.append(val['QAStats'])
                valuesQAFlags.append(val['QAFlags'])
                valuesParameter.append(val['ParameterName'])
        for i in set(valuesParameter):
            pn = self.ElementTree.SubElement(obj, 'ParameterName')
            pn.text = i

    def valInputPointer(self, obj):
        """Function to add InputPointer

        :param obj: element to add InputPointer
        """
        for i in self.parModis:
            for v in i.retInputGranule():
                ip = self.ElementTree.SubElement(obj, 'InputPointer')
                ip.text = v

    def valPlatform(self, obj):
        """Function to add Platform elements

        :param obj: element to add Platform elements
        """
        valuesSName = []
        valuesInstr = []
        valuesSensor = []
        for i in self.parModis:
            valuesSName.append(i.retPlatform()['PlatformShortName'])
            valuesInstr.append(i.retPlatform()['InstrumentShortName'])
            valuesSensor.append(i.retPlatform()['SensorShortName'])
        for i in set(valuesSName):
            pn = self.ElementTree.SubElement(obj, 'PlatformShortName')
            pn.text = i
        valInstr = self._checkval(valuesInstr)
        valSens = self._checkval(valuesSensor)

        if len(valInstr) != len(valSens):
            raise Exception('Something wrong reading XML files')
        else:
            for i in range(len(valInstr)):
                ins = self.ElementTree.SubElement(obj, 'Instrument')
                pn = self.ElementTree.SubElement(ins, 'InstrumentShortName')
                pn.text = valInstr[i]
                sens = self.ElementTree.SubElement(ins, 'Sensor')
                ps = self.ElementTree.SubElement(sens, 'SensorShortName')
                ps.text = valSens[i]

    def valInsertTime(self, obj):
        """Function to add InsertTime elements

        :param obj: element to add InsertTime elements
        """
        values = []
        for i in self.parModis:
            values.append(i.retInsertTime())
        for i in set(values):
            gur = self.ElementTree.SubElement(obj, 'InsertTime')
            gur.text = i

    def valLastUpdate(self, obj):
        """Function to add LastUpdate elements

        :param obj: element to add LastUpdate elements
        """
        values = []
        for i in self.parModis:
            values.append(i.retLastUpdate())
        for i in set(values):
            gur = self.ElementTree.SubElement(obj, 'LastUpdate')
            gur.text = i

    def valDataGranule(self, obj):
        """Function to add DataFileContainer

        :param obj: element to add DataFileContainer
        """
        values = []
        for i in self.parModis:
            values.append(i.retDataGranule())
        for i in values:
            dfc = self.ElementTree.SubElement(obj, 'ECSDataGranule')
            self._cicle_values(dfc, i)

    def valBrowseProduct(self, obj):
        """Function to add BrowseGranuleId

        :param obj: element to add BrowseGranuleId
        """
        values = []
        for i in self.parModis:
            values.append(i.retBrowseProduct())
        for i in set(values):
            dfc = self.ElementTree.SubElement(obj, 'BrowseGranuleId')
            dfc.text = i

    def valPSA(self, obj):
        """Function to add PSA

        :param obj: element to add PSA
        """
        values = []
        for i in self.parModis:
            values.append(i.retPSA())
        for k in sorted(values[0].keys()):
            psa = self.ElementTree.SubElement(obj, 'PSA')
            psaname = self.ElementTree.SubElement(psa, 'PSAName')
            psaname.text = k
            for s in values:
                psaval = self.ElementTree.SubElement(psa, 'PSAValue')
                psaval.text = s[k]

    def writexml(self, outputname, pretty=True):
        """Write a xml file for a mosaic

        :param str outputname: the name of output xml file
        :param bool pretty: write prettyfy output, by default true
        """

        # the root element
        granule = self.ElementTree.Element('GranuleMetaDataFile')
        # add DTDVersion
        self.valDTD(granule)
        # add DataCenterId
        self.valDataCenter(granule)
        # add GranuleURMetaData
        gurmd = self.ElementTree.SubElement(granule, 'GranuleURMetaData')
        # add GranuleUR
        self.valGranuleUR(gurmd)
        # add dbID
        self.valDbID(gurmd)
        # add InsertTime
        self.valInsertTime(gurmd)
        # add LastUpdate
        self.valLastUpdate(gurmd)
        # add CollectionMetaData
        cmd = self.ElementTree.SubElement(gurmd, 'CollectionMetaData')
        self.valCollectionMetaData(cmd)
        # add DataFiles
        df = self.ElementTree.SubElement(gurmd, 'DataFiles')
        self.valDataFiles(df)
        # add ECSDataGranule
        self.valDataGranule(gurmd)
        # add PGEVersionClass
        pgevc = self.ElementTree.SubElement(gurmd, 'PGEVersionClass')
        self.valPGEVersion(pgevc)
        # add RangeDateTime
        rdt = self.ElementTree.SubElement(gurmd, 'RangeDateTime')
        self.valRangeTime(rdt)
        # add SpatialDomainContainer
        sdc = self.ElementTree.SubElement(gurmd, 'SpatialDomainContainer')
        hsdc = self.ElementTree.SubElement(sdc, 'HorizontalSpatialDomainContainer')
        gp = self.ElementTree.SubElement(hsdc, 'GPolygon')
        bound = self.ElementTree.SubElement(gp, 'Boundary')
        self.valBound()
        self._addPoint(bound, 'min_lon', 'max_lat')
        self._addPoint(bound, 'max_lon', 'max_lat')
        self._addPoint(bound, 'min_lon', 'min_lat')
        self._addPoint(bound, 'max_lon', 'min_lat')
        # add MeasuredParameter
        mp = self.ElementTree.SubElement(gurmd, 'MeasuredParameter')
        mpc = self.ElementTree.SubElement(mp, 'MeasuredParameterContainer')
        self.valMeasuredParameter(mpc)
        # add Platform
        pl = self.ElementTree.SubElement(gurmd, 'Platform')
        self.valPlatform(pl)
        # add PSAs
        psas = self.ElementTree.SubElement(gurmd, 'PSAs')
        # add all PSA
        self.valPSA(psas)
        # add InputGranule and InputPointer
        ig = self.ElementTree.SubElement(gurmd, 'InputGranule')
        self.valInputPointer(ig)
        # add BrowseProduct
        bp = self.ElementTree.SubElement(gurmd, 'BrowseProduct')
        self.valBrowseProduct(bp)
        output = open(outputname, 'w')
        output.write('<?xml version="1.0" encoding="UTF-8"?>')
        output.write('<!DOCTYPE GranuleMetaDataFile SYSTEM "http://ecsinfo.'
                     'gsfc.nasa.gov/ECSInfo/ecsmetadata/dtds/DPL/ECS/'
                     'ScienceGranuleMetadata.dtd">')
        if pretty:
            import xml.dom.minidom as minidom
            reparsed = minidom.parseString(self.ElementTree.tostring(granule))
            output.write(reparsed.toprettyxml(indent="\t"))
        else:
            output.write(self.ElementTree.tostring(granule))
        output.close()
