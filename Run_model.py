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
    
    Plots/
        skagit_50m/
            plotting_files/
    
    GoogleDrive/
        SkagitPlots/
                   
    openearthtools/ (svn repo)
    
@author: S. C. Crosby
"""

#http://dd.weather.gc.ca/model_hrdps/west/grib2/12/031/CMC_hrdps_west_UGRD_TGL_10_ps2.5km_2017061312_P031-00.grib2
#http://dd.weather.gc.ca/model_hrdps/west/grib2/12/031/CMC_hrdps_west_UGRD_TGL_10_ps2.5km_2017061312_P031-00.grib2

# Import custom libaraies
import op_functions
import crop_functions
import d3d_functions
import misc_functions
import plot_functions

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

# ------------------------ SET GOOGLE DRIVE OUTPUT ----------------------------
google_drive = '../GoogleDrive'
google_drive_fol = 'SkagitPlots'

# ---------------------- INITIALIZE MODEL -------------------------------------

# Model parameters contained in this dictionary, paths, file names, etc
param = {}

# Length of forecast
param['num_forecast_hours']     = 48    # numer of files [hours]
param['crop_bounds']            = np.asarray([[207,56],[287,219]]) # Salish Sea region
param['tide_file']              = 'tide_pred_9448576.txt' # Set tide file to use

# Set some constants for creating amu/avu files
param['line_meteo_grid_size']   = 2     # Line number in meteo grid with Nx, Ny
param['line_header_skip']       = 4     # Number of header lines in meteo file
param['xLL']                    = 526108.0  # lower left corner of SWAN computational grid
param['yLL']                    = 5343228.0

# Set locations
param['fol_model']              = '../ModelRuns/skagit_wave_50m'
param['fol_wind_grib']          = '../Data/downloads/hrdps'
param['fol_wind_crop']          = '../Data/crop/hrdps'
param['fol_grid']               = '../Grids/delft3d/skagit'
param['fol_plots']              = '../Plots/skagit_50m'
    
# Set file names and prefixes
param['folname_crop_prefix']    = 'hrdps_crop_'
param['folname_grib_prefix']    = 'hrdps_grib_'
param['fname_prefix_wind']      = 'wind_crop_' #{0:s}_{1:02d}z'.format(dateString,zulu_hour)
param['fname_meteo_grid']       = 'skagit_meteo_50m.grd'
param['fname_meteo_enc']        = 'skagit_meteo_50m.enc'
param['fname_grid']             = 'skagit_50m.grd'
param['fname_dep']              = 'skagit_50m.dep'
param['fname_enc']              = 'skagit_50m.enc'
param['wind_u_name']            = 'wind_skagit.amu'    
param['wind_v_name']            = 'wind_skagit.amv'
param['fname_mdw']              = 'skagit_50m.mdw'
param['run_script']             = 'run_wave.sh'

# Set Output Locs
param['output_locs']            = []
#param['output_locs']            = ['LongB.loc',
#                                   'CrossBN.loc',
#                                   'CrossBS.loc']   
                                   
# HRDPS prefixes and url
param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'

# Set GMT offset to local time
param['gmt_offset']             = op_functions.get_gmt_offset_2()

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

# Parse grib, crop to region, and store
test_file = '{0:s}/{1:s}{2:s}/{3:s}{2:s}_{4:02d}z_47.dat'.format(param['fol_wind_crop'],
    param['folname_crop_prefix'],date_string,param['fname_prefix_wind'],zulu_hour)
if os.path.isfile(test_file):
    print 'Winds already processed and cropped, skipping'
else:
    crop_functions.region_crop(date_string, zulu_hour, param)

# Remove all files from model folder
misc_functions.clean_folder(param['fol_model'])

# Write amu and amv files
d3d_functions.write_amuv(date_string, zulu_hour, param)

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
    fname_dest = '{:s}/{:s}/wind_wave_skagit_latest_{:02d}.png'.format(google_drive, google_drive_fol, hour)
    shutil.copyfile(fname_src,fname_dest)
    
# Sync Google Drive Folder       
griveCommand = 'grive -s {:s}/'.format(google_drive_fol)
os.chdir(google_drive)
err = subprocess.check_call(griveCommand, shell=True)
os.chdir('../SkagitOperational')

# End timer
print 'Total time elapsed: {0:.2f} minutes'.format(((time.time() - start_time)/60.))







































