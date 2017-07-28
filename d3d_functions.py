# -*- coding: utf-8 -*-
"""
Created on Thu May 25 13:28:48 2017

@author: crosby
"""

from pytz import timezone
import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma
from datetime import datetime, timedelta
from pytz import timezone
from pyproj import Proj
import re
import os
import subprocess
import matplotlib.cm as cm
from matplotlib.colors import LightSource
#from scipy.interpolate import griddata
from matplotlib.mlab import griddata

import op_functions 


def write_amuv(dateString,zulu_hour,param):
# Create Curvilinear wind file

    # Set some constants that vary from model to model
    line_meteo_grid_size= param['line_meteo_grid_size']     # Line number in meteo grid with Nx, Ny
    line_header_skip    = param['line_header_skip']    # Number of header lines in meteo file
    num_forecast_hours  = param['num_forecast_hours']
    
    # Set locations
    fol_grid = param['fol_grid']
        
    # Set file names
    fname_meteo =       param['fname_meteo_grid']
    wind_u_file =       '{0:s}/{1:s}'.format(param['fol_model'],param['wind_u_name'])    
    wind_v_file =       '{0:s}/{1:s}'.format(param['fol_model'],param['wind_v_name'])
    
    # ------------------- Begin Function ----------------------------------    

    # create datetime obj    
    time_obj = datetime.strptime(dateString,'%Y%m%d')
    
    # Write Header
    print 'Writing D3D wind files to {0:s}'.format(wind_u_file)
    uFile = open(wind_u_file,'w')
    vFile = open(wind_v_file,'w')

    uFile.write('### START OF HEADER\n')
    uFile.write('### This file is created for Skagit Delta model\n')
    uFile.write('FileVersion     =    1.03\n')
    uFile.write('filetype        =    meteo_on_curvilinear_grid\n')
    uFile.write('NODATA_value    =    -9999.000\n')
    uFile.write('grid_file        =    {0:s}\n'.format(param['fname_meteo_grid']))
    uFile.write('first_data_value =    grid_llcorner\n')
    uFile.write('data_row         =    grid_row\n')
    uFile.write('n_quantity      =    1\n')
    uFile.write('quantity1       =    x_wind\n')
    uFile.write('unit1           =    m s-1\n')
    uFile.write('### END OF HEADER\n')

    vFile.write('### START OF HEADER\n')
    vFile.write('### This file is created for Skagit Delta model\n')
    vFile.write('FileVersion     =    1.03\n')
    vFile.write('filetype        =    meteo_on_curvilinear_grid\n')
    vFile.write('NODATA_value    =    -9999.000\n')
    vFile.write('grid_file        =    {0:s}\n'.format(param['fname_meteo_grid']))
    vFile.write('first_data_value =    grid_llcorner\n')
    vFile.write('data_row         =    grid_row\n')
    vFile.write('n_quantity      =    1\n')
    vFile.write('quantity1       =    y_wind\n')
    vFile.write('unit1           =    m s-1\n')
    vFile.write('### END OF HEADER\n')

    
    # Load D3D meteo grid
    gridFile = open('{0:s}/{1:s}'.format(fol_grid,fname_meteo),'r')
    lines = gridFile.readlines()
    
    # Read in Nx and Ny
    split_line = lines[line_meteo_grid_size].split()
    Nx = int(split_line[0])
    Ny = int(split_line[1])
    print("Nx, Ny", Nx, Ny)
    
    # Read in grid
    easting  = np.zeros((Ny,Nx), dtype='d')
    northing = np.zeros((Ny,Nx), dtype='d')
    N = len(lines)
    row = 0
    offset = line_header_skip  # header lines to skip
    j = 0
    for n in range(offset,(N-offset)/2):
        split_line = lines[n].split()
        if split_line[0] == 'ETA=':
            j = int(split_line[1]) - 1
            for i in range(5):
                easting[j,i] = float(split_line[i+2])
            row = 0
        else:
            for i in range(len(split_line)):
                easting[j,i+5+5*row] = float(split_line[i])
            row += 1

    for n in range(offset+(N-offset)/2,N):
        split_line = lines[n].split()
        if split_line[0] == 'ETA=':
            j = int(split_line[1]) - 1
            for i in range(5):
                northing[j,i] = float(split_line[i+2])
            row = 0
        else:
            for i in range(len(split_line)):
                northing[j,i+5+5*row] = float(split_line[i])
            row += 1


    #-----------------------Load and write winds from grib --------------------
    hyphenatedString = time_obj.strftime('%Y-%m-%d')
    
    # Read in winds from grib file for region (using bounds)
    (X, Y, U10, V10)= op_functions.read_hrdps_grib(dateString, zulu_hour, param)

    for hour in range(num_forecast_hours):        

        ui = griddata(X.flatten(), Y.flatten(), U10[hour].flatten(), easting, northing, interp='linear')  # linear, nearest, cubic
        vi = griddata(X.flatten(), Y.flatten(), V10[hour].flatten(), easting, northing, interp='linear')  # linear, nearest, cubic

        #Fixed format: time unit since date time time difference (time zone)
        uFile.write('TIME = {0:3.1f} minutes since {1:s} 00:00:00 +00:00\n'.format(60.0*(hour), hyphenatedString))
        vFile.write('TIME = {0:3.1f} minutes since {1:s} 00:00:00 +00:00\n'.format(60.0*(hour), hyphenatedString))
        for j in range(Ny):
            for i in range(Nx):
                if easting[j,i]*northing[j,i] > 0.0:
                    uFile.write('{0:16.9f}'.format(ui[j,i]))
                    vFile.write('{0:16.9f}'.format(vi[j,i]))
                else:
                    uFile.write('{0:16.9f}'.format(-9999.0))
                    vFile.write('{0:16.9f}'.format(-9999.0))
                if i > 0 and (i+1)%5 == 0:
                    uFile.write('\n')
                    vFile.write('\n')
            if Nx%5 != 0:
                uFile.write('\n')
                vFile.write('\n')

