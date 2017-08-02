#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 15:20:43 2017

@author: nvanarendonk
"""
import urllib2
import StringIO
import gzip
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

import op_functions



def get_ncdc_met(USAF, WBAN, Year, num_hours, St_name):

    # NOTE: PUT EVERYTHING ABOVE IN QUOTES, MUST BE STRINGS FOR INPUT VARIABLES

    # USAF: USAF number for station
    # WBAN: WBAN number for station
    # Year: Year of data retreival
    # NumHours: Number of hours in the past you want to go 
    # St_name: Station Name - Bham_Airport.txt for example

    # ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.txt search for other stations >> to view station list
       
    # Base URL
    URL = 'ftp://ftp.ncdc.noaa.gov/pub/data/noaa/'   
    # Concatenate the URL and Year                          
    URL = URL + Year + '/'                                                     
    
    # Genearte the File Name
    filename = USAF + '-' + WBAN + '-' + Year + '.gz'   
    # Get rid of file extension                       
    outFilename = filename[:-3]

    response = urllib2.urlopen(URL + filename) # access FTP
    compressedFile = StringIO.StringIO(response.read()) # Grab the file contents
    decompressedFile = gzip.GzipFile(fileobj=compressedFile) # Decompress
       
    # Write contents to outfile
    with open(outFilename, 'w') as outfile:  # Write contents to outfile
        outfile.write(decompressedFile.read())
           
    # Run the parsing of the data using the Java files ,saves to file
    #------ java -classpath . ishJava <input filename> <output filename> ------FOR WINDOWS, I BELIEVE IT IS THE SAME    
    save_file = St_name + '.txt'
    str_txt = 'java -classpath . ishJava' + ' ' + filename[:-3] + ' ' + save_file   
    os.system(str_txt)
    os.remove(outFilename)  # Deletes the unnecessary file
    
  
    # Parse to variables    
    wndspd = np.zeros(num_hours)
    wnddir = np.zeros(num_hours)  
    time = []
    with open(save_file, 'r') as f:
        next(f) # Skip header
        for i in range(num_hours):
            row = next(f)

            temp = row[13:25]
            time.append(datetime.strptime(temp,r'%Y%m%d%H%M'))

            if '*' in row[26:29]:
                wnddir[i] = 'NaN'
            else:
                wnddir[i] = int(row[26:29])
                if wnddir[i] > 360 or wnddir[i] < 0:
                    wnddir[i] = 'NaN'
                
            if '*' in row[30:33]:
                wndspd[i] = 'NaN'
            else:                               
                wndspd[i] = int(row[30:33])
                
    # Convert local time to UTC
    gmt2pst = op_functions.get_gmt_offset_2()
    time = [t-timedelta(hours=gmt2pst) for t in time]    
  
    return (time, wndspd, wnddir)        

    
# Use for testing/debugging        
if __name__ == '__main__':
    usaf = '727976'
    wban = '24217'
    year = '2017'
    hours = 48
    sta_name = 'bham_air'
    
    (date_time, wndspd, wnddir) = get_ncdc_met(usaf, wban, year, hours, sta_name)

    # plot wndspd
    plt.subplot(211)
    plt.plot(date_time,wndspd)
    plt.gcf().autofmt_xdate()
    plt.show()
    
    # plot wnddir
    plt.subplot(212)
    plt.plot(date_time,wnddir)
    plt.gcf().autofmt_xdate()
    plt.show()




