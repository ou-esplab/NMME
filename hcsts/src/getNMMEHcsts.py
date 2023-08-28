#!/usr/bin/env python
# coding: utf-8

import os
import xarray as xr
import numpy as np
import pandas as pd
from nmme_utils import *

# Set the output path for the data
hcstPath='/data/esplab/shared/model/initialized/nmme/hindcast/'

# Get the model information
nmmemodels_list,_, _,_=initModels()

# Loop over all the Models
for imodel,model in enumerate(nmmemodels_list):
    
    # Get the model, group, variables, and levels from the dictionary     
    units=model['units']
    dates=model['hcst_dates']
    url_substr=model['url_substr']
    varnames=model['varnames']
    plevstrs=model['levstrs']
    model=model['model']
    
    for varname,plevstr,unit in zip(varnames,plevstrs,units):
        
        # Read Data
        
        baseURL=url_substr+varname+'/'
            
        inFname=baseURL+str(datetime.today().toordinal())+'/pop/dods' 
        print(inFname)
        
        # Read Data from IRIDL
        ds=decode_cf(xr.open_dataset(inFname,decode_times=False),'S')
        
        # Convert startdates to datetime64 and extract hindcast years
        ds['S']=ds['S'].astype("datetime64[ns]")
        ds=ds.sel(S=slice(dates[0],dates[1]))
                   
        # Loop over all start times    
        for ic in ds['S'].values:
    
            # Drop the Initial condition date
            ds_out=ds.sel(S=ic).squeeze(drop=True).drop_vars('S')
         
            # Convert coordinate names to something useful
            ds_out=ds_out.rename({'X':'lon','Y':'lat','L':'lead','M':'ens'})

            # Set global attributes
            ds_out=setattrs(ds_out,units)

            # Create output path if it does not exist
            outPath=hcstPath+varname+'/monthly/full/'+model
            if (not os.path.isdir(outPath)):
                os.makedirs(outPath)
          
            # Write Data to netCDF      
            outFile = outPath+'/'+varname+'_'+model+'_'+pd.to_datetime(ic).strftime('%Y%m')+'.nc'
            print(outFile)
            ds_out.to_netcdf(outFile,mode='w')                 
    

