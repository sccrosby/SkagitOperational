# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 15:53:15 2017

@author: crosby
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
#from matplotlib import pyplot as plt

# Hardcoded location
fol_loc = '../Data/downloads/davis_winds'


def get_davis_latest(date_string,zulu_hour,sta_name,days_back):
    # set range of data to get
    date_current = datetime.strptime(date_string,'%Y%m%d')+timedelta(hours=zulu_hour)
    date_start = date_current-timedelta(days=days_back)
      
    # Get list of available data, get two months if needed
    data_file_list = os.listdir('{:s}/{:s}'.format(fol_loc,date_start.strftime('%Y%m')))
    if date_start.month != date_current.month:
        temp = os.listdir('{:s}/{:s}'.format(fol_loc,date_current.strftime('%Y%m')))
        data_file_list = data_file_list+temp
    
    # Create time list and find within range
    time = [datetime.strptime(tt,'davisPS_%Y%m%d_%H%M') for tt in data_file_list]
    time = [ tt for tt in time if (tt >= date_start) ]
    time.sort()
    
    df = read_files(time,fol_loc,sta_name)
    
    return df    



# NOTE: Only works with up to two months
def get_davis_range(date_start,date_end,sta_name):
    # Get list of available data, get two months if needed
    data_file_list = os.listdir('{:s}/{:s}'.format(fol_loc,date_start.strftime('%Y%m')))
    if date_start.month != date_end.month:
        temp = os.listdir('{:s}/{:s}'.format(fol_loc,date_end.strftime('%Y%m')))
        data_file_list = data_file_list+temp
    
    # Create time list and find within range
    time = [datetime.strptime(tt,'davisPS_%Y%m%d_%H%M') for tt in data_file_list]
    time = [ tt for tt in time if (tt >= date_start) & (tt <= date_end)]
    time.sort()
    
    df = read_files(time,fol_loc,sta_name)
    
    return df



def read_files(time,fol_loc,sta_name):
    # Initialize
    N_t = len(time)    
    df = pd.DataFrame({'time':time})
    df['wind_speed'] = np.zeros(N_t)
    df['wind_dir'] = np.zeros(N_t)
    df['slp'] = np.zeros(N_t)

    # Loop through files and grab data for station    
    for tt in range(N_t):
        fol_name = df.loc[tt,'time'].strftime('%Y%m')
        file_name = 'davisPS_{:s}'.format(df.loc[tt,'time'].strftime('%Y%m%d_%H%M'))        
        temp_df = pd.read_csv('{:s}/{:s}/{:s}'.format(fol_loc,fol_name,file_name),index_col=0)
    
        df.loc[tt,'wind_speed'] = temp_df.loc[sta_name,'Wind_Speed']
        df.loc[tt,'wind_dir'] = temp_df.loc[sta_name,'Wind_Direction']
        df.loc[tt,'slp'] = temp_df.loc[sta_name,' SLP']
    
    df.lat = temp_df.loc[sta_name,'Lat']
    df.lon = temp_df.loc[sta_name,'Lon']
    return df


# Test Function with bham kite location
if __name__ == '__main__':   
    # Input variables
    date_string = '20171030'
    zulu_hour = 6    
    sta_name = 'bellinghamkite'
    days_back = 8
    
    df = get_davis_latest(date_string,zulu_hour,sta_name,days_back)
    
    df.plot(x='time',y='wind_speed')
    df.plot(x='time',y='wind_dir')

##print df.keys()
#
#plt.plot(wind_speed)