#        WNDNOW_file = open('Wave_skagit/WNDNOW_{0:02d}'.format(hour),'w')
#        count = 0
#        for j in range(Ny):
#            for i in range(Nx):
#                if easting[j,i]*northing[j,i] > 0.0:
#                    WNDNOW_file.write('{0:16.6e}'.format(ui[j,i]))
#                else:
#                    WNDNOW_file.write('{0:16.6e}'.format(0.0))
#                if count > 0 and (count+1)%4 == 0:
#                    WNDNOW_file.write('\n')
#                count += 1
#        if (count-1)%4 != 0:
#            WNDNOW_file.write('\n')
#        count = 0
#        for j in range(Ny):
#            for i in range(Nx):
#                if easting[j,i]*northing[j,i] > 0.0:
#                    WNDNOW_file.write('{0:16.6e}'.format(vi[j,i]))
#                else:
#                    WNDNOW_file.write('{0:16.6e}'.format(0.0))
#                if count > 0 and (count+1)%4 == 0:
#                    WNDNOW_file.write('\n')
#                count += 1
#        if (count-1)%4 != 0:
#            WNDNOW_file.write('\n')
#        WNDNOW_file.close()

    uFile.close()
    vFile.close()

#    maxFileName = folder+'maximum_local_wind_{0:02d}Z.dat'.format(utc)
#    maxWindFile = open(maxFileName,'w')
#    maxWindFile.write('Maximum wind: {0:6.3f} m/s, maximum mean local wind {1:6.3f} m/s at {2:2d} hours\n'.format(maxWind, meanMax, maxHour))
#    maxWindFile.close()

    return 0

