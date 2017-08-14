# -*- coding: utf-8 -*-
"""
Created on Thu May 04 13:49:35 2017
SkagitOperational - Contains all codes

Run Skagit through scenarios
min tide -0.56
max tide 4.53




@author: Crosby
"""

# Import custom libaraies
import d3d_functions
import misc_functions
import get_param

# Import standard libraries
import numpy as np
import os
import subprocess
import shutil
import time


# ---------------------- SELECT DATE FOR MODEL RUN ----------------------------

# Specifiy date and zulu hour
date_string = '20170601'
zulu_hour = 12

# Select most recent available forecast
#(date_string, zulu_hour) = op_functions.latest_hrdps_forecast()

# ---------------------- INITIALIZE MODEL -------------------------------------

# Model parameters contained in this dictionary, paths, file names, etc
param = get_param.get_param_skagit_SC()

param['num_forecast_hours'] = 1

# Start timer
start_time = time.time()


for tide_level in [4]:#np.arange(0,6,.5): # [m] NAVD88
    
    for wind_speed in [15]: #[m/s]
        
        for wind_dir in np.arange(0,355,5):#[180]: #[135, 255, 15]:  #deg, arriving from, compass coord
        
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
            os.mkdir('temp')
            subprocess.check_call('./run_wave.sh',shell=True)             # Run Wave, which runs Swan using wind data
            
            # Make dir for output
            out_fol = '../../Output/skagit_t{:02d}_s{:d}_d{:d}'.format(int(tide_level*10),wind_speed,wind_dir)
            os.mkdir(out_fol)
            
            # Create list of files to save
            d3d_out_files = ['wavm-skagit_50m.dat', 'wavm-skagit_50m.def'] # for all files, use os.listdir(os.curdir)
            for fname in param['output_locs']:
                d3d_out_files.append(fname+'.tab')
                #d3d_out_files.append(fname+'.sp1')
                #d3d_out_files.append(fname+'.sp2')
            
            # Copy to Output
            for f in d3d_out_files:
                shutil.copyfile(f,'{:s}/{:s}'.format(out_fol,f))
            
            # Go back to working directory        
            os.chdir('../../SkagitOperational')
            
            print 'tide %d, wind speed %d, wind dir %d complete' % (int(tide_level),wind_speed,wind_dir)

# End timer
print 'Total time elapsed: {0:.2f} minutes'.format(((time.time() - start_time)/60.))







































