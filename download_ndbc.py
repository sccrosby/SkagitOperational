# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 13:06:02 2017

@author: crosby
"""

import os
import urllib
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def get_ndbc_realtime(station_id,num_hours):
# Returns time, speed [m/s], direction [deg], and pressure [kPa]
    ms2mph = 2.237  
    
    # Download data to file first
    url = 'http://www.ndbc.noaa.gov/data/realtime2/{:s}.txt'.format(station_id)
    open('data.txt','wb').write(urllib.urlopen(url).read())
    
    # Read in and parse lastest num_hours
    num_lines = num_hours
    time = []
    direction = np.zeros(num_lines)
    speed = np.zeros(num_lines)
    slp = np.zeros(num_lines)
    with open('data.txt', 'r') as f:
        next(f) # Skip two header lines
        next(f)
        for i in range(num_lines):
            line = f.next().split()
            time.append(datetime(int(line[0]),int(line[1]),int(line[2]),int(line[3]),int(line[4])))
            if line[5] == 'MM':
                direction[i] = float('NaN')      
                speed[i] = float('NaN')
            else:    
                direction[i] = int(line[5])        
                speed[i] = ms2mph*float(line[6])
            slp[i] = float(line[12])/10 
    
    # Delete data file
    # os.remove('data.txt')
    
    return (time,speed,direction,slp)


# Test setup for testing        
if __name__ == '__main__':
    station_id = '46118'
    (time,speed,direction,slp) = get_ndbc_realtime(station_id,48)        
    plt.subplot(311)        
    plt.plot(time,speed)
    plt.subplot(312)        
    plt.plot(time,direction)
    plt.subplot(313)        
    plt.plot(time,slp)
    plt.show()
    plt.close()

#
#webpage=str(urllib.urlopen(url).read())
#soup = bs4.BeautifulSoup(webpage,'lxml')
#
#print soup.get_text()
#