def write_amuv_homog(dateString, zulu_hour, param, wind_speed, wind_dir):
# Create Curvilinear wind file with homogenous wind forcing

    # Set some constants that vary from model to model
    line_meteo_grid_size= param['line_meteo_grid_size']     # Line number in meteo grid with Nx, Ny
    line_header_skip    = param['line_header_skip']    # Number of header lines in meteo file
    xLL                 = param['xLL']  # lower left corner of SWAN computational grid
    yLL                 = param['yLL']
    num_forecast_hours  = param['num_forecast_hours']
    
    # Set locations
    fol_wind_crop = param['fol_wind_crop']
    fol_wind_amuv = param['fol_model']
    fol_grid = param['fol_grid']
        
    # Set file names
    fname_fol_wind =    '{0:s}{1:s}'.format(param['folname_crop_prefix'],dateString)
    fname_wind_file = '{0:s}{1:s}_{2:02d}z'.format(param['fname_prefix_wind'],dateString,zulu_hour)
    fname_meteo =       param['fname_meteo_grid']
    fname_grd =         param['fname_grid']
    wind_u_file =       '{0:s}/{1:s}'.format(param['fol_model'],param['wind_u_name'])    
    wind_v_file =       '{0:s}/{1:s}'.format(param['fol_model'],param['wind_v_name'])
    
    # ------------------- Begin Function ----------------------------------    

    # create datetime obj    
    time_obj = datetime.strptime(dateString,'%Y%m%d')
    
    # Write Header
    print 'Writing D3D wind files to {0:s}'.format(wind_u_file)
    uFile = open(wind_u_file,'w')
    vFile = open(wind_v_file,'w')

    uFile.write('### START OF HEADER\n')
    uFile.write('### This file is created for Skagit Delta model\n')
    uFile.write('FileVersion     =    1.03\n')
    uFile.write('filetype        =    meteo_on_curvilinear_grid\n')
    uFile.write('NODATA_value    =    -9999.000\n')
    uFile.write('grid_file        =    {0:s}\n'.format(param['fname_meteo_grid']))
    uFile.write('first_data_value =    grid_llcorner\n')
    uFile.write('data_row         =    grid_row\n')
    uFile.write('n_quantity      =    1\n')
    uFile.write('quantity1       =    x_wind\n')
    uFile.write('unit1           =    m s-1\n')
    uFile.write('### END OF HEADER\n')

    vFile.write('### START OF HEADER\n')
    vFile.write('### This file is created for Skagit Delta model\n')
    vFile.write('FileVersion     =    1.03\n')
    vFile.write('filetype        =    meteo_on_curvilinear_grid\n')
    vFile.write('NODATA_value    =    -9999.000\n')
    vFile.write('grid_file        =    {0:s}\n'.format(param['fname_meteo_grid']))
    vFile.write('first_data_value =    grid_llcorner\n')
    vFile.write('data_row         =    grid_row\n')
    vFile.write('n_quantity      =    1\n')
    vFile.write('quantity1       =    y_wind\n')
    vFile.write('unit1           =    m s-1\n')
    vFile.write('### END OF HEADER\n')
   
    # Load D3D meteo grid
    gridFile = open('{0:s}/{1:s}'.format(fol_grid,fname_meteo),'r')
    lines = gridFile.readlines()
    
    # Read in Nx and Ny
    split_line = lines[line_meteo_grid_size].split()
    Nx = int(split_line[0])
    Ny = int(split_line[1])
    print("Nx, Ny", Nx, Ny)
    
    # Read in grid
    easting  = np.zeros((Ny,Nx), dtype='d')
    northing = np.zeros((Ny,Nx), dtype='d')
    N = len(lines)
    row = 0
    offset = line_header_skip  # header lines to skip
    j = 0
    for n in range(offset,(N-offset)/2):
        split_line = lines[n].split()
        if split_line[0] == 'ETA=':
            j = int(split_line[1]) - 1
            for i in range(5):
                easting[j,i] = float(split_line[i+2])
            row = 0
        else:
            for i in range(len(split_line)):
                easting[j,i+5+5*row] = float(split_line[i])
            row += 1

    for n in range(offset+(N-offset)/2,N):
        split_line = lines[n].split()
        if split_line[0] == 'ETA=':
            j = int(split_line[1]) - 1
            for i in range(5):
                northing[j,i] = float(split_line[i+2])
            row = 0
        else:
            for i in range(len(split_line)):
                northing[j,i+5+5*row] = float(split_line[i])
            row += 1


    #-----------------------Load and write winds from grib --------------------
    hyphenatedString = time_obj.strftime('%Y-%m-%d')

    print 'Creating amuv with wind speed {0:d} m/s and direction {1:d} deg'.format(wind_speed,wind_dir)    
    
    wind_dir = 90 - wind_dir #Switch to cartesian
    wind_dir = wind_dir + 180 #Switch from coming-from, to going-to

    deg2rad = np.pi/180.    
    
    u = wind_speed*np.cos(wind_dir*deg2rad)
    v = wind_speed*np.sin(wind_dir*deg2rad)
    
    print 'u velocity is {0:.2f} m/s and v velocity is {1:.2f} m/s'.format(u,v)    

    for hour in range(2):           
        #Fixed format: time unit since date time time difference (time zone)
        uFile.write('TIME = {:d} minutes since {:s} 00:00:00 +00:00\n'.format(hour*60,hyphenatedString))
        vFile.write('TIME = {:d} minutes since {:s} 00:00:00 +00:00\n'.format(hour*60,hyphenatedString))
        for j in range(Ny):
            for i in range(Nx):
                if easting[j,i]*northing[j,i] > 0.0:
                    uFile.write('{0:16.9f}'.format(u))
                    vFile.write('{0:16.9f}'.format(v))
                else:
                    uFile.write('{0:16.9f}'.format(-9999.0))
                    vFile.write('{0:16.9f}'.format(-9999.0))
                if i > 0 and (i+1)%5 == 0:
                    uFile.write('\n')
                    vFile.write('\n')
            if Nx%5 != 0:
                uFile.write('\n')
                vFile.write('\n')

    uFile.close()
    vFile.close()
    return 0

