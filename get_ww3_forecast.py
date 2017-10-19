#% Download at buoy site: 48087
#% ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/wave/prod/multi_1.20171016/
#% http://polar.ncep.noaa.gov/waves/viewer.shtml?-multi_1-US_wc_zm1-
#
#% File of interest multi_1.46078.spec

import os
import urllib2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


# Download data to file first
#url = 'http://www.ndbc.noaa.gov/data/realtime2/{:s}.txt'.format(station_id)
#open('data.txt','wb').write(urllib.urlopen(url).read())

date_string = '20171016'
zulu_hour = 6

url = 'ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/wave/prod/multi_1.{:s}/'.format(date_string)

fname = 'enp.t{:02d}z.spec_tar.gz'.format(zulu_hour)

print url + fname


# Save Location
'../Data/downloads/noaa_ww3/

outfile = 'test.tar.gz'

#webpage = urllib2.urlopen(url + fname)

try:
    webpage = urllib2.urlopen(url + fname)
    with open(outfile,'w') as fid:
        temp = webpage.read()
        fid.write(temp)
except:
    print 'no'

#%%


#def download_grib(gribPrefixP, url, dateString, zulu_hour, forecast_hour, loc_output):
#    # Set name and creat URL
#    grib_name = '%s%s%02d_P%03d-00.grib2' % (gribPrefixP, dateString, zulu_hour, forecast_hour)
#    grib_url = '%s/%02d/%03d/%s' % (url, zulu_hour, forecast_hour, grib_name)
#
#    # Download file to folder specified, throw error if not found
#    outfile = '%s/%s' % (loc_output,grib_name)
#    try:
#        webpage = urllib2.urlopen(grib_url)
#        with open(outfile,'w') as fid:
#            temp = webpage.read()
#            fid.write(temp)
#    except:
#        print 'First download attempt failed, trying 10 more times'       
#        for i in range(10):        
#            time.sleep(1)        
#            try:
#                webpage = urllib2.urlopen(grib_url)
#                with open(outfile,'w') as fid:
#                    temp = webpage.read()
#                    fid.write(temp)
#                msg = 'working'
#                print 'Attempt {:d} {:s}'.format(i,msg)
#                break
#            except:
#                msg = 'failed'
#                print 'Attempt {:d} {:s}'.format(i,msg)
#                
#        if msg == 'failed':
#            err_str = 'Grib file not found, url is incorrect. Check url, {:s}'.format(grib_url)
#            raise ValueError(err_str)
#
# Read in and parse lastest num_hours
#num_lines = num_hours
#time = []
#direction = np.zeros(num_lines)
#speed = np.zeros(num_lines)
#slp = np.zeros(num_lines)
#with open('data.txt', 'r') as f:
#    next(f) # Skip two header lines
#    next(f)
#    for i in range(num_lines):
#        line = f.next().split()
#        time.append(datetime(int(line[0]),int(line[1]),int(line[2]),int(line[3]),int(line[4])))
#        if line[5] == 'MM':
#            direction[i] = float('NaN')      
#            speed[i] = float('NaN')
#        else:    
#            direction[i] = int(line[5])        
#            speed[i] = ms2mph*float(line[6])
#        slp[i] = float(line[12])/10 
#
#
#
#
#Availabel buoys
#enp.46001.spec  enp.46041.spec  enp.46205.spec   enp.CDIP12.spec  enp.HNL52.spec   enp.OPCP04.spec
#enp.46002.spec  enp.46042.spec  enp.46206.spec   enp.CDIP13.spec  enp.HNL53.spec   enp.OPCP05.spec
#enp.46004.spec  enp.46047.spec  enp.46207.spec   enp.CDIP14.spec  enp.HNL54.spec   enp.OPCP06.spec
#enp.46005.spec  enp.46050.spec  enp.46208.spec   enp.CDIP15.spec  enp.HNL55.spec   enp.OPCP07.spec
#enp.46006.spec  enp.46053.spec  enp.51001.spec   enp.CDIP16.spec  enp.HNL56.spec   enp.OPCP08.spec
#enp.46011.spec  enp.46054.spec  enp.51002.spec   enp.CDIP17.spec  enp.HNL57.spec   enp.OPCP09.spec
#enp.46012.spec  enp.46059.spec  enp.51003.spec   enp.CDIP18.spec  enp.HNL58.spec   enp.OPCP10.spec
#enp.46013.spec  enp.46062.spec  enp.51004.spec   enp.CDIP19.spec  enp.HNL59.spec   enp.OPCP11.spec
#enp.46014.spec  enp.46063.spec  enp.CDIP01.spec  enp.CDIP20.spec  enp.HNL61.spec   enp.OPCP12.spec
#enp.46015.spec  enp.46066.spec  enp.CDIP02.spec  enp.CDIP21.spec  enp.HNL62.spec   enp.OPCP13.spec
#enp.46022.spec  enp.46080.spec  enp.CDIP03.spec  enp.CDIP22.spec  enp.HNL63.spec   enp.SGX01.spec
#enp.46023.spec  enp.46082.spec  enp.CDIP04.spec  enp.CDIP23.spec  enp.HNL64.spec   enp.t12z.spec_tar.gz
#enp.46025.spec  enp.46083.spec  enp.CDIP05.spec  enp.CDIP24.spec  enp.HNL65.spec   enp.TPC50.spec
#enp.46026.spec  enp.46084.spec  enp.CDIP06.spec  enp.HNL01.spec   enp.HNL66.spec   enp.TPC51.spec
#enp.46027.spec  enp.46086.spec  enp.CDIP07.spec  enp.HNL02.spec   enp.HNL67.spec   enp.TPC52.spec
#enp.46028.spec  enp.46087.spec  enp.CDIP08.spec  enp.HNL10.spec   enp.HNL68.spec   enp.TPC53.spec
#enp.46029.spec  enp.46089.spec  enp.CDIP09.spec  enp.HNL11.spec   enp.OPCP01.spec  enp.TPC54.spec
#enp.46030.spec  enp.46132.spec  enp.CDIP10.spec  enp.HNL12.spec   enp.OPCP02.spec  enp.TPC55.spec
#enp.46036.spec  enp.46184.spec  enp.CDIP11.spec  enp.HNL51.spec   enp.OPCP03.spec  enp.TPC56.spec