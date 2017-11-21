# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 10:18:20 2017

@author: crosby
"""

import urllib
import urllib2
from datetime import datetime, timedelta
import pandas as pd
import os

import op_functions

  
#-------------------------- Observations --------------------------------   
def get_obs(sta_id,start_date,end_date):
    url1 = 'https://tidesandcurrents.noaa.gov/api/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&station={:s}'.format(sta_id)
    url2 = '&begin_date={:s}&end_date={:s}&datum=MLLW&units=english&time_zone=GMT&format=csv'.format(start_date.strftime('%Y%m%d'),end_date.strftime('%Y%m%d'))
    
    # Download File to string
    fname = 'temp.csv'
    urllib.urlretrieve(url1+url2,fname)
    df_obs = pd.read_csv(fname)
    os.remove(fname)
    
    # Create new data frame to output
    df = pd.DataFrame()
    
    # Add time and observations
    df['time'] = [datetime.strptime(tt,'%Y-%m-%d %H:%M') for tt in df_obs['Date Time']]
    df['twl'] = df_obs[' Water Level']
    
    return df

  
#--------------------------GET FROM NOAA --------------------------------   
def get_pred(sta_id,start_date,end_date):  
    url1 = 'https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?&stnid={:s}'.format(sta_id)
    url2 = '&threshold=&thresholdDirection=&bdate={:s}&edate={:s}&units=standard&timezone=GMT&datum=MLLW&interval=6&clock=24hour&type=txt&annual=false'.format(start_date.strftime('%Y%m%d'),end_date.strftime('%Y%m%d'))
      
    # Download File to string
    fname = 'temp.csv'
    urllib.urlretrieve(url1+url2,fname)
    #df_obs = pd.read_csv(fname)
    #os.remove(fname) 
    
    url = url1 + url2 
    
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
            tdate.append(datetime.strptime(temp[0]+temp[2],'%Y/%m/%d%H:%M'))
            tide.append(float(temp[3]))
    
    df = pd.DataFrame()
    df['time'] = tdate
    df['twl'] = tide
    
    return df


if __name__ == '__main__':      
    # Start and stop
    (date_string, zulu_hour) = op_functions.latest_hrdps_forecast()
    
    # Bellingham
    sta_id = '9449211'
       
    # Port Susan
    sta_id = '9448043'
    
    # Cherry Point
    sta_id = '9449424'
    
    # date range    
    end_date = datetime.strptime(date_string,'%Y%m%d')
    start_date = end_date - timedelta(days=2)
   
    df_obs = get_obs(sta_id,start_date,end_date)
    df_pred = get_pred(sta_id,start_date,end_date)
    
    from matplotlib import pyplot as plt
    import seaborn as sns
    
    plt.plot(df_obs['time'],df_obs['twl'],label='Obs')
    plt.plot(df_pred['time'],df_pred['twl'],label='Pred')
    plt.ylabel('Water Level [ft, MLLW]')
    plt.legend()
   