def write_mdw(dateString, zulu_hour, tides, param):
    
    time_obj = datetime.strptime(dateString,'%Y%m%d')
    
#    # for tides:
#    if N_location == 0:
#        location_str = "Crescent Harbor, N. Whidbey Island, Washington"
#    elif N_location == 1:
#        location_str = "Bellingham, Bellingham Bay, Washington"
#    dt = timedelta(days=2, hours=1)
#    Start = tTide
#    Next  = tTide + dt
#    # ========================================= tides =============================================
#    command_str = 'tide -b \"{0:s}\" -e \"{1:s}\" -l \"{2:s}\" -mr -um -s 01:00'.\
#        format( datetime.strftime(Start,"%Y-%m-%d %H:%M"), datetime.strftime(Next,"%Y-%m-%d %H:%M"), location_str )
#    tidesStr = subprocess.check_output(command_str, shell=True)
#    tides = tidesStr.split()    # 48 times and 48 elevations
#    Ntides = len(tides)
#    if Ntides > 96:
#        Ntides = 96
#    elevation = np.empty(Ntides/2, dtype='d')
#    for n in range(0,Ntides,2):
#        elevation[n/2] = (float(tides[n+1]))
        
    # =============================================================================================
    mdwFile = open('{0:s}/{1:s}'.format(param['fol_model'],param['fname_mdw']),'w')
    mdwFile.write('[WaveFileInformation]\n')
    mdwFile.write('   FileVersion          = 02.00\n')
    mdwFile.write('[General]\n')
    mdwFile.write('   ProjectName          = Skgt_50m\n')
    mdwFile.write('   ProjectNr            = 1\n')
    mdwFile.write('   Description          = Grid info:\n')
    mdwFile.write('   OnlyInputVerify      = false\n')
    mdwFile.write('   SimMode              = stationary\n')
    mdwFile.write('   DirConvention        = nautical\n')
    mdwFile.write('   ReferenceDate        = {0:s}\n'.format(time_obj.strftime('%Y-%m-%d')))
    mdwFile.write('   MeteoFile            = {0:s}\n'.format(param['wind_u_name']))
    mdwFile.write('   MeteoFile            = {0:s}\n'.format(param['wind_v_name']))
    for hour in range(param['num_forecast_hours']):
        #elevation = float(tideLines[hour].split()[1])
        #elevation = tides[hour].split()[1]
        mdwFile.write('[TimePoint]\n')
        mdwFile.write('   Time                 =  {0:3.1f}\n'.format(hour*60.0))
        mdwFile.write('   WaterLevel           =  {0:9.6f}\n'.format(tides[hour]))        
        mdwFile.write('   XVeloc               =  0.0000000e+000\n')
        mdwFile.write('   YVeloc               =  0.0000000e+000\n')
    mdwFile.write('[Constants]\n')
    mdwFile.write('   WaterLevelCorrection =  0.0000000e+000\n')
    mdwFile.write('   Gravity              =  9.8100004e+000\n')
    mdwFile.write('   WaterDensity         =  1.0250000e+003\n')
    mdwFile.write('   NorthDir             =  9.0000000e+001\n')
    mdwFile.write('   MinimumDepth         =  5.0000001e-002\n')
    mdwFile.write('[Processes]\n')
    mdwFile.write('   GenModePhys          = 3\n')
    mdwFile.write('   Breaking             = true\n')
    mdwFile.write('   BreakAlpha           =  1.0000000e+000\n')
    mdwFile.write('   BreakGamma           =  7.3000002e-001\n')
    mdwFile.write('   Triads               = false\n')
    mdwFile.write('   TriadsAlpha          =  1.0000000e-001\n')
    mdwFile.write('   TriadsBeta           =  2.2000000e+000\n')
    mdwFile.write('   WaveSetup            = false\n')
    mdwFile.write('   BedFriction          = jonswap\n')
    mdwFile.write('   BedFricCoef          =  6.7000002e-002\n')
    mdwFile.write('   Diffraction          = true\n')
    mdwFile.write('   DiffracCoef          =  2.0000000e-001\n')
    mdwFile.write('   DiffracSteps         = 5\n')
    mdwFile.write('   DiffracProp          = true\n')
    mdwFile.write('   WindGrowth           = true\n')
    mdwFile.write('   WhiteCapping         = Komen\n')
    mdwFile.write('   Quadruplets          = true\n')
    mdwFile.write('   Refraction           = true\n')
    mdwFile.write('   FreqShift            = true\n')
    mdwFile.write('   WaveForces           = dissipation 3d\n')
    mdwFile.write('[Numerics]\n')
    mdwFile.write('   DirSpaceCDD          =  5.0000000e-001\n')
    mdwFile.write('   FreqSpaceCSS         =  5.0000000e-001\n')
    mdwFile.write('   RChHsTm01            =  2.0000000e-002\n')
    mdwFile.write('   RChMeanHs            =  2.0000000e-002\n')
    mdwFile.write('   RChMeanTm01          =  2.0000000e-002\n')
    mdwFile.write('   PercWet              =  9.8000000e+001\n')
    mdwFile.write('   MaxIter              = 30\n')
    mdwFile.write('[Output]\n')
    mdwFile.write('   TestOutputLevel      = 0\n')
    mdwFile.write('   TraceCalls           = false\n')
    mdwFile.write('   UseHotFile           = false\n')
    mdwFile.write('   Int2KeepHotfile      = 180.0\n')
    mdwFile.write('   WriteCOM             = false\n')
    mdwFile.write('   COMWriteInterval     = 60\n')
    mdwFile.write('   AppendCOM            = true\n')
    mdwFile.write('   WriteCOM             = false\n')
    for fname in param['output_locs']:
        mdwFile.write('   LocationFile         = {:s}\n'.format(fname))
    mdwFile.write('   WriteTable           = true\n')
    mdwFile.write('   WriteSpec1D          = false\n')
    mdwFile.write('   WriteSpec2D          = false\n')
    mdwFile.write('[Domain]\n')
    mdwFile.write('   Grid                 = {0:s}\n'.format(param['fname_grid']))
    mdwFile.write('   BedLevel             = {0:s}\n'.format(param['fname_dep']))
    mdwFile.write('   DirSpace             = circle\n')
    mdwFile.write('   NDir                 = 36\n')
    mdwFile.write('   StartDir             =  0.0000000e+000\n')
    mdwFile.write('   EndDir               =  0.0000000e+000\n')
    mdwFile.write('   FreqMin              =  1.25000001e-001\n')
    mdwFile.write('   FreqMax              =  5.0000000e+000\n')
    mdwFile.write('   NFreq                = 36\n')
    mdwFile.write('   Output               = true\n')
    mdwFile.close()

