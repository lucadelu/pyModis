#!/usr/bin/env python
#  class to convert/process modis data using gdal
#
#  Some code is coming from GDAL/OGR Test Suite
#  Copyright (c) 2008, Andrey Kiselev <dron16@ak4719.spb.edu>
#  Copyright (c) 2008-2014, Even Rouault <even dot rouault at mines-paris dot org>
#  http://trac.osgeo.org/gdal/browser/trunk/autotest/alg/warp.py#L782
#
#  (c) Copyright Luca Delucchi 2014
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

try:
    import osgeo.gdal as gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        raise('Python GDAL library not found, please install python-gdal')

try:
    import osgeo.osr as osr
except ImportError:
    try:
        import osr
    except ImportError:
        raise('Python GDAL library not found, please install python-gdal')


RESAM_GDAL = ['AVERAGE', 'BILINEAR', 'CUBIC', 'CUBIC_SPLINE', 'LANCZOS',
              'MODE', 'NEAREST_NEIGHBOR']
sinusoidal_wkt = 'PROJCS["Sinusoidal_Sanson_Flamsteed",GEOGCS["GCS_Unknown",' \
                 'DATUM["D_unknown",SPHEROID["Unknown",6371007.181,"inf"]],' \
                 'PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]' \
                 ',PROJECTION["Sinusoidal"],PARAMETER["central_meridian",0],' \
                 'PARAMETER["false_easting",0],PARAMETER["false_northing",0]' \
                 ',UNIT["Meter",1]]'


def getResampling(r):
    if r == 'AVERAGE':
        return gdal.GRA_Average
    elif r == 'BILINEAR' or r == 'BICUBIC':
        return gdal.GRA_Bilinear
    elif r == 'LANCZOS':
        return gdal.GRA_Lanczos
    elif r == 'MODE':
        return gdal.GRA_Mode
    elif r == 'NEAREST_NEIGHBOR':
        return gdal.GRA_NearestNeighbour
    elif r == 'CUBIC_CONVOLUTION' or r == 'CUBIC':
        return gdal.GRA_Cubic
    elif r == 'CUBIC_SPLINE':
        return gdal.GRA_CubicSpline


class convertModisGDAL:
    """A class to convert modis data from hdf to GDAL formats using GDAL
    """
    def __init__(self, hdfname, prefix, subset, res, outformat="GTiff",
                 epsg=None, wkt=None, resampl='NEAREST_NEIGHBOR'):
        # Open source dataset
        self.in_name = hdfname
        self.src_ds = gdal.Open(self.in_name)
        self.layers = self.src_ds.GetSubDatasets()
        self.output_pref = prefix
        self.resolution = res
        if epsg:
            self.dst_srs = osr.SpatialReference()
            self.dst_srs.ImportFromEPSG(int(epsg))
            self.dst_wkt = self.dst_srs.ExportToWkt()
        elif wkt:
            try:
                f = open(wkt)
                self.dst_wkt = f.read()
                f.close()
            except:
                self.dst_wkt = wkt
        else:
            raise IOError('You have to set one of the following option: ' \
                          '"epsg", "wkt"')
        # error threshold the same value as gdalwarp
        self.error_threshold = 0.125
        self.resampling = getResampling(resampl)
        self.subset = subset.replace('(', '').replace(')', '').strip()
        self.driver = gdal.GetDriverByName(outformat)
        if self.driver is None:
            raise IOError('Format driver %s not found, pick a supported ' \
                          'driver.' % outformat)

    def _boundingBox(self, src):
        src_gtrn = src.GetGeoTransform(can_return_null=True)

        src_bbox_cells = (
            (0., 0.),
            (0, src.RasterYSize),
            (src.RasterXSize, 0),
            (src.RasterXSize, src.RasterYSize),
          )

        geo_pts_x = []
        geo_pts_y = []
        for x, y in src_bbox_cells:
            x2 = src_gtrn[0] + src_gtrn[1] * x + src_gtrn[2] * y
            y2 = src_gtrn[3] + src_gtrn[4] * x + src_gtrn[5] * y
            geo_pts_x.append(x2)
            geo_pts_y.append(y2)
        return ((min(geo_pts_x), min(geo_pts_y)), (max(geo_pts_x),
                 max(geo_pts_y)))

    def _calculateRes(self, mi, ma, res):
        return int(round((ma - mi) / res))

    def _createWarped(self):
        """Create a warped VRT file to fetch default values for target raster
        dimensions and geotransform"""
        src = gdal.Open(self.layers[0][0])
        tmp_ds = gdal.AutoCreateWarpedVRT(src, sinusoidal_wkt,
                                          self.dst_wkt, self.resampling,
                                          self.error_threshold)

        if not self.resolution:
            self.dst_xsize = tmp_ds.RasterXSize
            self.dst_ysize = tmp_ds.RasterYSize
            self.dst_gt = tmp_ds.GetGeoTransform()
        else:
            bbox = self._boundingBox(tmp_ds)
            self.dst_xsize = self._calculateRes(bbox[0][0], bbox[1][0],
                                                self.resolution)
            self.dst_ysize = self._calculateRes(bbox[0][1], bbox[1][1],
                                                self.resolution)
            self.dst_gt = [bbox[0][0], self.resolution, 0.0, bbox[1][1], 0.0,
                           -self.resolution]
        tmp_ds = None
        src = None
        return 0

    def _progressCallback(self, pct, message, user_data):
        #print(pct)
        return 1  # 1 to continue, 0 to stop

    def _reprojectOne(self, l):
        l_src_ds = gdal.Open(l[0])
        meta = l_src_ds.GetMetadata()
        band = l_src_ds.GetRasterBand(1)
        fill_value = meta['_FillValue']
        datatype = band.DataType
        l_name = l[1].split(' ')[1]
        out_name = "{pref}_{lay}.tif".format(pref=self.output_pref, lay=l_name)
        try:
            dst_ds = self.driver.Create(out_name, self.dst_xsize,
                                        self.dst_ysize, 1, datatype)
        except:
            raise IOError('Not possibile to create dataset %s' % out_name)
        dst_ds.SetProjection(self.dst_wkt)
        dst_ds.SetGeoTransform(self.dst_gt)

        cbk = self._progressCallback
        # value for last parameter of above self._progressCallback
        cbk_user_data = None
        try:
            gdal.ReprojectImage(l_src_ds, dst_ds, sinusoidal_wkt, self.dst_wkt,
                                self.resampling, 0, self.error_threshold, cbk,
                                cbk_user_data)
            print "Layer %s reprojected" % l[0]
        except:
            raise IOError('Not possibile to reproject dataset %s' % l[0])
        dst_ds.SetMetadata(meta)
        dst_ds = None
        l_src_ds = None
        return 0

    def run(self):
        """Reproject all the choosen layer"""
        self._createWarped()
        n = 0
        for i in self.subset:
            if i == '1':
                self._reprojectOne(self.layers[n])
            n = n + 1
        print "All layer for dataset %s reprojected" % self.in_name
