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
from shutil import copy2, rmtree
from datetime import datetime, timedelta
from pytz import timezone
import matplotlib
import matplotlib.pyplot as plt



def getFTP(USAF, WBAN, Year, NumHours, St_name):

    # NOTE: PUT EVERYTHING ABOVE IN QUOTES, MUST BE STRINGS FOR INPUT VARIABLES

    # USAF: USAF number for station
    # WBAN: WBAN number for station
    # Year: Year of data retreival
    # NumHours: Number of hours in the past you want to go 
    # St_name: Station Name - Bham_Airport.txt for example

    # ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.txt search for other stations >> to view station list
    
###############################################################################
    
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
    
###############################################################################
    
    # Write contents to outfile
    with open(outFilename, 'w') as outfile:  # Write contents to outfile
        outfile.write(decompressedFile.read())
        
    # Current Directory    
    cdir = os.getcwd()

    # Make a folder to house the files needed
    os.mkdir(St_name)
    # Copy necessary files into that directory
    copy2('ishJava.java', cdir + '/' + St_name)
    copy2('ishJava.class', cdir + '/' + St_name)
    copy2(outFilename, cdir + '/' + St_name)
    
    # Change into that directory
    os.chdir(cdir + '/' + St_name)
    
    # Run the parsing of the data using the Java files
    #------ java -classpath . ishJava <input filename> <output filename> ------FOR WINDOWS, I BELIEVE IT IS THE SAME    
    str_txt = 'java -classpath . ishJava' + ' ' + filename[:-3] + ' ' + St_name + '.txt'
    os.system(str_txt)
    
    os.remove(outFilename)  # Deletes the unnecessary file
    os.remove('ishJava.java')  # Deletes the unnecessary file
    os.remove('ishJava.class')  # Deletes the unnecessary file
   
###############################################################################

# Go Through the parsed data and grab the date, speed and direction and write it to a file
    
    
    inputfile = open(St_name + '.txt', 'r') # Open in read mode
    outputfile = open(St_name + '_F1.txt', 'w') # Create file and open in write mode, F1 stands for Format Round 1
    
    for row in inputfile:
        dataWant = row[13:34] # Grab the data that I want
        outputfile.write(dataWant+'\n') # Add it to the newly created file 

    inputfile.close()  # Close files up
    outputfile.close()
    
###############################################################################

    # Convert to Datetime format
    
    #curDate = datetime.now().strftime('%Y-%m-%d %H:%M')  # Current Date
    curDateInt = datetime.now()  # Datetime obj integer
    station_data = [] # Create empty list
    format = '%Y-%m-%d %H:%M'  # Format for datetime object


    # Taken from op_functions.py
    pdt = timezone('US/Pacific') # establish time zone
    nowUTC = datetime.utcnow() # Grab current time in UTC
    nowPDT = datetime.now(pdt) # grab current time
    nowUTCCorrected = datetime(int(nowUTC.year), int(nowUTC.month), int(nowUTC.day), 
                               int(nowUTC.hour), int(nowUTC.minute))
    nowPDTCorrected = datetime(int(nowPDT.year), int(nowPDT.month), 
                               int(nowPDT.day), int(nowPDT.hour), int(nowPDT.minute))
    diff_time = nowUTCCorrected - nowPDTCorrected
    diff_hour = int(round(diff_time.seconds/3600))
    # diff_hour tells me that there are currently 7 hours of difference between PDT and UTC
    
   
    d = curDateInt - timedelta(hours = NumHours)  # Find date of interest
    d_utc = d + timedelta(hours = diff_hour) # find UTC time of interest
    
    d = str(d) # Convert to a string
    d_utc = str(d_utc)
    
    d = d[:13] # Grab the values that correspond to data in text files
    d_utc = d_utc[:13] # This is the 'IN THE PAST' UTC date limit
    

    with open(St_name + '_F1.txt', 'r') as f:   # Open up the text file to format
        next(f) # skips header
        for line in f:  # Iterate through it
        # Format Data for Date to get in YYYY-MO-DA HR:MN 
            grabData = line[:4] + '-' + line[4:6] + '-' + line[6:8] + ' ' + line[8:10] + ':' + line[10:12] + ' ' + line[13:16] + ' ' + line[18:20]
            #grabData has all of the data that I need in it
            dt = grabData[:16] # Grab just the date  
            dateNaive = datetime.strptime(dt, format)  # Create a naive datetime object
            dateUTC = str(dateNaive + timedelta(hours = diff_hour)) # find the UTC time
            dateUTC = dateUTC[:13]
            if dateUTC > d_utc: # if the current date is greater than the farthest back date the User Defines
                station_data.append(grabData)  
            else:
                continue
            
    f.close()
    os.remove(St_name + '.txt') # Get rid of unneeded files
    os.chdir('../') # Move back a directory
    os.remove(filename[:-3]) # Remove raw data file
    os.chdir(St_name)
  
