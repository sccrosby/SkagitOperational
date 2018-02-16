# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 14:32:11 2017

@author: crosby
"""

from plot_functions import load_hrdps_point_hindcast, load_hrdps_mask
import op_functions
import davis_weather
import get_param
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib import dates as mdates
from datetime import timedelta

# set end date
date_string = '20180124'
zulu_hour = 0

# Choose station
sta_name = 'bellinghamkite'

# File locations
param = get_param.get_param_bbay()

ms2mph = 2.237     

# Get time offset  
gmt_off = op_functions.get_gmt_offset()

#----------------------- Load up HRDP Land Mask----------------------------------------
(Nx,Ny) = load_hrdps_mask(date_string, zulu_hour, param) 

# ------------------Get Davis Winds---------------------------------------    
days_back = 7
df = davis_weather.get_davis_latest(date_string,zulu_hour,sta_name,days_back)
df['time'] = df['time']-timedelta(hours=7)
df['wind_speed'] = df['wind_speed']*ms2mph
df['slp'] = df['slp']/10

print (df.lat, df.lon)
# -------------------- Load Concatenated Hindcast ------------------------
num_goback = 4*days_back;     # Number of forecasts to go back to (6hr each)
(hind_time, hind_speed, hind_dir, hind_slp) = load_hrdps_point_hindcast(date_string, zulu_hour, param, Nx, Ny, df.lat, df.lon, num_goback)
hind_time = [x - timedelta(hours=gmt_off) for x in hind_time] # Convert from UTC to local
   

# Setup figure,            
fig = plt.figure(figsize=(8.,11.))   
   
# set up subplots    
gs = gridspec.GridSpec(30,1)
gs.update(left=0.17, right=0.98, top=0.98, bottom=0.015, wspace=0.15, hspace=0.05)     
ax2 = plt.subplot(gs[2:10,0])
ax3 = plt.subplot(gs[11:19,0])        
ax4 = plt.subplot(gs[20:28,0])    

# Plot Speed
ax2.plot(df['time'],df['wind_speed'],'k.',label='Observations')        
ax2.plot(hind_time,hind_speed,'r',label='Hindcast')
ax2.set_ylabel('Wind Speed [mph]')
ax2.legend(frameon=False, prop={'size':10}, bbox_to_anchor=(1, 1.3), ncol=3 )
ax2.set_ylim([0, 50])
ax2.set_xlim([hind_time[0], hind_time[-1]])
#y_top = ax2.get_ylim()

# Plot Dir
ax3.plot(df['time'],df['wind_dir'],'k.',label='Observations')        
ax3.plot(hind_time,hind_dir,'r',label='Hindcast')
ax3.set_ylabel('Wind Direction [deg]')
ax3.set_ylim([0, 360])
ax3.set_xlim([hind_time[0], hind_time[-1]])
#ax3.legend(frameon=False, prop={'size':10}, bbox_to_anchor=(1, 1.3), ncol=3 )
  
# Plot SLP
ax4.plot(df['time'],df['slp'],'k.',label='Observations')        
ax4.plot(hind_time,hind_slp,'r',label='Hindcast')
ax4.set_ylabel('Pressure [hP]')
ax4.set_ylim([97, 103])
ax4.set_xlim([hind_time[0], hind_time[-1]])
#ax4.legend(frameon=False, prop={'size':10}, bbox_to_anchor=(1, 1.3), ncol=3 )

# Ax color
#ax1.set_axis_bgcolor('white')
#ax2.set_axis_bgcolor('white') 
#ax3.set_axis_bgcolor('silver')     

# Make x-axis nice 
weeks = mdates.WeekdayLocator()
days = mdates.DayLocator()
hours = mdates.HourLocator()    
days_fmt = mdates.DateFormatter('%m/%d')

major = weeks
minor = days

ax2.xaxis.set_major_locator(major)
ax2.xaxis.set_major_formatter(days_fmt)
ax2.xaxis.set_minor_locator(minor)
ax2.tick_params(labelbottom='off')

ax3.xaxis.set_major_locator(major)
ax3.xaxis.set_major_formatter(days_fmt)
ax3.xaxis.set_minor_locator(minor)              
ax3.tick_params(labelbottom='off')

ax4.xaxis.set_major_locator(major)
ax4.xaxis.set_major_formatter(days_fmt)
ax4.xaxis.set_minor_locator(minor)              

fig.savefig('BellinghamKite_Deploy2.png',dpi=200)
plt.close()
           