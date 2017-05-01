#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  class to download modis data
#
#  (c) Copyright Luca Delucchi 2010-2016
#  Authors: Luca Delucchi
#  Email: luca dot delucchi at fmach dot it
#
##################################################################
#
#  The Modis class is licensed under the terms of GNU GPL 2
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

class product:
    """Definition of MODIS product with url and path in the ftp server
    """

    def __init__(self, value=None):
        # url to download products
        urlbase = 'http://e4ftl01.cr.usgs.gov'
        usrsnow = 'ftp://n5eil01u.ecs.nsidc.org'
        # values of lst product:
        lst_spec = '( 1 0 0 0 1 0 0 0 0 0 0 0 )'
        lst_specqa = '( 1 1 0 0 1 1 0 0 0 0 0 0 )'
        # suffix for the lst product (key is the lst map, value the QA)
        lst1km_suff = {'.LST_Day_1km': '.QC_Day',
                       '.LST_Night_1km': '.QC_Night'}
        lst6km_suff = {'.LST_Day_6km': '.QC_Day',
                       '.LST_Night_6km': '.QC_Night'}
        # color for lst product
        lst_color = ['celsius']
        # values of vi product:
        vi_spec = '( 1 1 0 0 0 0 0 0 0 0 0 0 )'
        vi_specqa = '( 1 1 1 0 0 0 0 0 0 0 0 1 )'
        vi_color = ['ndvi', 'evi']
        vi250m_suff = {'.250m_16_days_NDVI': '.250m_16_days_VI_Quality',
                       '.250m_16_days_EVI': '.250m_16_days_VI_Quality'}
        vi500m_suff = {'.500m_16_days_NDVI': '.500m_16_days_VI_Quality',
                       '.500m_16_days_EVI': '.500m_16_days_VI_Quality'}
        vi1km_suff = {'.1_km_16_days_NDVI': '.1_km_16_days_VI_Quality',
                      '.1_km_16_days_EVI': '.1_km_16_days_VI_Quality'}
        # values of snow product:
        snow1_spec = ('( 1 )')
        snow1_specqa = ('( 1 1 )')
        snow1_suff = {'.Snow_Cover_Daily_Tile': '.Snow_Spatial_QA'}
        snow8_spec = ('( 1 1 )')
        snow_color = ['gyr']  # TODO CREATE THE COLOR TABLE FOR MODIS_SNOW
        snow8_suff = {'.Maximum_Snow_Extent': None,
                      '.Eight_Day_Snow_Cover': None}
        lstL2_spec = 'LST; QC; Error_LST; Emis_31; Emis_32; View_angle; View_time'
        # values of surface reflectance product:
        surf_spec = '( 1 1 1 1 1 1 1 0 0 0 0 0 0 )'
        surf_specqa = '( 1 1 1 1 1 1 1 1 0 0 0 0 0 )'
        surf_suff = {'.sur_refl_b01': '.sur_refl_qc_500m', '.sur_refl_b02':
                     '.sur_refl_qc_500m', '.sur_refl_b03': '.sur_refl_qc_500m',
                     '.sur_refl_b04': '.sur_refl_qc_500m', '.sur_refl_b05':
                     '.sur_refl_qc_500m', '.sur_refl_b06': '.sur_refl_qc_500m',
                     '.sur_refl_b07': '.sur_refl_qc_500m'}
        # value for water product
        water_spec = ('( 1 )')
        water_specqa = ('( 1 1 )')
        water_suff = {'.water_mask': '.water_mask_QA'}

        # granularity
        daily = 1
        eight = 8
        sixteen = 16
        self.prod = value
        lst = {'lst_aqua_daily_1000': {'url': urlbase, 'folder': 'MOLA/',
                                       'prod': 'MYD11A1.005', 'days': daily,
                                       'spec': lst_spec, 'spec_qa': lst_specqa,
                                       'suff': lst1km_suff, 'res': 1000,
                                       'color': lst_color},
               'lst_terra_daily_1000': {'url': urlbase, 'folder': 'MOLT/',
                                        'prod': 'MOD11A1.005', 'days': daily,
                                        'spec': lst_spec, 'spec_qa': lst_specqa,
                                        'suff': lst1km_suff, 'res': 1000,
                                        'color': lst_color},
               'lst_terra_eight_1000': {'url': urlbase, 'folder': 'MOLT/',
                                        'prod': 'MOD11A2.005', 'days': eight,
                                        'spec': lst_spec, 'spec_qa': lst_specqa,
                                        'suff': lst1km_suff, 'res': 1000,
                                        'color': lst_color},
               'lst_aqua_eight_1000': {'url': urlbase, 'folder': 'MOLA/',
                                       'prod': 'MYD11A2.005', 'days': eight,
                                       'spec': lst_spec, 'spec_qa': lst_specqa,
                                       'suff': lst1km_suff, 'res': 1000,
                                       'color': lst_color},
               'lst_terra_daily_6000': {'url': urlbase, 'folder': 'MOLT/',
                                        'prod': 'MOD11B1.005', 'days': daily,
                                        'spec': lst_spec, 'spec_qa': lst_specqa,
                                        'suff': lst6km_suff, 'res': 6000,
                                        'color': lst_color},
               'lst_aqua_daily_6000': {'url': urlbase, 'folder': 'MOLA/',
                                       'prod': 'MYD11B1.005', 'days': daily,
                                       'spec': lst_spec, 'spec_qa': lst_specqa,
                                       'suff': lst6km_suff, 'res': 6000,
                                       'color': lst_color}
               }
        vi = {'ndvi_terra_sixteen_250': {'url': urlbase, 'folder': 'MOLT/',
                                         'prod': 'MOD13Q1.005',
                                         'spec': vi_spec, 'spec_qa': vi_specqa,
                                         'suff': vi250m_suff, 'res': 250,
                                         'color': vi_color, 'days': sixteen},
              'ndvi_aqua_sixteen_250': {'url': urlbase, 'folder': 'MOLA/',
                                        'prod': 'MYD13Q1.005',
                                        'spec': vi_spec, 'spec_qa': vi_specqa,
                                        'suff': vi250m_suff, 'res': 250,
                                        'color': vi_color, 'days': sixteen},
              'ndvi_terra_sixteen_500': {'url': urlbase, 'folder': 'MOLT/',
                                         'prod': 'MOD13A1.005',
                                         'spec': vi_spec, 'spec_qa': vi_specqa,
                                         'suff': vi1km_suff, 'res': 500,
                                         'color': vi_color, 'days': sixteen},
              'ndvi_aqua_sixteen_500': {'url': urlbase, 'folder': 'MOLA/',
                                        'prod': 'MYD13A1.005',
                                        'spec': vi_spec, 'spec_qa': vi_specqa,
                                        'suff': vi500m_suff, 'res': 500,
                                        'color': vi_color, 'days': sixteen},
              'ndvi_terra_sixteen_1000': {'url': urlbase, 'folder': 'MOLT/',
                                          'prod': 'MOD13A2.005',
                                          'spec': vi_spec, 'spec_qa': vi_specqa,
                                          'suff': vi500m_suff, 'res': 1000,
                                          'color': vi_color, 'days': sixteen},
              'ndvi_aqua_sixteen_1000': {'url': urlbase, 'folder': 'MOLA/',
                                         'prod': 'MYD13A2.005',
                                         'spec': vi_spec, 'spec_qa': vi_specqa,
                                         'suff': vi1km_suff, 'res': 1000,
                                         'color': vi_color, 'days': sixteen}
              }
        surf_refl = {'surfreflec_terra_eight_500': {'url': urlbase,
                                                    'folder': 'MOLT/',
                                                    'prod': 'MOD09A1.005',
                                                    'spec': surf_spec,
                                                    'spec_qa': surf_specqa,
                                                    'res': 500, 'days': eight,
                                                    'color': snow_color,
                                                    'suff': surf_suff},
                     'surfreflec_aqua_eight_500': {'url': urlbase,
                                                   'folder': 'MOLA/',
                                                   'prod': 'MYD09A1.005',
                                                   'spec': surf_spec,
                                                   'spec_qa': surf_specqa,
                                                   'res': 500, 'days': eight,
                                                   'color': snow_color,
                                                   'suff': surf_suff}
                     }
        snow = {'snow_terra_daily_500': {'url': usrsnow, 'folder': 'SAN/MOST/',
                                         'prod': 'MOD10A1.005',
                                         'spec': snow1_spec, 'days': daily,
                                         'spec_qa': snow1_specqa,
                                         'color': snow_color,
                                         'suff': snow1_suff, 'res': 500},
                'snow_aqua_daily_500': {'url': usrsnow,
                                        'folder': 'SAN/MOSA/',
                                        'prod': 'MYD10A1.005',
                                        'spec': snow1_spec, 'days': daily,
                                        'spec_qa': snow1_specqa,
                                        'color': snow_color,
                                        'suff': snow1_suff, 'res': 500},
                'snow_terra_eight_500': {'url': usrsnow,
                                         'folder': 'SAN/MOST/',
                                         'prod': 'MOD10A2.005',
                                         'spec': snow8_spec,
                                         'spec_qa': None, 'days': eight,
                                         'color': snow_color,
                                         'suff': snow8_suff, 'res': 500},
                'snow_aqua_eight_500': {'url': usrsnow,
                                        'folder': 'SAN/MOSA/',
                                        'prod': 'MYD10A2.005',
                                        'spec': snow8_spec,
                                        'spec_qa': None, 'days': eight,
                                        'color': snow_color,
                                        'suff': snow8_suff, 'res': 500}
                }
        water = {'water_terra_250': {'url': urlbase, 'folder': 'MOLT/',
                                     'prod': 'MOD44W.005', 'spec': water_spec,
                                     'spec_qa': water_specqa, 'res': 250,
                                     'suff': water_suff, 'days': daily,
                                     'color': snow_color}
                }
        self.products = {}
        self.products.update(lst)
        self.products.update(vi)
        self.products.update(snow)
        self.products.update(surf_refl)
        self.products.update(water)
        self.products_swath = {'lst_terra_daily': {'url': urlbase,
                                                   'folder': 'MOLT/',
                                                   'prod': 'MOD11_L2.005',
                                                   'spec': lstL2_spec},
                               'lst_aqua_daily': {'url': urlbase,
                                                  'folder': 'MOLA/',
                                                  'prod': 'MYD11_L2.005',
                                                  'spec': lstL2_spec}
                               }

    def returned(self):
        if self.products.keys().count(self.prod) == 1:
            return self.products[self.prod]
        elif self.products_swath.keys().count(self.prod) == 1:
            return self.products_swath[self.prod]
        else:
            raise Exception ("The code insert is not supported yet. Consider "
                          "to ask on the grass-dev mailing list for future "
                          "support")

    def fromcode(self, code):
        import string
        for k, v in self.products.iteritems():
            if string.find(v['prod'], code) != -1:
                return self.products[k]
        for k, v in self.products_swath.iteritems():
            if string.find(v['prod'], code) != -1:
                return self.products_swath[k]
        raise Exception("The code insert is not supported yet. Consider to "
                      "open a ticket in https://github.com/lucadelu/pyModis/issues")

    def color(self, code=None):
        if code:
            return self.fromcode(code)['color']
        else:
            return self.returned()['color']

    def suffix(self, code=None):
        if code:
            return self.fromcode(code)['suff']
        else:
            return self.returned()['suff']

    def __str__(self):
        prod = self.returned()
        string = "url: " + prod['url'] + ", folder: " + prod['folder']
        if prod.keys().count('spec') == 1:
            string += ", spectral subset: " + prod['spec']
        if prod.keys().count('spec_qa') == 1:
            string += ", spectral subset qa:" + prod['spec_qa']
        return string
