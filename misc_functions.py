# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 11:05:38 2017

@author: crosby
"""
import os, shutil
from datetime import datetime, timedelta
import subprocess

# Remove all files and directories from folder 
def clean_folder(folder):    
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path) #comment if want to remove only files
        except Exception as e:
            print(e)

def get_xtides():
    #=================== Tides ========================
    location_str = "Crescent Harbor, N. Whidbey Island, Washington"
    Nx = 415
    Ny = 490

    dt = timedelta(days=2, hours=1)
    Start = tTide
    Next  = tTide + dt

    command_str = 'tide -b \"{0:s}\" -e \"{1:s}\" -l \"{2:s}\" -mr -um -s 01:00'.\
        format( datetime.strftime(Start,"%Y-%m-%d %H:%M"), datetime.strftime(Next,"%Y-%m-%d %H:%M"), location_str )
    tidesStr = subprocess.check_output(command_str, shell=True)
    tides = tidesStr.split()
    Ntides = len(tides)
    if Ntides > 96:
        Ntides = 96
    tide = np.empty(Ntides/2, dtype='d')
    for n in range(0,Ntides,2):
        tide[n/2] = (float(tides[n+1]))
    
    return tide