
# -*- coding: utf-8 -*-
"""
#---------------------------------------------------------------------#
#----------------------Skagit Operational Model-----------------------#
#---------------------------------------------------------------------#

#-----------------------Assumed File Structure------------------------#

Documents/
    SkagitOperational/  (git repo)
        Archive/
        
    Grids/
        delft3d/
            skagit/
            skagitE_200m/
            bbay/            
        delftfm/
        suntans/
        
    Data/
        raw_downloads/
            hrdps/
                max_files/
                hrdps_grib_xxxxx/            
            davis_winds/
            noaa_ww3/
        crop/
            hrdps/
                hrdps_crop_xxxxx/
        d3d_input/
            skagit/    
    
    ModelRuns/
        skagit_wave_50m/
        skagit_wave_100m/
        bbay_150m/
    
    Plots/
        skagit_50m/
            plotting_files/
    
    GoogleDrive/
        SkagitPlots/
                   
    openearthtools/ (svn repo)
    
@author: S. C. Crosby
"""

# Note, it's possible that forecast 48 is avialable several mintues before 043, crashing the program

# Needed for use with crontab, By default matplotlib uses x-windows, see https://stackoverflow.com/questions/2801882/generating-a-png-with-matplotlib-when-display-is-undefined
# To test crontab in its environment, use: env -i sh -c './run_script.sh'

import matplotlib
matplotlib.use('Agg')

# Import custom libaraies
import op_functions
import d3d_functions
import misc_functions
import plot_functions
import get_param
import send_email_text
import swan_fns

# Import standard libraries
import os
import subprocess
import shutil
import time


# ---------------------- SELECT DATE FOR MODsEL RUN ----------------------------

# OPTION 1: Specifiy date and zulu hour  (Run Historical)
#date_string = '20180208'
#zulu_hour = 18

# OPTION 2: Select most recent available forecast
(date_string, zulu_hour) = op_functions.latest_hrdps_forecast()

RUN_BBAY_WAVE   = True
RUN_SKAGIT_WAVE = True
SYNC_GDRIVE     = True

#RUN_BBAY_WAVE   = False
#RUN_SKAGIT_WAVE = False
#SYNC_GDRIVE     = False

# ---------------------- INITIALIZE MODEL -------------------------------------
param = get_param.get_param_bbay()

# Determine offset from local time (PST/PDT) to GMT +
print 'Current offset to GMT is %d (method1)' % op_functions.get_gmt_offset()
print 'Current offset to GMT is %d (method2)' % op_functions.get_gmt_offset_2()

# Start timer
start_time = time.time()

# Download raw grib files
test_file = '{0:s}/{1:s}{2:s}/{3:s}{2:s}{4:02d}_P047-00.grib2'.format(param['fol_wind_grib'],
    param['folname_grib_prefix'],date_string,param['hrdps_PrefixP'],zulu_hour)
if os.path.isfile(test_file):
    print 'Grib files already downloaded, skipping'
else:
    op_functions.get_hrdps(date_string, zulu_hour, param)

try:
    if RUN_BBAY_WAVE:
        # Remove all files from model folder
        misc_functions.clean_folder(param['fol_model'])
        
