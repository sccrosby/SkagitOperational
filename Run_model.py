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
            bbay/
        delftfm/
        suntans/
        
    Data/
        raw_downloads/
            hrdps/
                max_files/
                hrdps_grib_xxxxx/            
        crop/
            hrdps/
                hrdps_crop_xxxxx/
        d3d_input/
            skagit/    
    
    ModelRuns/
        skagit_wave_50m/
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
# To test crontab in its environment, use env -i sh -c './run_script.sh'
import matplotlib
matplotlib.use('Agg')

# Import custom libaraies
import op_functions
import crop_functions
import d3d_functions
import misc_functions
import plot_functions
import get_param

# Import standard libraries
import numpy as np
import os
import subprocess
import shutil
import time


# ---------------------- SELECT DATE FOR MODsEL RUN ----------------------------

# OPTION 1: Specifiy date and zulu hour
# date_string = '20170601'
# zulu_hour = 12

# OPTION 2: Select most recent available forecast
(date_string, zulu_hour) = op_functions.latest_hrdps_forecast()

# ------------------------ SET GOOGLE DRIVE FOLDER ----------------------------
google_drive = '../GoogleDrive'

# ---------------------- INITIALIZE MODEL -------------------------------------

param = get_param.get_param_skagit()

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

# Make Wind Plots for BBay
print 'Making wind plots for BBay'
plot_functions.plot_bbay_wind(date_string, zulu_hour, param)

# Sync Bbay Plots to Google Drive Folder       
print 'Syncing google drive BellinghamBay Folder'
griveCommand = 'grive -s {:s}/'.format('BellinghamBay')
os.chdir(google_drive)
err = subprocess.check_call(griveCommand, shell=True)
os.chdir('../SkagitOperational')

#(X, Y, U10, V10)= op_functions.read_hrdps_grib(date_string, zulu_hour, param)

# Parse grib, crop to region, and store
#test_file = '{0:s}/{1:s}{2:s}/{3:s}{2:s}_{4:02d}z_47.dat'.format(param['fol_wind_crop'],
#    param['folname_crop_prefix'],date_string,param['fname_prefix_wind'],zulu_hour)
#if os.path.isfile(test_file):
#    print 'Winds already processed and cropped, skipping'
#else:
#    crop_functions.region_crop(date_string, zulu_hour, param)

# Remove all files from model folder
misc_functions.clean_folder(param['fol_model'])

# Create D3D amuv files
d3d_functions.write_amuv(date_string,zulu_hour,param)

# Get tide predictions for forecast
tide = op_functions.get_tides(date_string, zulu_hour, param)

# Write mdw file to model folder
d3d_functions.write_mdw(date_string, zulu_hour, tide, param)

# Copy files to model folder 
for fname in ['fname_dep','fname_grid','fname_enc','fname_meteo_grid','fname_meteo_enc','run_script']:
    shutil.copyfile('{0:s}/{1:s}'.format(param['fol_grid'],param[fname]),'{0:s}/{1:s}'.format(param['fol_model'],param[fname]))
# Copy location files to model folder
for fname in param['output_locs']:
   shutil.copyfile('{0:s}/{1:s}'.format(param['fol_grid'],fname),'{0:s}/{1:s}'.format(param['fol_model'],fname))

# Make run file executeable (when copying it loses this property)
import stat
myfile = '{:s}/{:s}'.format(param['fol_model'],param['run_script'])
st = os.stat(myfile)
os.chmod(myfile, st.st_mode | stat.S_IEXEC)

# Run Model 
print 'Beginning D3D model run'
os.chdir(param['fol_model'])
if not os.path.isdir('temp'):
    os.mkdir('temp')  # Add temp directory for outputing raw swan files
subprocess.check_call('./run_wave.sh',shell=True)  # Start D3D
os.chdir('../../SkagitOperational')

# Plot 
print 'Plotting'
max_wind = 10
plot_functions.plot_skagit_hsig(date_string, zulu_hour, max_wind, tide, param)

# Copy files and Google Drive Folder
for hour in range(param['num_forecast_hours']):
    fname_src = '{0:s}/wind_wave_skagit{1:s}_{2:02d}z_{3:02d}.png'.format(param['fol_plots'], date_string, zulu_hour, hour)
    fname_dest = '{:s}/{:s}/wind_wave_skagit_latest_{:02d}.png'.format(google_drive, param['folname_google_drive'], hour)
    shutil.copyfile(fname_src,fname_dest)
    
# Sync Google Drive Folder       
griveCommand = 'grive -s {:s}/'.format(param['folname_google_drive'])
os.chdir(google_drive)
err = subprocess.check_call(griveCommand, shell=True)
os.chdir('../SkagitOperational')

# End timer
print 'Total time elapsed: {0:.2f} minutes'.format(((time.time() - start_time)/60.))







































