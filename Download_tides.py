# -*- coding: utf-8 -*-
"""
Downloads NOAA tide predictions for select station and saves in text file
Note, some testing is needed to determine URL format of station name
Created on Wed May 03 11:34:52 2017

Downloads tides from 2017 thru the end of 2021 
@author: Crosby S. C.
"""

import urllib2
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from pytz import timezone
from datetime import datetime, timedelta

import op_functions

# Start and stop
start = datetime(2016,1,1)
stop = datetime(2017,1,1)

# Set Station location & Info 
# Skagit
#location_str = 'Sneeoosh Point, Washington'
#sta_id = '9448576'	
#mllw2navd88 = 0.615 # [meters] Navd88 = MLLW - mllw2NAVD88

# Bellingham
location_str = "Bellingham, Bellingham Bay, Washington"
sta_id = '9449211'
mllw2navd88 = 0.1606 # [meters] Navd88 = MLLW - mllw2NAVD88
   

# Port Susan
#location_str = "Bellingham, Bellingham Bay, Washington"
sta_id = '9448043'
mllw2navd88 = 0.6489 # [meters] Navd88 = MLLW - mllw2NAVD88
  
#--------------------------GET FROM NOAA --------------------------------   
   
# Build NOAA URLs     
interval = 'h' # 'h' - hour, '6'- 6 minutes
url1 = 'https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?&stnid={:s}'.format(sta_id)
url2 = '&threshold=&thresholdDirection=&bdate={:s}&edate={:s}&'.format(start.strftime('%Y%m%d'),stop.strftime('%Y%m%d'))
url3 = 'units=metric&timezone=GMT&datum=MLLW&interval={:s}&clock=12hour&type=txt&annual=false'.format(interval)       
url = url1 + url2 + url3

# Download File to string
aResp = urllib2.urlopen(url)
web_pg = aResp.read()

# Parse Data
count = 0 
tdate = []
tide = []
for m in web_pg.splitlines():
    count += 1
    if count > 14: # Skip header lines
        temp = m.split('\t')
        tdate.append(datetime.strptime(temp[0]+temp[2],'%Y/%m/%d%I:%M %p'))
        tide.append(float(temp[3]))

# Convert from MLLW to NAVD88
tide = [t-mllw2navd88 for t in tide]

# Print data to file
with open('tide_pred_%s.txt' % sta_id,'w') as fid:
    fid.write('Date, Tide_NAVD88_Meters\n')
    for x,y in zip(tdate,tide):
        fid.write('%s %4.2f\n' % (x.strftime('%Y-%m-%d-%H-%M-%S'),y))


import sys
sys.exit()

# ------------------------- GET FROM XTIDE ---------------------------------

# hour-by-hour tides
command_str = 'tide -b \"{0:s}\" -e \"{1:s}\" -l \"{2:s}\" -z -mr -um -s 01:00'.\
    format( datetime.strftime(start,"%Y-%m-%d %H:%M"), datetime.strftime(stop,"%Y-%m-%d %H:%M"), location_str )
        
tides_str = subprocess.check_output(command_str, shell=True)
tide_raw = tides_str.split()
Ntides = len(tide_raw) # combined number of dates and elevations

tide_xtide = np.empty(Ntides/2, dtype='d')
time_epoch = np.empty(Ntides/2, dtype='d')
for tt in range(Ntides/2):
    time_epoch[tt] = tide_raw[2*tt]
    tide_xtide[tt] = tide_raw[2*tt-1]

# Convert EPOCH time stamp to datetime
time = [datetime.fromtimestamp(tt) for tt in time_epoch]

# Convert from MLLW to NAVD88
tide_xtide = [tt-mllw2navd88 for tt in tide_xtide]

# Convert from Local to UTC
pst2gmt = op_functions.get_gmt_offset_2()
time = [tt+timedelta(hours=pst2gmt) for tt in time]
    
## Print data to file
with open('tide_pred_%s_xtide.txt' % sta_id,'w') as fid:
    fid.write('Date, Tide_NAVD88_Meters\n')
    for x,y in zip(time,tide_xtide):
        fid.write('%s %4.2f\n' % (x.strftime('%Y-%m-%d-%H-%M-%S'),y))

# Quick plot
plt.plot(tdate,tide)
plt.plot(time,tide_xtide)
plt.show()
plt.close()






#---------------------OLD

## Set date start and end
#date_start = datetime.strptime('20170101','%Y%m%d')
#date_end = datetime.strptime('20211230','%Y%m%d')
#
## Build URL
#url_noaa = 'https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?'
#url_sta = 'name=%s&state=WA&stnid=9448576&threshold=&thresholdDirection=&subordinate=false' % sta_str
#url_time = ('&referenceName=&referenceId=&heightOffsetLow=0.9&heightOffsetHigh=0.97&timeOffsetLow=39&timeOffsetHigh=32'+
#    '&heightAdjustedType=R&' + 'bdate={0:04d}{1:02d}{2:02d}'.format(date_start.year,date_start.month,date_start.day) +
#    '&edate={0:04d}{1:02d}{2:02d}'.format(date_end.year,date_end.month,date_end.day+1) + 
#    '&units=standard&timezone=GMT&datum=MLLW&interval=h&clock=12hour'+
#    '&type=txt&annual=false')
    