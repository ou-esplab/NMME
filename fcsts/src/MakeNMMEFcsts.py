#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xarray as xr
import numpy as np
import pandas as pd

import os.path
from datetime import datetime, timedelta, date
import time

import matplotlib.pyplot as plt
import proplot as pplt

import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature

from nmme_utils import *


# In[2]:


# Eliminate Warnings
import warnings
warnings.filterwarnings("ignore")


# In[3]:


# Set xarray to keep attributes
xr.set_options(keep_attrs=True)  


# ## Models and Forecast Settings

# In[4]:


models_list,vnames,levstrs,units=initModels()
model_labels=[item['model'] for item in models_list]


# ## File Paths

# In[5]:


url='http://iridl.ldeo.columbia.edu/SOURCES/.Models/.NMME'
datatype='FORECAST'
climPath='/mcs/scratch/kpegion/nmme/climatology/monthly/1991-2020/'


# ### Make a nmme_fcst `xarray.Dataset` containing all models + MME for months 1-12

# In[6]:


print('PROCESSING FCSTS FOR: ')

# Loop over all the Models
ds_models_list=[]
for imodel,nmme_model in enumerate(models_list):
    
    # Get the model, group, variables, and levels from the dictionary 
    varnames=nmme_model['varnames']
    levstrs=nmme_model['levstrs']
    model=nmme_model['model']
    group=nmme_model['group']
    
    print('===> ',model)
    
    # Loop over variables for this model
    ds_anoms_list=[]
    for varname,levstr in zip(varnames,levstrs):
        
        print(varname,levstr)
        
        # Construct URLs to read data; some details to do this are model specific
        if group == "":
            if (model=='COLA-RSMAS-CCSM4'):
                baseURL=url+'/.'+model+'/.MONTHLY'+'/.'+varname 
            elif (model=='NCEP-CFSv2'):
                baseURL=url+'/.'+model+'/.'+datatype+'/.EARLY_MONTH_SAMPLES/.MONTHLY/.'+varname 
            else:
                baseURL=url+'/.'+model+'/.'+datatype+'/.MONTHLY'+'/.'+varname
        else:
            baseURL=url+'/.'+group+'/.'+model+'/.'+datatype+'/.MONTHLY'+'/.'+varname
        inFname=baseURL+'/2000/pop/dods'  
        
        # Read data
        ds=xr.open_dataset(inFname,decode_times=False,chunks={'S':'500MB'})
        
        # Decode Times & convert to datetime
        ds = decode_cf(ds, 'S')
        ds['S']=ds['S'].astype("datetime64[ns]")
        
        # Store number of ensemble members
        nens=len(ds['M'])

        # Select the most recent start date in fcst
        ds=ds.sel(S=ds['S'][-1])
        print(ds['S'][-1]
        #ds=ds.sel(S='2023-05-01')
            
        # Get Latest Forecast Data Using Ingrid on IRIDL
        ds=getDataViaIngrid(ds,baseURL)
                
        # Create model as coordinates to keep track of which models are being used
        ds=ds.assign_coords({'model':model})    
                        
        # Convert L (lead) to integer
        ds['L'] = (ds['L'] - 0.5).astype('int')
             
        # Rename coordinates & add attributes
        ds=ds.rename({'X':'lon','Y':'lat','L':'lead'})  
        ds=ds.assign_coords({'nens':nens,'model':model})
        ds['lead'].attrs = {'units': 'months'}
        ds['lon'].attrs['units']='degrees_east'
        ds['lat'].attrs['units']='degrees_north'
        if ('Z' in ds.dims):
            ds=ds.squeeze(dim='Z',drop=True)
        
        # Get climo 1991-2020
        climo_url=climPath+model+'.'+varname+'_'+levstr+'.clim.1991-2020.nc'
        ds_clim=xr.open_dataset(climo_url)
        
        # Make anomalies
        ds_anoms=ds-ds_clim.sel(month=int(ds['S.month'].values))
        
        # Convert lead to datetime
        tmp_list=[]
        for l in ds_anoms['lead'].values:
            tmp_list.append(ds_anoms['S'].values[0]+pd.DateOffset(months=l))
        ds_anoms['valid']=tmp_list
        
        # Append anoms to list
        ds_anoms_list.append(ds_anoms)
        
    # Make list with all variables for this model and append to models list 
    ds_models_list.append(xr.merge(ds_anoms_list,compat='override'))

# Combine into dataset with all variables and all models
ds_models=xr.combine_nested(ds_models_list,concat_dim='model',compat='override',coords=['nens']).persist()

# Make MME
ds_mme=ds_models.mean(dim='model')
ds_mme=ds_mme.assign_coords({'model':'MME',
                             'nens':ds_models['nens'].sum()})

# Combine dataset for individual models and MME into a single xarray.Dataset 
ds_fcst=xr.concat([ds_models,ds_mme],dim='model').compute()

# Make Plots
fcstdate=ds['S'][-1].dt.strftime('%Y%m').values
figpath='/mcs/scratch/kpegion/nmme/forecast/monthly/'+fcstdate+'/images/'
nmmePlot(ds_fcst,figpath)

# Write Data
nmmeWrite(ds_fcst,fcstdate)


# In[7]:


ds

