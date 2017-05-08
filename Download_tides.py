# -*- coding: utf-8 -*-
"""
Downloads NOAA tide predictions for select station and saves in text file
Note, some testing is needed to determine URL format of station name
Created on Wed May 03 11:34:52 2017
@author: Crosby S. C.
"""

import urllib2
from pytz import timezone
from datetime import datetime, timedelta

# Set Constant
mllw2NAVD88 = 0.615 # [meters] Navd88 = MLLW + mllw2NAVD88

# Set Station location
sta_id = '9448576'
sta_str = 'Sneeoosh%20Point'

# Set date start and end
date_start = datetime.strptime('20170101','%Y%m%d')
date_end = datetime.strptime('20171230','%Y%m%d')

# Build URL
url_noaa = 'https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?'
url_sta = 'name=%s&state=WA&stnid=9448576&threshold=&thresholdDirection=&subordinate=false' % sta_str
url_time = ('&referenceName=&referenceId=&heightOffsetLow=0.9&heightOffsetHigh=0.97&timeOffsetLow=39&timeOffsetHigh=32'+
    '&heightAdjustedType=R&' + 'bdate={0:04d}{1:02d}{2:02d}'.format(date_start.year,date_start.month,date_start.day) +
    '&edate={0:04d}{1:02d}{2:02d}'.format(date_end.year,date_end.month,date_end.day+1) + 
    '&units=standard&timezone=GMT&datum=MLLW&interval=h&clock=12hour'+
    '&type=txt&annual=false')
url = url_noaa + url_sta + url_time

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

# Convert to meters
tide = [t*0.3048 for t in tide]

# Convert to NAVD88
tide = [t+mllw2NAVD88 for t in tide]

# Print data to file
with open('tide_pred_%s.txt' % sta_id,'w') as fid:
    fid.write('Date, Tide_NAVD88_Meters\n')
    for x,y in zip(tdate,tide):
        fid.write('%s %4.2f\n' % (x.strftime('%Y-%m-%d-%H-%M-%S'),y))


    