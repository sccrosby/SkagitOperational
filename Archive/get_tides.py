# -*- coding: utf-8 -*-
"""
Created on Fri May 05 12:31:56 2017

@author: Crosby
"""

# Inputs
datestring = '20170504'
forecast_hour = 6

from datetime import datetime

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

# Load Tide File
fname = 'tide_pred_9448576.txt'
with open(fname) as fid:
    content = fid.readlines()

# Disregard Header    
content.pop(0)

# Format of time data
t_format = '%Y-%m-%d-%H-%M-%S'

# Parse time and tide data 
time = [datetime.strptime(x.split()[0],t_format) for x in content]    
tide = [float(x.split()[1]) for x in content]

# Format input date
temp = '%s%02d' % (datestring, forecast_hour)
time_forecast =  datetime.strptime(temp,'%Y%m%d%H')

# Find index for requested time
time_nearest = nearest(time,time_forecast)
idx = time.index(time_nearest)

# Return 48-hour forecast of tides
model_time = time[idx:idx+48]
model_tide = tide[idx:idx+48]