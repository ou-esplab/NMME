import xarray as xr
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta, date

import matplotlib.pyplot as plt
import proplot as pplt
#import hvplot.xarray  # noqa

import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import cartopy.feature as cfeature

xr.set_options(keep_attrs=True)  


def initModels():
        
    all_varnames=['tref','prec','sst']
    all_levstrs=['2m','sfc','sfc']
    all_units=['degC','mmday-1','degC']
    
    #all_varnames=['sst']
    #all_levstrs=['sfc']
    #all_units=['degC']


    cfsv2_dict={'model':'NCEP-CFSv2','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'climo_range':'mc9120','plot_loc':0}
    cancm_dict={'model':'CanCM4i-IC3','group':'CanSIPS-IC3','varnames': all_varnames, 'levstrs': all_levstrs,'climo_range':'mc9120','plot_loc':1}
    gem_dict={'model':'GEM5-NEMO','group':'CanSIPS-IC3','varnames': all_varnames, 'levstrs': all_levstrs,'climo_range':'mc9120','plot_loc':2}
    gfdl_dict={'model':'GFDL-SPEAR','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'climo_range':'mc9120','plot_loc':3}
    ccsm_dict={'model':'COLA-RSMAS-CCSM4','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'climo_range':'mc9120','plot_loc':4}
    geos_dict={'model':'NASA-GEOSS2S','group':'','varnames': all_varnames, 'levstrs': all_levstrs,'climo_range':'mc8210','plot_loc':5}
 
    models_list=[cfsv2_dict,geos_dict,cancm_dict,gem_dict,gfdl_dict,ccsm_dict]
    
    return models_list,all_varnames, all_levstrs, all_units

def initPlotParams():

    # Dictionary defining parameters for plottting variables
   
    clevs_tas=[-4,-3,-2,-1,-0.5,-0.25,0.25,0.5,1,2,3,4]
    #clevs_pr=[-100,-50,-25,-10,-5,-2,2,5,10,25,50,100]
    clevs_pr=[-10,-6,-4,-2,-1,-0.5,-0.25,0.25,0.5,1,2,4,6,10]
    clevs_zg=[-50,-45,-40,-35,-30,-25,-20,-15,15,20,25,30,35,40,45,50]
    clevs_sst=[-4,-3,-2,-1,-0.5,-0.25,0.25,0.5,1,2,3,4]
    
    tas_dict={'name':'tref','plev':'2m','label':'2m Temperature','outname':'2mTemp',
              'clevs':clevs_tas,'cmap':'ColdHot','units':'${^oC}$',
              'regions':['Global','NorthAmerica'],'scale_factor':1}
    pr_dict={'name':'prec','plev':'sfc','label':'Precipitation Rate','outname':'Precip',
              'clevs':clevs_pr,'cmap':'DryWet','units':'mm/day',
              'regions':['Global','NorthAmerica'],'scale_factor':1}
    zg_dict={'name':'zg','plev':'500',
             'label':'500hPa Geopotential Height',
             'outname':'500hPaGeopotentialHeight',
             'clevs':clevs_zg,'cmap':'NegPos','units':'m',
             'regions':['NorthernHemisphere'],'scale_factor':1}
    sst_dict={'name':'sst','plev':'sfc',
             'label':'Sea Surface Temperature',
             'outname':'SST',
             'clevs':clevs_sst,'cmap':'NegPos','units':'${^oC}$',
             'regions':['Global'],'scale_factor':1}

    var_params_dict=[tas_dict,pr_dict,sst_dict]
     
    # Dictionary defining parameters for plotting different regions
    
    global_dict={'name':'Global','lons':(0,360),'lats':(-90,90),'clon':0,'mproj':'robin',
                'state_colors':'gray5'}
    na_dict={'name':'NorthAmerica','lons':(190,305),'lats':(15,75),'clon':247.5,'mproj':'pcarree',
            'state_colors':'k'}
    nh_dict={'name':'NorthernHemisphere','lons':(-270,90),'lats':(30,90),'clon':247.5,'mproj':'npstere',
            'state_colors':'gray5','state_colors':'gray5'}
    
    reg_params_dict=[global_dict,na_dict,nh_dict]
    
    return var_params_dict, reg_params_dict

def decode_cf(ds, time_var):
    """Decodes time dimension to CFTime standards.""" 
    if ds[time_var].attrs["calendar"] == "360":
          ds[time_var].attrs["calendar"] = "360_day"
    ds = xr.decode_cf(ds, decode_times=True)
    ds[time_var].attrs["calendar"] = "365_day"

    return ds

def getDataViaIngrid(ds_meta,baseURL):

    # Construct the pressure level information for IngridURL if it exists
    #ingrid_pvalue=''
    #if ('P' in list(ds_meta.coords)):
    #    print(ds_meta['P'].values)
    #    ingrid_pvalue='P/%28'+str(int(ds_meta['P'].values))+'%29VALUES'
            
    # Construct the Date Information for the IngridURL
    day='%20'+ds_meta['S'].dt.strftime('%d').values 
    month='%20'+ds_meta['S'].dt.strftime('%b').values
    year='%20'+ds_meta['S'].dt.strftime('%Y').values
    hrs='%20'+ds_meta['S'].dt.strftime('%H').values+'00'
    ingrid_svalue='S/%28'+hrs+day+month+year+'%29VALUES/[M]average'
    
    # Close the full dataset used to get the metadata
    ds_meta.close()
    
    # Construct the Ingrid URL
    ingridURL=baseURL+'/'+ingrid_svalue+'/dods/'
    
    print(ingridURL)
    
    # Open the subsetted version of the dataset using the Ingrid URL
    ds=xr.open_dataset(ingridURL,decode_times=False)
    ds = decode_cf(ds, 'S') #.compute()
    ds['S']=ds['S'].astype("datetime64[ns]")
    
    return ds

def getClimDataViaIngrid(hcstURL,fcstURL):
    
        
    # Open the dataset using the Ingrid URL
    dshcst=xr.open_dataset(hcstURL+'/[M]average/dods',decode_times=False,chunks={'S':'500MB'})
    dshcst = decode_cf(dshcst, 'S')
    dshcst['S']=dshcst['S'].astype("datetime64[ns]")
    
    if (hcstURL==fcstURL):
        dsfcst=dshcst
    else:
        print(fcstURL+'/[M]average/dods')
        dsfcst=xr.open_dataset(fcstURL+'/[M]average/dods',decode_times=False)
        dsfcst = decode_cf(dsfcst, 'S')
        dsfcst['S']=dsfcst['S'].astype("datetime64[ns]")
        
    # This is for CFSv2 only.  Need to add model and if statement
    tmp1=dshcst.sel(S=slice('1991-01-01','2011-02-28'))
    tmp2=dsfcst.sel(S=slice('2011-03-01','2020-12-31'))
    ds=xr.concat([tmp1,tmp2],'S')
    
    #if ('Z' in ds.dims):
    #    ds=ds.squeeze(dim='Z',drop=True)
    
    return ds,dshcst,dsfcst

def nmmePlot(ds,path):

    # Get the plotting parameters for variables and regions
    var_params_dict,reg_params_dict=initPlotParams()

    # Loop over variables
    for var_params in var_params_dict:
        print(var_params['name']) 
        
        # Loop over regions to be plotting for this variable
        for regs in var_params['regions']:
        
            # Find dictionary for this region
            reg_dict=next(item for item in reg_params_dict if item['name'] == regs)
        
            # Output figure partial name
            figname=path+var_params['outname']+reg_dict['name']

            
            # Call plottting with variable and region parameters 
            makeWebImages(ds,var_params['name'],var_params['units'],
                          var_params['label'],var_params['clevs'],var_params['cmap'],
                          var_params['scale_factor'],
                          reg_dict['lons'],reg_dict['lats'],reg_dict['clon'],
                          reg_dict['mproj'],reg_dict['state_colors'],figname)
            

def makeWebImages(ds_fcst,v,unit,vl,clevs,cmap,sf,lonreg,latreg,clon,mproj,statescolor,figname):
   
    fcstdate=pd.to_datetime(ds_fcst['S'].values).strftime('%Y%m')
    
    # Proplot makes high res pics so need to reduce for web pics
    pplt.rc.savefigdpi = 100
    
    # Get SubX Models List for plot locations
    models_list,_,_,_=initModels()   

    # Loop over all months -- one figure per month
    for ilead,lead in enumerate(ds_fcst['lead'].values):
    
        # Set the plot grid and create the subplot container
        grid = [[1, 2, 3],
                [4, 5, 6],
                [7, 0, 0]]
        f, axs = pplt.subplots(grid,
                               proj=mproj,proj_kw={'lon_0': clon},
                               width=11,height=8.5)
     
        fcstmonth_str=(ds_fcst['S'][-1].values+pd.DateOffset(months=ilead)).strftime('%b')        
        suptitle='NMME Forecast '+fcstmonth_str+' '+vl+' Anomalies ('+unit+'): '+str(lead)+' Months Lead'
    
        # Loop over all models
        sub_nens=0
        for imodel,model in enumerate(ds_fcst['model'].values):
            
            if (model=='MME'):
                iplot=6
            else:
                model_dict=next(item for item in models_list if item['model'] == model)
                iplot=model_dict['plot_loc']
                            
            # Select the model
            ds=ds_fcst.sel(model=model).dropna(dim='lead',how='all').squeeze()
                
            if ('lead' in ds.dims):
                if (ds['lead'].values.max() >= ilead): # Logic to handle models that do not have 12 months of lead
                    ds=ds.sel(lead=ilead)
                
                    if (model != 'MME'):
                        sub_nens=sub_nens+ds['nens'].values
                
                    # Get the startdate for this model
                    startdate=ds['S'].values
    
                    # Define titles for individual subplot panels
                    nens_str=str(ds['nens'].values.astype(int))
                
                    if (model=='MME'):
                        title=model+' (IC: '+(pd.to_datetime(ds_fcst['S'][-1].values)).strftime('%Y%m')+'; '+str(int(sub_nens))+' Ens )'
                    else:
                        title=model+' (IC: '+(pd.to_datetime(ds_fcst['S'][-1].values)).strftime('%Y%m')+'; '+nens_str+' Ens )'
     
                    # Define normalization for colorbar centering
                    norm = pplt.Norm('diverging', vcenter=0)
           
                    # Contour plot for each panel
           
                    if (mproj=='robin'):
                        m=axs[iplot].contourf(ds['lon'],ds['lat'],ds[v].values*sf,levels=clevs,
                                              cmap=cmap,extend='both',norm=norm)
                        axs[iplot].format(coast=True,grid=False,borders=True,
                                          borderscolor='gray5',title=title,suptitle=suptitle) 
                
                        # Add US state borders    
                        axs[iplot].add_feature(cfeature.STATES,edgecolor=statescolor)
                    else:
                        m=axs[iplot].contourf(ds['lon'],ds['lat'],ds[v].values*sf,
                                              levels=clevs,cmap=cmap,extend='both',norm=norm)
                        axs[iplot].format(coast=True,lonlim=lonreg,latlim=latreg,grid=False,borders=True,
                                          borderscolor='gray5',title=title,suptitle=suptitle) 
                        # Add US state borders    
                        axs[iplot].add_feature(cfeature.STATES,edgecolor=statescolor)

        # Add colorbar
        f.colorbar(m,loc='b',label=unit, length=0.7) 
    
        # Save Figure
        print('Writing Figures to: '+figname+'Month'+str(ilead)+'.png')
        f.save(figname+'Month'+str(ilead)+'.png')
        
def setattrs(ds,fcstdate,units):
    ds.attrs['units']=units
    ds.attrs['fcst_date'] = str(fcstdate)
    ds.attrs['title'] = "NMME Forecast Anomalies" 
    ds.attrs['long_title'] = "NMME Forecast Anomalies"
    ds.attrs['comments'] = "NMME https://www.cpc.ncep.noaa.gov/products/NMME/" 
    ds.attrs['institution'] = "[IRI, U. Miami]" 
    ds.attrs['source'] = "NMME IRIDL: https://iridl.ldeo.columbia.edu/SOURCES/.Models/.NMME/"
    ds.attrs['CreationDate'] = date.today().strftime('%Y-%m-%d')
    ds.attrs['CreatedBy'] = os.environ['USER']+' '+'U. Oklahoma, School of Meteorology'
    ds.attrs['Source'] = os.path.basename(__file__)
    ds.attrs['Reference'] = "DOI: 10.1175/BAMS-D-20-0327.1; 10.1029/2020GL087408; 10.1175/BAMS-D-12-00050.1 "

    return ds
        
def nmmeWrite(ds_fcst,fcstdate):
    
    print("WRITING DATA")
    
    # Get a dictionary of Models 
    models_list,all_varnames,all_plevstrs,all_units=initModels()
    
    # Loop over all variables to write out
    for v,p,u in zip(all_varnames,all_plevstrs,all_units):

        ds_model_list=[]
    
        # Loop over the Models
        for imodel,nmme_model in enumerate(models_list):
            
            # Get the model, group, variables, and levels from the dictionary 
            varnames=nmme_model['varnames']
            plevstrs=nmme_model['levstrs']
            model=nmme_model['model']
            group=nmme_model['group']

            if (model in ds_fcst['model'].values):
                print(model,'is here')
                
            # Check if this model has this variable and append
            if (v in varnames):
                
                # Individual Models
                ds=ds_fcst[v].sel(model=model).to_dataset(name=model).squeeze(drop=True)
                ds[model].attrs['long_name']=model+' '+fcstdate
                ds[model].attrs['units']=u
                ds_model_list.append(ds.reset_coords(drop=True))
                
            
                # MME
                ds=ds_fcst[v].sel(model='MME').to_dataset(name='MME').squeeze(drop=True)
                ds['MME'].attrs['long_name']='MME'+' '+fcstdate
                ds['MME'].attrs['units']=u
                ds_model_list.append(ds.reset_coords(drop=True))
        
        # Output file -- probably should pass basepath in as optional argument
        ofname_mon='/data/esplab/shared/model/initialized/nmme/forecast/monthly/'+fcstdate+'/data/NMME_fcst_'+fcstdate+'.anom.monthly.'+v+'_'+p+'.emean.nc'
        ofname_seas='/data/esplab/shared/model/initialized/nmme/forecast/seasonal/'+fcstdate+'/data/NMME_fcst_'+fcstdate+'.anom.seas.'+v+'_'+p+'.emean.nc'
        print(ofname_seas)
        
        
        # Check if list of models for this variable has data
        if (ds_model_list):
        
            # Put all the models together for this variable        
            ds_models=xr.merge(ds_model_list,compat='override')
            
            # Set Global attributes
            ds_models=setattrs(ds_models,fcstdate,u)
            
            # Set time dimension and units for grads readable
            ds_models['lead']=ds_fcst['valid'].values
            ds_models=ds_models.rename({'lead':'time'})
            ds_models['time'].attrs['standard_name']='time'
            ds_models['time'].attrs['long_name']='Forecast Valid Month'
    
            # Shift longitudes
            ds_models=ds_models.assign_coords(lon=(((ds_models['lon'] +180) % 360))-180)
            ds_models=ds_models.sortby(ds_models['lon'])

            # Write out monthly file
            ds_models.to_netcdf(ofname_mon)
            
            # Write out seasonal file
            ds_models=ds_models.groupby('time.season').mean()
            ds_models['season'].attrs['long_name']='Forecast Valid Season'
            ds_models.to_netcdf(ofname_seas)
            
        else: # list is empty, variable does not exist
            print('This variable '+v+' does not exist in any models. File '+ofname_mon+' not written.')
