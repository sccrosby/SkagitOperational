# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 11:25:48 2017

@author: crosby
"""


import matplotlib
matplotlib.use('Agg')

# Import custom libaraies
import op_functions
#import d3d_functions
#import misc_functions
import plot_functions
import get_param
import send_email_text

# Import standard libraries
import os
import subprocess
#import shutil
#import time

# Get current forecast
(date_string, zulu_hour) = op_functions.latest_hrdps_forecast()

# Download raw grib files
param = get_param.get_param_bbay()
test_file = '{0:s}/{1:s}{2:s}/{3:s}{2:s}{4:02d}_P047-00.grib2'.format(param['fol_wind_grib'],
    param['folname_grib_prefix'],date_string,param['hrdps_PrefixP'],zulu_hour)
if os.path.isfile(test_file):
    print 'Grib files already downloaded, skipping'
else:
    op_functions.get_hrdps(date_string, zulu_hour, param)

# Get TWL predictions
try:
    sta_id = '9449424'
    sta_name = 'CherryPoint'
    lat = 48. + 51.8/60
    lon = -122. - 45.5/60
    plot_functions.plot_twl_obs_point(date_string,zulu_hour,param,sta_id,sta_name,lat,lon)
except Exception as inst:
    alert = 'Recieved error: {:s}, TWL predictions failed station {:s}'.format(inst,sta_name)
    print alert
    send_email_text.send_email('schcrosby@gmail.com',alert) 
try:
    sta_id = '9444900'
    sta_name = 'PortTownsend'
    lat = 48. + 6.8/60
    lon = -122. - 45.6/60
    plot_functions.plot_twl_obs_point(date_string,zulu_hour,param,sta_id,sta_name,lat,lon)
except Exception as inst:
    alert = 'Recieved error: {:s}, TWL predictions failed station {:s}'.format(inst,sta_name)
    print alert
    send_email_text.send_email('schcrosby@gmail.com',alert) 
try:
    sta_id = '9447130'
    sta_name = 'Seattle'
    lat = 47. + 36.1/60
    lon = -122. - 20.3/60
    plot_functions.plot_twl_obs_point(date_string,zulu_hour,param,sta_id,sta_name,lat,lon)
except Exception as inst:
    alert = 'Recieved error: {:s}, TWL predictions failed station {:s}'.format(inst,sta_name)
    print alert
    send_email_text.send_email('schcrosby@gmail.com',alert) 
try:
    sta_id = '9446484'
    sta_name = 'Tacoma'
    lat = 47. + 16.2/60
    lon = -122. - 24.8/60
    plot_functions.plot_twl_obs_point(date_string,zulu_hour,param,sta_id,sta_name,lat,lon)
except Exception as inst:
    alert = 'Recieved error: {:s}, TWL predictions failed station {:s}'.format(inst,sta_name)
    print alert
    send_email_text.send_email('schcrosby@gmail.com',alert) 

try:
    # Make Validation Plots
    print 'Making Validation Plots'
    sta_name = 'bellinghamkite'
    plot_functions.plot_davis_val(date_string, zulu_hour, param, sta_name)
    sta_name = 'cruiseterminal'
    plot_functions.plot_davis_val(date_string, zulu_hour, param, sta_name)
    #sta_name = 'nskabb'
    #plot_functions.plot_davis_val(date_string, zulu_hour, param, sta_name)
    sta_name = 'whatcomcc'
    plot_functions.plot_davis_val(date_string, zulu_hour, param, sta_name)
except Exception as inst:
    alert = 'Recieved error: {:s}, David Wind validation plots failed on {:s}'.format(inst,sta_name)
    print alert
    send_email_text.send_email('schcrosby@gmail.com',alert) 
    

# Sync plots to Google Drive Folder       
print 'Syncing google drive BellinghamBay Folder'
griveCommand = 'grive -s {:s}/'.format('BellinghamBay')
os.chdir(param['fol_google'])
err = subprocess.check_call(griveCommand, shell=True)
os.chdir('../SkagitOperational')


