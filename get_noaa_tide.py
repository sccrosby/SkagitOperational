# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 10:18:20 2017

@author: crosby
"""

import urllib
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from pytz import timezone
from datetime import datetime, timedelta
import pandas as pd
import os

import op_functions

# Start and stop
(date_string, zulu_hour) = op_functions.latest_hrdps_forecast()

# Bellingham
location_str = "Bellingham, Bellingham Bay, Washington"
sta_id = '9449211'
mllw2navd88 = 0.1606 # [meters] Navd88 = MLLW - mllw2NAVD88
   
# Port Susan
#location_str = "Bellingham, Bellingham Bay, Washington"
sta_id = '9448043'
mllw2navd88 = 0.6489 # [meters] Navd88 = MLLW - mllw2NAVD88

# Cherry Point
sta_id = '9449424'
  
#--------------------------GET FROM NOAA --------------------------------   
   
## Build NOAA URLs     
#interval = 'h' # 'h' - hour, '6'- 6 minutes
#url1 = 'https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?&stnid={:s}'.format(sta_id)
#url2 = '&threshold=&thresholdDirection=&bdate={:s}&edate={:s}&'.format(start.strftime('%Y%m%d'),stop.strftime('%Y%m%d'))
#url3 = 'units=metric&timezone=GMT&datum=MLLW&interval={:s}&clock=12hour&type=txt&annual=false'.format(interval)       
#url = url1 + url2 + url3
#
## Download File to string
#aResp = urllib2.urlopen(url)
#web_pg = aResp.read()

end_date = datetime.strptime(date_string,'%Y%m%d')
start_date = end_date - timedelta(days=2)

url1 = 'https://tidesandcurrents.noaa.gov/api/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&station={:s}'.format(sta_id)
url2 = '&begin_date={:s}&end_date={:s}&datum=MLLW&units=english&time_zone=GMT&format=csv'.format(start_date.strftime('%Y%m%d'),end_date.strftime('%Y%m%d'))

# Download File to string
fname = 'temp.csv'
urllib.urlretrieve(url1+url2,fname)
df = pd.read_csv(fname)
os.remove(fname)















