# -*- coding: utf-8 -*-
"""
Created on Thu May 04 14:20:12 2017

@author: Crosby
"""

from datetime import datetime
from pytz import timezone
import os
import urllib2

# Function returns current offset to PST/PDT (8 or 7 hours)
def get_gmt_offset():
    pdt = timezone('US/Pacific')
    nowUTC = datetime.utcnow()
    nowPDT = datetime.now(pdt)
    nowUTCCorrected = datetime(int(nowUTC.year), int(nowUTC.month), int(nowUTC.day), 
                               int(nowUTC.hour), int(nowUTC.minute), 
                                int(nowUTC.second))
    nowPDTCorrected = datetime(int(nowPDT.year), int(nowPDT.month), 
                               int(nowPDT.day), int(nowPDT.hour), int(nowPDT.minute), 
                                int(nowPDT.second))
    diff_time = nowUTCCorrected - nowPDTCorrected
    diff_hour = int(round(diff_time.seconds/3600))
    return diff_hour

# Function downloads grib file
#   Used by get_hrdps()
def download_grib(gribPrefixP, url, dateString, hour, loc_output):
    # Set name and creat URL
    grib_name = '%s%s00_P%03d-00.grib2' % (gribPrefixP, dateString, hour)
    grib_url = '%s/00/%03d/%s' % (url, hour, grib_name)

    # Download file to folder specified, throw error if not found
    outfile = '%s/%s' % (loc_output,grib_name)
    try:
        webpage = urllib2.urlopen(grib_url)
        with open(outfile,'w') as fid:
            temp = webpage.read()
            fid.write(temp)
    except:
        err_str = 'Grib file not found, url incorrect, trying %s' % grib_url
        raise ValueError(err_str)

# Function download winds & pressure from Canada HRDPS predictions
def get_hrdps(date_requested):
    #Static (Hardwired) Variables
    forecast_hour = range(48)
    gribPrefixP = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' #Canadian file prefixes
    gribPrefixU = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
    gribPrefixV = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
    url = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
    
    # Create datestring
    dateString  = date_requested.strftime('%Y%m%d')
    
    # Set output folder location
    loc_output = 'hrdps_grib_%s' % dateString 
    
    # Make output folder if neccessary
    if os.path.exists(loc_output):
        print('Folder \'{0:s}\' exists.'.format(loc_output))
    else:
        os.mkdir(loc_output)
         
    # Download grib files
    for hour in range(1):#forecast_hour:
        # Pressure (prtmsl)    
        download_grib(gribPrefixP, url, dateString, hour, loc_output)      
        # U wind    
        download_grib(gribPrefixU, url, dateString, hour, loc_output)       
        # V wind    
        download_grib(gribPrefixV, url, dateString, hour, loc_output)
        
        
