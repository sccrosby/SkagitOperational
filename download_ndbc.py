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

# Functions returns time (UTC), speed (m/s), and direction (deg)
def get_ndbc_realtime(station_id):
    # Download data to file first
    url = 'http://www.ndbc.noaa.gov/data/realtime2/{:s}.txt'.format(station_id)
    open('data.txt','wb').write(urllib.urlopen(url).read())
    
    # Read in and parse lastest 48 data points
    num_lines = 48
    time = []
    direction = np.zeros(num_lines)
    speed = np.zeros(num_lines)
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
                speed[i] = float(line[6])
    
    # Delete data file
    os.remove('data.txt')
    
    return (time,speed,direction)


# Test setup for testing        
if __name__ == '__main__':
    station_id = '46118'
    (time,speed,direction) = get_ndbc_realtime(station_id)        
    plt.subplot(211)        
    plt.plot(time,speed)
    plt.subplot(212)        
    plt.plot(time,direction)
    plt.show()
    plt.close()

#
#webpage=str(urllib.urlopen(url).read())
#soup = bs4.BeautifulSoup(webpage,'lxml')
#
#print soup.get_text()
#