###############################################################################
    

    # create empty list
    wndspd = []
    wnddir = []
    date_time = []
    date_num = []
    
    for x in station_data: 
        
        # Grab wind direction and get rid of NaNs
        direc = x[17:20]
        if '*' in direc or direc == '990':
            wnddir.append('NaN') 
        else:
            wnddir.append(int(direc))
        
        # Grab wind speed and get rid of NaNs
        spd = x[21:23]
        if '*' in spd:
            wndspd.append('NaN') 
        else:
            wndspd.append(int(spd))
   
        date = x[:16]
        date_obj = datetime.strptime(date, format)
        date = date_obj + timedelta(hours = diff_hour)
        dateNum = matplotlib.dates.date2num(date)
        #date = str(date)
        date_time.append(date)
        date_num.append(dateNum)
    
    # Convert to tuples
    wndspd = tuple(wndspd)
    wnddir = tuple(wnddir)
    date_time = tuple(date_time)
    date_num = tuple(date_num)

    os.chdir('../') # change directory
    rmtree(St_name) #Delete File   
    
##    # plot wndspd
##    plt.plot(date_time,wndspd)
##    # beautify the x-labels
##    plt.gcf().autofmt_xdate()
##    plt.show()
##    
##    # plot
##    plt.plot(date_num,wnddir)
##    # beautify the x-labels
##    plt.gcf().autofmt_xdate()
##    plt.show()

    return wnddir
    return wndspd
    return date_time
    return date_num    
    
##usaf = '727976'
##wban = '24217'
##year = '2017'
##hours = 48
##St_name = 'bham_air'
##
##getFTP(usaf, wban, year, hours, St_name)






