# -*- coding: utf-8 -*-
# Created 5/1/2017
# Author S. C. Crosby

from datetime import datetime, timedelta
from pytz import timezone
import numpy as np
import os
import urllib2
import time


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
        print 'First download attempt failed, trying 10 more times'       
        for i in range(10):        
            time.sleep(1)        
            try:
                webpage = urllib2.urlopen(grib_url)
                with open(outfile,'w') as fid:
                    temp = webpage.read()
                    fid.write(temp)
                msg = 'working'
                print 'Attempt {:d} {:s}'.format(i,msg)
                break
            except:
                msg = 'failed'
                print 'Attempt {:d} {:s}'.format(i,msg)
                
        if msg == 'failed':
            err_str = 'Grib file not found, url is incorrect. Check url, {:s}'.format(grib_url)    
            with open('Errfile.txt','w') as f:
                f.write(err_str)            
            raise ValueError(err_str)
            


# Small function to load rotations needed for HRDPS
def load_rotations(hrdps_rotation_file,Ny,Nx):
    Theta = np.zeros((Ny,Nx), dtype='d')
    RotationFile = open(hrdps_rotation_file,'r')
    Lines = RotationFile.readlines()
    RotationFile.close()
    for Line in Lines:
        LineSplit = Line.split()
        i = int(LineSplit[0])
        j = int(LineSplit[1])
        Theta[j,i] = -float(LineSplit[2])
    return Theta

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
    
    # Function to find minimum nearest
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
    return (model_time, model_tide)


def tide_exc_prob(t_file, t_level, duration):
    # Function returns probablity that tide will exceed t_level during the duration
    # duration [hours]
    # t_level [m] in NAVD88

    # Load Tide File
    with open(t_file) as fid:
        content = fid.readlines()
    
    # Disregard Header    
    content.pop(0)
     
    # Parse tide data , ignore time
    tide = [float(x.split()[1]) for x in content]
    
    # Estimate probablity of threshold exceedence
    N = len(tide)    
    p_true = 0.
    for t in range(N-duration):
        block = tide[t:t+duration]
        test = [i for i in block if i>t_level]
        if test:
            p_true += 1
            
    prob = p_true/(N-duration)
    
    return prob

    
def read_hrdps_grib(date_string, zulu_hour, param):
    import pygrib
    from pyproj import Proj
    
    # Initialize    
    forecast_count = param['num_forecast_hours'] #Number of forecast hours
    hrdps_lamwest_file = param['hrdps_lamwest_file']
    hrdps_rotation_file = param['hrdps_rotation_file']
    grib_input_loc = '{0:s}/{1:s}{2:s}/'.format(param['fol_wind_grib'],param['folname_grib_prefix'],date_string)
    prefix_uwnd = param['hrdps_PrefixU'] 
    prefix_vwnd = param['hrdps_PrefixV'] 
    bounds = param['crop_bounds']
    
    #----------------------- Load up HRDP Land Mask----------------------------------------
    maskFileName = '{0:s}/{1:s}{2:s}{3:02d}_P000-00.grib2'.format(grib_input_loc, param['hrdps_PrefixLAND'], date_string, zulu_hour)
    grbl = pygrib.open(maskFileName)
    grblL = grbl.select(name='Land-sea mask')[0]
    Land = grblL.values
    Land = np.asarray(Land)
    Ny = np.shape(Land)[0]
    Nx = np.shape(Land)[1]
    Land = Land[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]    # reduce to Salish Sea region
    
    #------------------------------- Load lat/lon positions of hrps ---------------------------------
    degreesLat = np.zeros((Ny,Nx), dtype='d')
    degreesLon = np.zeros((Ny,Nx), dtype='d')
    indexFile = open(hrdps_lamwest_file,'r')
    for line in indexFile:
        split = line.split()
        i = int(split[0])-1
        j = int(split[1])-1
        degreesLat[j,i] = float(split[2])
        degreesLon[j,i] = float(split[3])
    indexFile.close()
    degreesLat = degreesLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    degreesLon = degreesLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    
    #---------------------------- Load rotations---------------------
    Theta = load_rotations(hrdps_rotation_file,Ny,Nx)
    Theta = Theta[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    Nyr = np.shape(Theta)[0]
    Nxr = np.shape(Theta)[1]
    
    
    #--------------------------------------------- UTM ----------------------------------------------
    p = Proj(proj='utm', zone=10, ellps='WGS84')
    X, Y = p(degreesLon, degreesLat)  # note the capital L
    
    
    # ------------ Load in All Forecast Data --------------------------------
    U10 = []
    V10 = []
    for hour in range(forecast_count):
        #Input grib file names            
        UwindFileName = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, prefix_uwnd, date_string, zulu_hour, hour)
        VwindFileName = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, prefix_vwnd, date_string, zulu_hour, hour)
        
        # Open grib
        grbsu = pygrib.open(UwindFileName)
        grbu  = grbsu.select(name='10 metre U wind component')[0]
        grbsv = pygrib.open(VwindFileName)
        grbv  = grbsv.select(name='10 metre V wind component')[0]
        
        u10 = grbu.values # same as grb['values']
        v10 = grbv.values
        u10 = np.asarray(u10)
        v10 = np.asarray(v10)
        
        # Crop
        u10 = u10[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
        v10 = v10[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
        
        
        # Rotate to earth relative with Bert-Derived rotations based on grid poitns (increased accuracy was derived for grid locations)
        for j in range(Nyr):
            for i in range(Nxr):
                R = np.matrix([ [np.cos(Theta[j,i]), -np.sin(Theta[j,i])], [np.sin(Theta[j,i]), np.cos(Theta[j,i])] ])
                rot = R.dot([u10[j,i],v10[j,i]])
                u10[j,i] = rot[0,0]
                v10[j,i] = rot[0,1]
        
        # Save all varaibles into list of arrays        
        U10.append(u10)
        V10.append(v10)
    
    return (X, Y, U10, V10)


if __name__ == '__main__':    
    import get_param
    import matplotlib.pyplot as plt
    (date_string, zulu_hour) = latest_hrdps_forecast()
    param = get_param.get_param_bbay()    
    (model_time, model_tide) = get_tides(date_string, zulu_hour, param)
    
    plt.plot(model_time,model_tide)
    plt.show()
    plt.close()
    
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

