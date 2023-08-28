import xarray as xr
import numpy as np
import pandas as pd

import os
from datetime import datetime, timedelta, date


xr.set_options(keep_attrs=True)  


def initModels():

    baseurl='https://iridl.ldeo.columbia.edu/SOURCES/.Models/.NMME/'
    
    #all_varnames=['tref'] #,'prec','sst']
    #all_levstrs=['2m'] #,'sfc','sfc']
    #all_units=['degC'] #,'mmday-1','degC']

    all_varnames=['sst']
    all_levstrs=['sfc']
    all_units=['degC']
    
    ### Current Real-time Models

    cfsv2_dict={'model':'NCEP-CFSv2','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
                'hcst_dates':['1982-01-01','2010-12-01'],'fcst_dates':['2011-03-01',datetime.today().strftime('%Y-%m')+'-01'],
               'url_substr':baseurl+'NCEP-CFSv2/.HINDCAST/.PENTAD_SAMPLES/.MONTHLY/.'}

    cancm_dict={'model':'CanCM4i-IC3','group':'CanSIPS-IC3','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
                'hcst_dates':['1982-01-01','2020-11-01'],'fcst_dates':['2020-12-01',datetime.today().strftime('%Y-%m')+'-01'],
                'url_substr':baseurl+'.CanSIPS-IC3/.CanCM4i-IC3/.HINDCAST/.MONTHLY/.'}

    gem_dict={'model':'GEM5-NEMO','group':'CanSIPS-IC3','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
              'hcst_dates':['1982-01-01','2020-11-01'],'fcst_dates':['2020-12-01',datetime.today().strftime('%Y-%m')+'-01'],
              'url_substr':baseurl+'.CanSIPS-IC3/.GEM5-NEMO/.HINDCAST/.MONTHLY/.'}

    gfdl_dict={'model':'GFDL-SPEAR','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
               'hcst_dates':['1991-01-01','2020-12-01'],'fcst_dates':['2021-01-01',datetime.today().strftime('%Y-%m')+'-01'],
               'url_substr':baseurl+'GFDL-SPEAR/.HINDCAST/.MONTHLY/.'}

    ccsm_dict={'model':'COLA-RSMAS-CCSM4','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
               'hcst_dates':['1982-01-01','2010-01-01'],'fcst_dates':['2014-05-01',datetime.today().strftime('%Y-%m')+'-01'],
               'url_substr':baseurl+'COLA-RSMAS-CCSM4/.MONTHLY/.'}

    geos_dict={'model':'NASA-GEOSS2S','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
              'hcst_dates':['1981-01-01','2010-12-01'],'fcst_dates':['2017-02-01',datetime.today().strftime('%Y-%m')+'-01'],
               'url_substr':baseurl+'NASA-GEOSS2S/.HINDCAST/.MONTHLY/.'}
     
    ### No longer Real-time
    gemv2_dict={'model':'GEM-NEMO','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
                'hcst_dates':['1982-01-01','2020-12-01'],'fcst_dates':['2020-12-01','2021-12-01'],
                'url_substr':baseurl+'GEM-NEMO/.HINDCAST/.MONTHLY/.'}
    cancm41_dict={'model':'CanCM4i','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
                  'hcst_dates':['1982-01-01','2010-12-01'],'fcst_dates':['2019-08-01','2021-12-01'],
                  'url_substr':baseurl+'CanCM4i/.HINDCAST/.MONTHLY/.'}
    cmc2_dict={'model':'CMC2-CanCM4','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
               'hcst_dates':['1981-01-01','2010-12-01'],'fcst_dates':['2010-12-01','2019-12-01'],
               'url_substr':baseurl+'CMC2-CanCM4/.HINDCAST/.MONTHLY/.'}
    cmc1_dict={'model':'CMC1-CanCM3','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'units':all_units,
               'hcst_dates':['1981-01-01','2010-12-01'],'fcst_dates':['2012-08-01','2019-12-01'],
               'url_substr':baseurl+'CMC1-CanCM3/.HINDCAST/.MONTHLY/.'}
    ccsm3_dict={'model':'COLA-RSMAS-CCSM3','group':'','varnames': all_varnames,'levstrs': all_levstrs,'units':all_units,
                'hcst_dates':['1982-01-01','2010-01-01'],'fcst_dates':['2011-08-01','2014-12-01'],
                'url_substr':baseurl+'COLA-RSMAS-CCSM4/.MONTHLY/.'}
   
    
    models_list=[cfsv2_dict,geos_dict,cancm_dict,gem_dict,gfdl_dict,ccsm_dict,gemv2_dict,cancm41_dict,cmc2_dict,cmc1_dict,ccsm3_dict]
    
    return models_list,all_varnames, all_levstrs, all_units


def decode_cf(ds, time_var):
    """Decodes time dimension to CFTime standards.""" 
    if ds[time_var].attrs["calendar"] == "360":
          ds[time_var].attrs["calendar"] = "360_day"
    ds = xr.decode_cf(ds, decode_times=True)
    ds[time_var].attrs["calendar"] = "365_day"

    return ds



def setattrs(ds,units):
    ds.attrs['units']=units
    ds.attrs['title'] = "NMME Data" 
    ds.attrs['long_title'] = "NMME Data"
    ds.attrs['comments'] = "NMME https://www.cpc.ncep.noaa.gov/products/NMME/" 
    ds.attrs['institution'] = "[IRI, U. Miami]" 
    ds.attrs['source'] = "NMME IRIDL: https://iridl.ldeo.columbia.edu/SOURCES/.Models/.NMME/"
    ds.attrs['CreationDate'] = date.today().strftime('%Y-%m-%d')
    ds.attrs['CreatedBy'] = os.environ['USER']+' '+'U. Oklahoma, School of Meteorology'
    ds.attrs['Source'] = os.path.basename(__file__)
    ds.attrs['Reference'] = "DOI: 10.1175/BAMS-D-20-0327.1; 10.1029/2020GL087408; 10.1175/BAMS-D-12-00050.1 "

    return ds


