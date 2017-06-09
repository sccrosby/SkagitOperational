# -*- coding: utf-8 -*-
"""
Created on Thu May 04 13:49:35 2017
SkagitOperational - Contains all codes

Assumed File Structure

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
    
    ModelRuns
        skagit_wave_50m/
            
    openearthtools/ (svn repo)
    
@author: Crosby
"""

# Import custom libaraies
import op_functions
import crop_functions
import d3d_functions
import misc_functions

# Import standard libraries
import numpy as np
import os
import sys
import subprocess
import shutil
import time
from datetime import datetime, timedelta

# ---------------------- SELECT DATE FOR MODEL RUN ----------------------------

# Specifiy date and zulu hour
date_string = '20170601'
zulu_hour = 12

# Select most recent available forecast
#(date_string, zulu_hour) = op_functions.latest_hrdps_forecast()

# ---------------------- INITIALIZE MODEL -------------------------------------

# Model parameters contained in this dictionary, paths, file names, etc
param = {}

# Length of forecast
param['num_forecast_hours']     = 1    # numer of files [hours]
param['crop_bounds']            = np.asarray([[207,56],[287,219]]) # Salish Sea region
param['tide_file']              = 'tide_pred_9448576.txt' # Set tide file to use

# Set some constants for creating amu/avu files
param['line_meteo_grid_size']   = 1     # Line number in meteo grid with Nx, Ny
param['line_header_skip']       = 3     # Number of header lines in meteo file
param['xLL']                    = 526108.0  # lower left corner of SWAN computational grid
param['yLL']                    = 5343228.0

# Set locations
param['fol_model']              = '../ModelRuns/skagit_wave_50m'
param['fol_wind_grib']          = '../Data/downloads/hrdps'
param['fol_wind_crop']          = '../Data/crop/hrdps'
param['fol_grid']               = '../Grids/delft3d/skagit'
    
# Set file names
param['folname_crop_prefix']    = 'hrdps_crop_'
param['folname_grib_prefix']    = 'hrdps_grib_'
param['fname_prefix_wind']      = 'wind_crop_' #{0:s}_{1:02d}z'.format(dateString,zulu_hour)
param['fname_meteo_grid']       = 'skagit_meteo.grd'
param['fname_meteo_enc']        = 'skagit_meteo.enc'
param['fname_grid']             = 'skagit_50m.grd'
param['fname_dep']              = 'skagit_50m.dep'
param['fname_enc']              = 'skagit_50m.enc'
param['wind_u_name']            = 'wind_skagit.amu'    
param['wind_v_name']            = 'wind_skagit.amv'
param['fname_mdw']              = 'skagit_50m.mdw'
param['run_script']             = 'run_wave.sh'

# Set Output Locs
param['output_locs']            = ['LongB.loc',
                                   'CrossBN.loc',
                                   'CrossBS.loc']   

# HRDPS prefixes and url
param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'


# Start timer
start_time = time.time()



# Determine offset from local time (PST/PDT) to GMT +
print 'Current offset to GMT is %d (method1)' % op_functions.get_gmt_offset()
print 'Current offset to GMT is %d (method2)' % op_functions.get_gmt_offset_2()


# Download raw grib files
#op_functions.get_hrdps(date_string, zulu_hour, param)

# Parse grib, crop to region, and store
#crop_functions.region_crop(date_string, zulu_hour, param)


# Get tide predictions for forecast
# tides = op_functions.get_tides(date_string, zulu_hour, param)
for tide_level in [3]:#[0., 1., 2., 3.]:
    
    for wind_speed in [20]:# [25, 20, 15, 10, 5]: #[m/s]
        
        for wind_dir in [120]:#[0, 60, 120, 180, 240, 300]:  #deg, arriving from, compass coord
        
            # Functions expecting a list of water/tide levels
            tide = [tide_level]        
        
            # Remove all files from model folder
            misc_functions.clean_folder(param['fol_model'])
            
            # Write amuv files
            d3d_functions.write_amuv_homog(date_string, zulu_hour, param, wind_speed, wind_dir)
            
            # Write mdw file to model folder
            d3d_functions.write_mdw(date_string, zulu_hour, tide, param)
            #d3d_functions.make_test_loc(param)
            
            # Copy grid files to model folder 
            for fname in ['fname_dep','fname_grid','fname_enc','fname_meteo_grid','fname_meteo_enc','run_script']:
                shutil.copyfile('{0:s}/{1:s}'.format(param['fol_grid'],param[fname]),'{0:s}/{1:s}'.format(param['fol_model'],param[fname]))           
            # Copy location files to model folder
            for fname in param['output_locs']:
                shutil.copyfile('{0:s}/{1:s}'.format(param['fol_grid'],fname),'{0:s}/{1:s}'.format(param['fol_model'],fname))
            
            # Make run file executeable (loses this property in copy over)
            import stat
            myfile = '{:s}/{:s}'.format(param['fol_model'],param['run_script'])
            st = os.stat(myfile)
            os.chmod(myfile, st.st_mode | stat.S_IEXEC)
            
            # Run Model 
            os.chdir(param['fol_model'])
            subprocess.check_call('./run_wave.sh',shell=True)             # Run Wave, which runs Swan using wind data
            
            # Make dir for output
            out_fol = '../../Output/skagit_t{:d}_s{:d}_d{:d}'.format(int(tide),wind_speed,wind_dir)
            os.mkdir(out_fol)
            
            # Copy files to output
            my_file_list = ['wavm-skagit_50m.dat', 'wavm-skagit_50m.def'] # for all files, use os.listdir(os.curdir)
            for f in my_file_list:
                shutil.copyfile(f,'{:s}/{:s}'.format(out_fol,f))
            
            # Go back to working directory        
            os.chdir('../../SkagitOperational')
            
            print 'tide %d, wind speed %d, wind dir %d complete' % (int(tide),wind_speed,wind_dir)

# End timer
print 'Total time elapsed: {0:.2f} minutes'.format(((time.time() - start_time)/60.))







































