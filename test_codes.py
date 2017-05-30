# -*- coding: utf-8 -*-
"""
Created on Thu May 04 13:49:35 2017
SkagitOperational - Contains all codes

File Structure

Documents/
    SkagitOperational/  (git repo)
        Archive/
    Grids/
        delft3d/
        delftfm/
        suntans/
    Data/
        raw_downloads/
            hrdps/
                hrdps_grib_xxxxx/            
        crop/
            hrdps/
                hrdps_crop_xxxxx/
        d3d_input/
            skagit_wind_hrdps/    
    openearthtools/
    
@author: Crosby
"""
# Clear workspace
#import my_utilities
#my_utilities.clear_all()
#my_utilities.reset()

# Import libaraies
import op_functions
import crop_functions
import numpy as np
#from datetime import datetime, timedelta

# Test functions
print 'Current offset to GMT is %d (method1)' % op_functions.get_gmt_offset()
print 'Current offset to GMT is %d (method2)' % op_functions.get_gmt_offset_2()



# Find latest
#from seek_latest_canadian_data import find_latest_canadian_data
#gribPrefix = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_'
#(x,y) = find_latest_canadian_data(gribPrefix)

# Determine most recent available forecast
(latest_date, latest_zulu) = op_functions.latest_hrdps_forecast()

# Download raw grib files
# op_functions.get_hrdps(latest_date, latest_zulu)

# Parse grib, crop to region, and store
bounds = np.asarray([[207,56],[287,219]]) # Salish Sea region of HRDPS forecast
crop_functions.region_crop(latest_date, latest_zulu, bounds)

# Prep D3D wind files for Skagit








































