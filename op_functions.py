# -*- coding: utf-8 -*-
# Created 5/1/2017
# Author S. C. Crosby

from datetime import datetime, timedelta
from pytz import timezone
import os
import urllib2

# Function returns current offset to PST/PDT (8 or 7 hours)
def get_gmt_offset():
    pdt = timezone('US/Pacific')
    nowUTC = datetime.utcnow()
    nowPDT = datetime.now(pdt)
    nowUTCCorrected = datetime(int(nowUTC.year), int(nowUTC.month), int(nowUTC.day), 
                               int(nowUTC.hour), int(nowUTC.minute), 
                                int(nowUTC.second))
    nowPDTCorrected = datetime(int(nowPDT.year), int(nowPDT.month), 
                               int(nowPDT.day), int(nowPDT.hour), int(nowPDT.minute), 
                                int(nowPDT.second))
    diff_time = nowUTCCorrected - nowPDTCorrected
    diff_hour = int(round(diff_time.seconds/3600))
    return diff_hour

# Returns GMT offset to PST/PDT 
def get_gmt_offset_2():
    # Works through 2019, HARDCODED
    myTime = datetime.utcnow()
    if datetime(2015,3,8,2,0,0) < myTime < datetime(2015,11,1,2,0,0):
        GMT2PST = 7 #hr
    elif datetime(2016,3,13,2,0,0) < myTime < datetime(2016,11,6,2,0,0):
        GMT2PST = 7 #hr
    elif datetime(2017,3,12,2,0,0) < myTime < datetime(2017,11,5,2,0,0):
        GMT2PST = 7 #hr
    elif datetime(2018,3,11,2,0,0) < myTime < datetime(2018,11,4,2,0,0):
        GMT2PST = 7 #hr
    elif datetime(2019,3,10,2,0,0) < myTime < datetime(2019,11,3,2,0,0):
        GMT2PST = 7 #hr
    else:
        GMT2PST = 8 #hr
    return GMT2PST


# Function download winds & pressure from Canada HRDPS predictions
def get_hrdps(date_string, zulu_hour, param):
    
    #Set Static Variables
    num_forecast_hours = param['num_forecast_hours']
    gribPrefixP = param['hrdps_PrefixP']
    gribPrefixU = param['hrdps_PrefixU']
    gribPrefixV = param['hrdps_PrefixV']
    gribPrefixLAND = param['hrdps_PrefixLAND']
    url = param['hrdps_url']
    
    # Set folder for downloads
    loc_output = '{0:s}/{1:s}{2:s}'.format(param['fol_wind_grib'],param['folname_grib_prefix'],date_string)
  
    # Create datestring
    # dateString  = date_requested.strftime('%Y%m%d')
    
  
    # Make output folder if neccessary
    if os.path.exists(loc_output):
    	temp=0#print('Folder \'{0:s}\' exists.'.format(loc_output))
    else:
        os.mkdir(loc_output)
    
    # Dowload land mask?
    download_grib(gribPrefixLAND, url, date_string, zulu_hour, 0, loc_output)
         
    # Download grib files
    for hour in range(num_forecast_hours): 
    	print 'Dowloading hrdps forecast hour %02d' % hour
        # Pressure (prtmsl)    
        download_grib(gribPrefixP, url, date_string, zulu_hour, hour, loc_output)      
        # U wind    
        download_grib(gribPrefixU, url, date_string, zulu_hour, hour, loc_output)       
        # V wind    
        download_grib(gribPrefixV, url, date_string, zulu_hour, hour, loc_output)
 
# Function downloads grib file
#   Used by get_hrdps()
def download_grib(gribPrefixP, url, dateString, zulu_hour, forecast_hour, loc_output):
    # Set name and creat URL
    grib_name = '%s%s%02d_P%03d-00.grib2' % (gribPrefixP, dateString, zulu_hour, forecast_hour)
    grib_url = '%s/%02d/%03d/%s' % (url, zulu_hour, forecast_hour, grib_name)

    # Download file to folder specified, throw error if not found
    outfile = '%s/%s' % (loc_output,grib_name)
    try:
        webpage = urllib2.urlopen(grib_url)
        with open(outfile,'w') as fid:
            temp = webpage.read()
            fid.write(temp)
    except:
        err_str = 'Grib file not found, url incorrect, trying %s' % grib_url
        raise ValueError(err_str)
   

# Find latest files available for Canada HRDPS
def latest_hrdps_forecast():
	# Set static string and format
    gribPrefix = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_'
    forecastHr = 48
	
    # Try today and yesterday
    for ndy in [0,-1]:
        NowUTC = datetime.utcnow() + timedelta(days=ndy)
        dateString = NowUTC.strftime('%Y%m%d')
		
		# Try most recent forecast first, then go backwards
        for runStart in [18,12,6,0]:
            gribName = '{0:s}{1:s}{2:02d}_P{3:03d}-00.grib2'.format(gribPrefix, dateString, runStart, forecastHr)
            gribUrl   = 'http://dd.weather.gc.ca/model_hrdps/west/grib2/{0:02d}/{1:03d}/{2:s}'.format(runStart, forecastHr, gribName)
            #print(gribUrl)
            
            # See if file exists, if so return, otherwise loop
            try:
            	   urllib2.urlopen(gribUrl)
            	   forecastHour = runStart
            	   return dateString, forecastHour
            except:
                print('48 hour file doesn\'t exist yet for {0:s}, {1:02d}Z\n'.format(dateString, runStart)),

    #If no files found return null
    dateString = 'null'
    forecastHour = 'null'
    return dateString, forecastHour


def get_tides(datestring, zulu_hour, param):   
    # NULL vars ignored
    
    # Functoin to find minimum nearest
    def nearest(items, pivot):
        return min(items, key=lambda x: abs(x - pivot))
    
    # Load Tide File
    with open(param['tide_file']) as fid:
        content = fid.readlines()
    
    # Disregard Header    
    content.pop(0)
    
    # Format of time data
    t_format = '%Y-%m-%d-%H-%M-%S'
    
    # Parse time and tide data 
    time = [datetime.strptime(x.split()[0],t_format) for x in content]    
    tide = [float(x.split()[1]) for x in content]

    # Format input date
    temp = '%s%02d' % (datestring, zulu_hour)
    time_forecast =  datetime.strptime(temp,'%Y%m%d%H')
    
    # Find index for requested time
    time_nearest = nearest(time,time_forecast)
    idx = time.index(time_nearest)
    
    # Return 48-hour forecast of tides
    model_time = time[idx:idx+param['num_forecast_hours']]
    model_tide = tide[idx:idx+param['num_forecast_hours']]
    
    return model_tide    
    
#    # Convert to Local Time
#    model_time = [x-timedelta(hours=timeDifference) for x in model_time ]
#    
    # Write latest tide time file
#    fname = 'D:\EG_WORK\Skagit_OperationalModel\pythonscripting\CANADA\Tide_data_canada\latest_tide_time.txt'
#    out_contents = '%s   %02d' % (datestring, forecast_hour)
#    with open(fname,'w') as fid:
#        fid.write(out_contents)
    
    # Write 48-hour tide file
#    fol_loc = r'D:/EG_WORK/Skagit_OperationalModel/pythonscripting/CANADA/Tide_data_canada'
#    fname = '%s/tide_forecast_%s_%02dZ.txt' % (fol_loc, datestring, forecast_hour)
#    #print fname
#    with open(fname,'w') as fid:
#        for x,y in zip(model_time,model_tide):
#            fid.write('%s  %5.3f\n' % (x.strftime('%Y-%m-%d %H:%M:%S'),y))

    # Return 48-hour tide forecast