Contact GitHub API Training Shop Blog About
© 2017 GitHub, Inc. Terms Privacy Security Status Help#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 15:20:43 2017
@author: nvanarendonk
"""
import urllib2
import StringIO
import gzip
import os
from shutil import copy2, rmtree
from datetime import datetime, timedelta
from pytz import timezone
import matplotlib
import matplotlib.pyplot as plt



def getFTP(USAF, WBAN, Year, NumHours, St_name):

    # NOTE: PUT EVERYTHING ABOVE IN QUOTES, MUST BE STRINGS FOR INPUT VARIABLES

    # USAF: USAF number for station
    # WBAN: WBAN number for station
    # Year: Year of data retreival
    # NumHours: Number of hours in the past you want to go 
    # St_name: Station Name - Bham_Airport.txt for example

    # ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.txt search for other stations >> to view station list
    
###############################################################################
    
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
    
###############################################################################
    
    # Write contents to outfile
    with open(outFilename, 'w') as outfile:  # Write contents to outfile
        outfile.write(decompressedFile.read())
        
    # Current Directory    
    cdir = os.getcwd()

    # Make a folder to house the files needed
    os.mkdir(St_name)
    # Copy necessary files into that directory
    copy2('ishJava.java', cdir + '/' + St_name)
    copy2('ishJava.class', cdir + '/' + St_name)
    copy2(outFilename, cdir + '/' + St_name)
    
    # Change into that directory
    os.chdir(cdir + '/' + St_name)
    
    # Run the parsing of the data using the Java files
    #------ java -classpath . ishJava <input filename> <output filename> ------FOR WINDOWS, I BELIEVE IT IS THE SAME    
    str_txt = 'java -classpath . ishJava' + ' ' + filename[:-3] + ' ' + St_name + '.txt'
    os.system(str_txt)
    
    os.remove(outFilename)  # Deletes the unnecessary file
    os.remove('ishJava.java')  # Deletes the unnecessary file
    os.remove('ishJava.class')  # Deletes the unnecessary file
   
###############################################################################

# Go Through the parsed data and grab the date, speed and direction and write it to a file
    
    
    inputfile = open(St_name + '.txt', 'r') # Open in read mode
    outputfile = open(St_name + '_F1.txt', 'w') # Create file and open in write mode, F1 stands for Format Round 1
    
    for row in inputfile:
        dataWant = row[13:34] # Grab the data that I want
        outputfile.write(dataWant+'\n') # Add it to the newly created file 

    inputfile.close()  # Close files up
    outputfile.close()
    
###############################################################################

    # Convert to Datetime format
    
    #curDate = datetime.now().strftime('%Y-%m-%d %H:%M')  # Current Date
    curDateInt = datetime.now()  # Datetime obj integer
    station_data = [] # Create empty list
    format = '%Y-%m-%d %H:%M'  # Format for datetime object


    # Taken from op_functions.py
    pdt = timezone('US/Pacific') # establish time zone
    nowUTC = datetime.utcnow() # Grab current time in UTC
    nowPDT = datetime.now(pdt) # grab current time
    nowUTCCorrected = datetime(int(nowUTC.year), int(nowUTC.month), int(nowUTC.day), 
                               int(nowUTC.hour), int(nowUTC.minute))
    nowPDTCorrected = datetime(int(nowPDT.year), int(nowPDT.month), 
                               int(nowPDT.day), int(nowPDT.hour), int(nowPDT.minute))
    diff_time = nowUTCCorrected - nowPDTCorrected
    diff_hour = int(round(diff_time.seconds/3600))
    # diff_hour tells me that there are currently 7 hours of difference between PDT and UTC
    
   
    d = curDateInt - timedelta(hours = NumHours)  # Find date of interest
    d_utc = d + timedelta(hours = diff_hour) # find UTC time of interest
    
    d = str(d) # Convert to a string
    d_utc = str(d_utc)
    
    d = d[:13] # Grab the values that correspond to data in text files
    d_utc = d_utc[:13] # This is the 'IN THE PAST' UTC date limit
    

    with open(St_name + '_F1.txt', 'r') as f:   # Open up the text file to format
        next(f) # skips header
        for line in f:  # Iterate through it
        # Format Data for Date to get in YYYY-MO-DA HR:MN 
            grabData = line[:4] + '-' + line[4:6] + '-' + line[6:8] + ' ' + line[8:10] + ':' + line[10:12] + ' ' + line[13:16] + ' ' + line[18:20]
            #grabData has all of the data that I need in it
            dt = grabData[:16] # Grab just the date  
            dateNaive = datetime.strptime(dt, format)  # Create a naive datetime object
            dateUTC = str(dateNaive + timedelta(hours = diff_hour)) # find the UTC time
            dateUTC = dateUTC[:13]
            if dateUTC > d_utc: # if the current date is greater than the farthest back date the User Defines
                station_data.append(grabData)  
            else:
                continue
            
    f.close()
    os.remove(St_name + '.txt') # Get rid of unneeded files
    os.chdir('../') # Move back a directory
    os.remove(filename[:-3]) # Remove raw data file
    os.chdir(St_name)
  
###############################################################################
    

    # create empty list
    wndspd = []
    wnddir = []
    date_time = []
    date_num = []
    
    for x in station_data: 
        
        # Grab wind direction and get rid of NaNs
        direc = x[17:20]
        if '*' in direc or direc == '990':
            wnddir.append('NaN') 
        else:
            wnddir.append(int(direc))
        
        # Grab wind speed and get rid of NaNs
        spd = x[21:23]
        if '*' in spd:
            wndspd.append('NaN') 
        else:
            wndspd.append(int(spd))
   
        date = x[:16]
        date_obj = datetime.strptime(date, format)
        date = date_obj + timedelta(hours = diff_hour)
        dateNum = matplotlib.dates.date2num(date)
        #date = str(date)
        date_time.append(date)
        date_num.append(dateNum)
    
    # Convert to tuples
    wndspd = tuple(wndspd)
    wnddir = tuple(wnddir)
    date_time = tuple(date_time)
    date_num = tuple(date_num)

    os.chdir('../') # change directory
    rmtree(St_name) #Delete File   
    
##    # plot wndspd
##    plt.plot(date_time,wndspd)
##    # beautify the x-labels
##    plt.gcf().autofmt_xdate()
##    plt.show()
##    
##    # plot
##    plt.plot(date_num,wnddir)
##    # beautify the x-labels
##    plt.gcf().autofmt_xdate()
##    plt.show()

    return wnddir
    return wndspd
    return date_time
    return date_num    
    
##usaf = '727976'
##wban = '24217'
##year = '2017'
##hours = 48
##St_name = 'bham_air'
##
##getFTP(usaf, wban, year, hours, St_name)



