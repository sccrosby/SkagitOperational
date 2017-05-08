# -*- coding: utf-8 -*-
"""
Created on Wed May 03 11:20:56 2017

@author: Crosby
"""

import urllib2
import re
from pytz import timezone
from datetime import datetime, timedelta
import os

mllw2NAVD88 = 0
timeDifference = ''
tide48hr = [None] * 48
pattern = '<td nowrap width="25%" align="right" >'
pdt = timezone('US/Pacific')

for dayDiff in range(2):
    date = datetime.now(pdt) - timedelta(days=dayDiff)
    NOAA=('https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?'+
        'name=Sneeoosh%20Point&state=WA&stnid=9448576&threshold=&thresholdDirection=&subordinate=false'+
        '&referenceName=&referenceId=&heightOffsetLow=0.9&heightOffsetHigh=0.97&timeOffsetLow=39&timeOffsetHigh=32'+
        '&heightAdjustedType=R&' + 'bdate={0:04d}{1:02d}{2:02d}'.format(date.year,date.month,date.day) +
        '&edate={0:04d}{1:02d}{2:02d}'.format(date.year,date.month,date.day+1) + 
        '&units=standard&timezone=GMT&datum=MLLW&interval=h&clock=12hour'+
        '&type=txt&annual=false')
    #NOAA = 'https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=9448576&units=standard&bdate={0:04d}{1:02d}{2:02d}&edate=20170503&timezone=GMT&clock=12hour&datum=MLLW&interval=h&action=data'.format(date.year, date.month, date.day)
    print NOAA
    
    
    aResp = urllib2.urlopen(NOAA)
    web_pg = aResp.read()
    patternFound = [m.start() for m in re.finditer(pattern, web_pg)]
    result = [web_pg[m+len(pattern)+2:m+len(pattern)+6] for m in patternFound]
    resultInFloat = [str2num(m)+mllw2NAVD88 for m in result]
#    if dayDiff == 0:
#        tide48hr[7:] = resultInFloat[:41]
#    elif dayDiff == 1:
#        tide48hr[:7] = resultInFloat[41:]
#tideFolder = 'USA/Tide_data'
#if not os.path.exists(tideFolder):
#    os.mkdir(tideFolder)
#dateString  = datetime.now(pdt).strftime('%Y%m%d')
#tideFile = '{0:s}/tide_forecast_{1:s}.txt'.format(tideFolder, dateString)
#fid = open(tideFile,'w')
#date = datetime.now(pdt) - timedelta(days=1)
#dateTemp = datetime(date.year, date.month, date.day, 17)
#for tideIndex in range(48):
#    fid.write('{0:s}   {1:3.3f}\n'.format(dateTemp.strftime('%Y-%m-%d %H:%M:%S'), tide48hr[tideIndex]))
#    dateTemp = dateTemp + timedelta(hours=1)
#fid.close()
#return tide48hr