def make_test_loc(param):
    locFile = open('{0:s}/test.loc'.format(param['fol_model']),'w')
    locFile.write('533624.235 5358750.978\n')
    locFile.write('533409.416 5359552.696\n')
    locFile.write('533194.596 5360354.415\n')
    locFile.close()













##============================================
#def read_SRTM():
    #Nxs = 3601
    #Nys = 3601
    #height   = np.zeros((Nys, Nxs), 'd')
    #topoFile = open('Bellingham_SRTM1_UTM.dat','r')
    #topoLines = topoFile.readlines()
    #topoFile.close()
    #for j in range(Nys):
        #for i in range(Nxs):
            #split = topoLines[j*Nxs+i].split()
            #height[Nys-1-j,i]   = float(split[2])
    ## images read from top to bottom

    #height = np.ma.masked_where(height <= 0.0, height)
    #return height

#def Skagit_regrid_plot(day_of_year, fileCount, maxWind, utc, tTide):
#    #================== Skagit topography ========================
#    NxT = 2500
#    NyT = 2400
#    xT = np.zeros((NyT,NxT), dtype='d')
#    yT = np.zeros((NyT,NxT), dtype='d')
#    zT = np.zeros((NyT,NxT), dtype='d')
#    cropFile = open('cropped_two_meter.dat','r')
#    for j in range(NyT):
#        for i in range(NxT):
#            line = cropFile.readline()
#            split = line.split()
#            xT[j,i] = float(split[0])
#            yT[j,i] = float(split[1])
#            zT[j,i] = float(split[2])
#
#    zT = np.ma.masked_where(zT <= 1.4, zT)
#    ls = LightSource(azdeg=225, altdeg=60)
#
#    ewMin = 525000.0
#    ewMax = 550000.0
#    nsMin = 5343000.0
#    nsMax = 5367000.0
#
#    #p = Proj(proj='utm', zone=10, ellps='WGS84')
#    #ls = LightSource(azdeg=225, altdeg=60)
#    #GeoBounds = np.asarray([[-123,-122],[48.0, 49.0]])
#    #utmEbounds, utmNbounds = p(GeoBounds[0,:],GeoBounds[1,:])
#    #height = read_SRTM()
#
#    #ewMin = utmEbounds[0]
#    #ewMax = utmEbounds[1]
#    #nsMin = utmNbounds[0]
#    #nsMax = utmNbounds[1]
#
#    # =========================================
#
#    # lower left corner of SWAN computational grid
#    xLL =  526108.0
#    yLL = 5343228.0
#
#    ##=============================================
#    #nShorePts = np.zeros(11, dtype='i')
#    #shoreFile = open('SKAGIT_shore.dat','r')
#    #shoreLines = shoreFile.readlines()
#    ##=============================================
#    skagitMeans = []
#    skagitMaxes = []
#    labels = []
#    imageCount = 0
#    for hour in range(fileCount):
#        figureName = 'regular_grid_skagit_wind_{0:03d}_{1:02d}z_{2:02d}.png'.format(day_of_year, utc, hour)
#        if os.path.exists(figureName):
#            print(figureName + ' found.')
#        else:
#            windFileName = 'wind_data_{0:03d}/cropped_wind_{0:03d}_{1:02d}z_{2:02d}.dat'.format(day_of_year, utc, hour)
#
#            windFile = open(windFileName,"r")
#            line = windFile.readline()
#            Ny = int(line.split()[0])
#            Nx = int(line.split()[1])
#            Nw = Ny*Nx
#
#            x = np.zeros(Nw, dtype='d')
#            y = np.zeros(Nw, dtype='d')
#            xy = np.zeros((Nw,2), dtype='d')
#            u = np.zeros(Nw, dtype='d')
#            v = np.zeros(Nw, dtype='d')
#
#            for n in range(Nw):
#                line = windFile.readline()
#                split_line = line.split()
#                x[n] = float(split_line[0])
#                y[n] = float(split_line[1])
#                xy[n,0] = x[n]
#                xy[n,1] = y[n]
#                u[n] = float(split_line[2])
#                v[n] = float(split_line[3])
#
#            if EQUIDISTANT:
#                margin = 50.0
#                deltax = np.linspace(0.0, (20700.0+2.0*margin), Nx)
#                deltay = np.linspace(0.0, (24450.0+2.0*margin), Ny)
#                xi = deltax + xLL - margin
#                yi = deltay + yLL - margin
#
#            if CURVILINEAR or ON_GRID:
#                deltax = np.linspace(0.0, (20700.0), Nx)
#                deltay = np.linspace(0.0, (24450.0), Ny)
#                xi = deltax + xLL
#                yi = deltay + yLL
#
#            wsp = np.sqrt(u**2 + v**2)
#
#            if SCIPY:
#                wi = griddata(xy,  wsp, (xi[None,:], yi[:,None]), method='cubic')
#                ui = griddata(xy,  u, (xi[None,:], yi[:,None]), method='cubic')  # linear, nearest, cubic
#                vi = griddata(xy,  v, (xi[None,:], yi[:,None]), method='cubic')
#            else:
#                wi = griddata(x, y,  wsp, xi, yi, interp='nn')
#                ui = griddata(x, y,  u, xi, yi, interp='nn') # linear, nn
#                vi = griddata(x, y,  v, xi, yi, interp='nn')
#
#            ws = np.sqrt(ui.flatten()**2 + vi.flatten()**2)
#            # ------------------------------- find means --------------------------
#            MeanWind = np.mean(ws)
#            MaxWind  = np.max( ws)
#            skagitMeans.append(MeanWind)
#            skagitMaxes.append(MaxWind)
#
#            dhour = timedelta(hours=hour)
#            hourStr = datetime.strftime(tTide+dhour,"%d %H")
#            labels.append(hourStr)
#            #print('{0:s} {1:6.3f} {2:6.3f} '.format(hourStr, MeanWind, MaxWind)),
#            # ---------------------------------------------------------------------
#            #cartesian = np.arctan2(vi.flatten(),ui.flatten())*180.0/np.pi
#            #wd  = (270.0 - cartesian)%360.0
#
#            dt = timedelta(hours=hour)
#            Next  = tTide + dt
#            pnwDateString = datetime.strftime(Next, "%Y-%m-%d %H:%M")
#
#            #====================================================================================
#
#            #fig = plt.figure(figsize=(12.8,10))
#
#            ##================== shoreline ================
#            #first = True
#            #n = 0
#            #for line in shoreLines:
#                #if re.search('#', line):
#                    #if not first:
#                        #n += 1
#                        #xs,ys = p(slon,slat)
#                        #xs = np.asarray(xs)
#                        #ys = np.asarray(ys)
#                        #plt.plot(xs, ys, 'k-', lw=1.5)
#                    #slon = []
#                    #slat = []
#                    #first = False
#                #else:
#                    #nShorePts[n] += 1
#                    #slon.append(float(line.split()[0]))
#                    #slat.append(float(line.split()[1]))
#
#            ##================ XBeach grids ===============
#            ##XBx = [ 532812.0,  535212.0,  535212.0,  532812.0,  532812.0]
#            ##XBy = [5359202.0, 5359202.0, 5360722.0, 5360722.0, 5359202.0]
#            ##plt.plot(XBx, XBy, 'r-')
#            ##XBxx = [ 533050.0,  533481.33513652,  533000.50252532,  532569.16738879, 533050.0 ]
#            ##XByy = [5360750.0, 5361181.33513652, 5361662.16774773, 5361230.83261121, 5360750.0]
#            ##plt.plot(XBxx, XByy, 'k-')
#            ##XBxxx = [ 533632.0,  534694.51840892,  534249.34965134,  533186.83124242,  533632.0]
#            ##XByyy = [ 5358722.0,  5359006.70094961,  5360668.09337083,  5360383.39242122, 5358722.0]
#            ##plt.plot(XBxxx, XByyy, 'r-', lw=2)
#            ##swanx = [ 532632.0, 534187.63491861, 533056.26406871, 531500.6291501, 532632.0 ]
#            ##swany = [ 5358942.0, 5360497.63491861, 5361629.00576851, 5360073.3708499, 5358942.0]
#            ##plt.plot(swanx, swany, 'b-', lw=2.0)
#            ##=============================== topography ==================================
#            #plt.imshow(ls.hillshade(zT), cmap=cm.gray, origin='upper',aspect='equal',
#                   #extent=[ewMin, ewMax, nsMin, nsMax], zorder=11)
#            ##=============================================
#            #plt.quiver(x, y, u, v, color='w', width=0.003, scale=100.0, zorder=5)
#            #sp = plt.streamplot(xi,yi, ui, vi, color='w', density=1.5, arrowsize=0.01, zorder=5)
#            #levels = np.linspace(0.0, maxWind, 30)
#
#            #CS = plt.contour( xi, yi, wi, levels, colors=['0.0', '0.5', '0.5', '0.5', '0.5'])   # linewidths=0.5, colors='k'
#            #CS = plt.contourf(xi, yi, wi, levels, cmap=plt.cm.jet)
#            #plt.colorbar()
#            #plt.scatter(x, y, marker='o', c='b',s=5)
#            #plt.title('Irregular Wind Grid -> regular ~50 m Skagit grid\n {0:s}'.format(pnwDateString))
#            ##plt.xlim( 526100.0, 546800.0)
#            ##plt.ylim(5343200.0,5367700.0)
#            #plt.xlim(ewMin+1100.0, ewMax)
#            #plt.ylim(nsMin+200, nsMax)
#            #ax = plt.gca()
#            #ax.set_xticklabels('')
#            #ax.set_yticklabels('')
#            #plt.grid(True, zorder=6)
#            #plt.savefig(figureName)
#            ##plt.show()
#            #plt.close()
#            #print(figureName)
#            imageCount += 1
#
#    if imageCount == fileCount:
#        #================ Tides =====================
#        # for representative tides:
#        location_str = "Crescent Harbor, N. Whidbey Island, Washington"
#        dt = timedelta(days=2, hours=1)
#        Start = tTide
#        Next  = tTide + dt
#
#        command_str = 'tide -b \"{0:s}\" -e \"{1:s}\" -l \"{2:s}\" -mr -um -s 01:00'.\
#            format( datetime.strftime(Start,"%Y-%m-%d %H:%M"), datetime.strftime(Next,"%Y-%m-%d %H:%M"), location_str )
#        tidesStr = subprocess.check_output(command_str, shell=True)
#        tides = tidesStr.split()
#        Ntides = len(tides)
#        if Ntides > 96:
#            Ntides = 96
#        tide = np.empty(Ntides/2, dtype='d')
#        for n in range(0,Ntides,2):
#            tide[n/2] = (float(tides[n+1]))
#        #td_hrs = np.linspace(-7.0, 40.0, 48)
#        td_hrs = np.arange(Ntides/2)
#        #=============================================
#
#        figName = 'Skagit_mean_winds_{0:03d}_{1:02d}z.png'.format(day_of_year, utc)
#        legendLabels = ('average', 'maximum', 'gale')
#        print(figName),
#        hrs = np.arange(fileCount)
#        skagitMeans = np.asarray(skagitMeans)
#        skagitMaxes = np.asarray(skagitMaxes)
#        print(np.min(hrs),np.max(hrs), np.shape(skagitMeans), Ntides/2)
#        gale = np.ones(fileCount, dtype='d')*17.5
#        fig = plt.figure(1, figsize=(20,12))
#        ax1 = fig.add_subplot(211)
#        ax1.plot(hrs,skagitMeans, 'b-')
#        ax1.plot(hrs,skagitMaxes, 'g-')
#        ax1.plot(gale, 'r-')
#        ax1.legend(legendLabels, loc='upper left')
#        ax1.grid(True)
#        ax1.set_ylabel('meters / second')
#        ax1.set_title('Skagit Delta mean and maximum wind speeds from ' + datetime.strftime(tTide, "%B %d %Y"))
#        ax1.set_xlim(0, fileCount)
#
#        ax2 = fig.add_subplot(212)
#        ax2.plot(td_hrs, tide, 'b-', lw=2)
#        ax2.set_xticks(hrs)
#        ax2.set_xticklabels(labels, rotation=45)
#        ax2.set_xlabel('day and hour')
#        ax2.set_ylabel('tide in meters')
#        ax2.set_ylim(-0.75,4.1)
#        ax2.grid(True)
#        ax2.set_xlim(0, fileCount)
#
#        plt.tight_layout(h_pad=0.1)  # padding is in fraction of fontsize
#        plt.savefig(figName)
#        #plt.show()
#        plt.close()

#import pytz
#datestring = '20160217'
#t00 = datetime.strptime(datestring,'%Y%m%d')
#t00 = pytz.utc.localize(t00)
#utc = 12
#region = 0  # 0 -> jdf, 1 -> sog
#Skagit_regrid_plot(48, 48, 20, utc, t00)