# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 14:32:11 2017

@author: crosby
"""

import op_functions
import davis_weather
import scipy
from datetime import timedelta, datetime

# Convert timestamp to datenum
def datetime2matlabdn(dt):
   #ord = dt.toordinal()
   mdn = dt + timedelta(days = 366)
   frac = (dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
   return mdn.toordinal() + frac

# set end date
date_start = datetime(2017,11,10)
date_end = datetime(2018,1,31)

# Choose station
sta_name = 'bellinghamkite'

# Get time offset  
gmt_off = op_functions.get_gmt_offset()

# ------------------Get Davis Winds---------------------------------------    
df = davis_weather.get_davis_range(date_start,date_end,sta_name)
df['time'] = df['time']-timedelta(hours=7)
df['wind_speed'] = df['wind_speed']
df['slp'] = df['slp']/10

# Convert dictionary to set of lists, note orient is important!)
tosave = df.to_dict(orient='list')
tosave['lat'] = df.lat
tosave['lon'] = df.lon

# Convert timestamps to datenums
mtime = [datetime2matlabdn(tt) for tt in tosave['time']]
tosave['time'] = mtime

# save to mat file
scipy.io.savemat(file_name='{:s}.mat'.format(sta_name),mdict=tosave,appendmat=False,oned_as='column',do_compression=True)



