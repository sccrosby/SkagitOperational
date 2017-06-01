import numpy as np
import os
import subprocess
from datetime import datetime, timedelta
from pytz import timezone
"""
Subfolders
    downloaded_grib_files   or  All_Grib_Files
    cropped_wind_data
    Wind
    Wind/bin/linux
    XBeach
"""
from fetch_data import fetch
from seek_latest_canadian_data import find_latest_canadian_data, fetch_canadian                              # download current grib files for analysis and forecast
from SkagitDelta import Skagit_crop, Skagit_plot    
from SkagitDeltaCanada import Skagit_crop_canada, Skagit_plot_canada        # extract winds from grib files, crop, and store in ASCII format
from irregular_to_regular import regrid, regrid_plot      # Interpolate wind data onto Delft curvilinear grid.
from irregular_to_regular_canada import regrid_canada, regrid_plot_canada      # Interpolate wind data onto Delft curvilinear grid.
from NOAA import getTides, getTides_canada
from write_mdwFile import mdw, locations, parameters
from write_mdwFile_canada import mdw_canada
from split_sp2_files import split_spectrum
#from gm_montage import montage_regular, montage_lcc, montage_rose
runningPath = 'C:/Users/ahooshmand/Desktop/Bellingham/pythonscripting/'
windDataSource = 'CANADA' #CANADA
latMin = 48.2
latMax = 48.55
lonMin = -122.7
lonMax = -122.30
mllw2NAVD88 = 0.615 #m
Nlocations = 3
NOW = True
Resolution = 2.5  # or 5.0
grid_number = 3 # which grid to use
fileCount = 48
start = 0       # Select a number from 0 to 18 for a starting point for 6-hour run.
gribPrefixPressure = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' #Canadian pressure data
gribPrefixU = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
gribPrefixV = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
pdt = timezone('US/Pacific')
nowUTC = datetime.utcnow()
nowPDT = datetime.now(pdt)
nowUTCCorrected = datetime(int(nowUTC.year), int(nowUTC.month), int(nowUTC.day), 
                           int(nowUTC.hour), int(nowUTC.minute), 
                            int(nowUTC.second))
nowPDTCorrected = datetime(int(nowPDT.year), int(nowPDT.month), 
                           int(nowPDT.day), int(nowPDT.hour), int(nowPDT.minute), 
                            int(nowPDT.second))
timeDiff = nowUTCCorrected - nowPDTCorrected
GMT2PST = int(round(timeDiff.seconds/3600))
os.chdir(runningPath)
if NOW:
    pdt = timezone('US/Pacific')
    day_of_year = datetime.now(pdt).timetuple().tm_yday     # optionally use utcnow()
    print(datetime.now(pdt).strftime('%y/%m/%d %H:%M:%S'))
    dateString  = datetime.now(pdt).strftime('%Y%m%d')         
    folder = 'downloaded_grib_files/downloaded_grib_files_{0:s}'.format(dateString)
    hyphenatedString = datetime.now(pdt).strftime('%Y-%m-%d')
    #hyphenatedString = (datetime.now(pdt) - timedelta(days=1)).strftime('%Y-%m-%d')
else:
    dateString = '20150829'
    hyphenatedString = '2015-08-09'
    day_of_year = 241
    folder = 'All_Grib_Files'
print(day_of_year, dateString)
if windDataSource == 'USA':
    fileCount = fetch(Resolution, dateString)
elif windDataSource == 'CANADA':
    dateStringCanada, utcCanada = find_latest_canadian_data(gribPrefixPressure)
    fileCount = fetch_canadian(gribPrefixPressure, dateString, dateStringCanada, utcCanada)
    fileCount = fetch_canadian(gribPrefixU, dateString, dateStringCanada, utcCanada)
    fileCount = fetch_canadian(gribPrefixV, dateString, dateStringCanada, utcCanada)
print('{0:d} files downloaded'.format(fileCount))
if windDataSource == 'USA':
    maxWind,Nx,Ny,meanMax = Skagit_crop(day_of_year, dateString, folder, 
                                        Resolution, fileCount, latMin, latMax, 
                                        lonMin, lonMax)
    Skagit_plot(day_of_year, dateString, folder, Resolution, fileCount, maxWind, Nx, Ny)
elif windDataSource == 'CANADA':
    maxWind,Nx,Ny,meanMax = Skagit_crop_canada(dateString, dateStringCanada, 
                                               utcCanada, fileCount, latMin, 
                                               latMax, lonMin, lonMax, 
                                               gribPrefixU, gribPrefixV)
    Skagit_plot_canada(dateString, dateStringCanada, utcCanada, fileCount, maxWind, Nx, Ny, GMT2PST)
# #
print('Max wind: {0:4f}, hour of maximum mean area wind: {1:2d}'.format(maxWind,meanMax))

#if fileCount == 24:
#    montage_lcc(day_of_year, fileCount)
if windDataSource == 'USA':
    maxWindWrong, meanMaxWrong = regrid(Resolution, dateString, day_of_year, hyphenatedString, fileCount)
    print('Max wind: {0:4f}, hour of maximum mean local wind: {1:2d}'.format(maxWind,meanMax))
    regrid_plot(Resolution, dateString, day_of_year, hyphenatedString, fileCount, maxWind)
elif windDataSource == 'CANADA':
    maxWindWrong, meanMaxWrong = regrid_canada(Resolution, dateString, day_of_year, hyphenatedString, fileCount, dateStringCanada, utcCanada, GMT2PST)
    print('Max wind: {0:4f}, hour of maximum mean local wind: {1:2d}'.format(maxWind,meanMax))
    regrid_plot_canada(dateString, dateStringCanada, utcCanada, day_of_year, hyphenatedString, fileCount, maxWind, GMT2PST)
#if fileCount == 24:
#    montage_regular(day_of_year, fileCount)
#    montage_rose(day_of_year, fileCount)
if windDataSource == 'USA':
    tide48HrForcast = getTides(mllw2NAVD88, GMT2PST)
    mdw(start, tide48HrForcast, fileCount)
    locations(grid_number)
elif windDataSource == 'CANADA':
    tide48HrForcast = getTides_canada(mllw2NAVD88, GMT2PST, dateStringCanada, utcCanada)
    mdw_canada(start, dateString, tide48HrForcast, fileCount, dateStringCanada, utcCanada, GMT2PST)
    locations(grid_number)
#print(os.getcwd())
#os.chdir('Wave')
#print(os.getcwd())
#subprocess.check_call('./run_wave.sh')       # Run Wave, which runs Swan using wind data
#split_spectrum(Nlocations)                   # Split SWAN output spectra into separate files
#os.chdir('../XBeach')
#parameters()
#subprocess.check_call('./XBeach')            # Run XBeach using swan output
