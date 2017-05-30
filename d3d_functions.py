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

SCIPY = True

# Choose one of these
EQUIDISTANT = False
CURVILINEAR = True
ON_GRID = False         # not enabled yet in WAVE

if SCIPY:
    from scipy.interpolate import griddata
else:
    from matplotlib.mlab import griddata


if EQUIDISTANT:
    Nx = 415+2
    Ny = 490+2
if CURVILINEAR or ON_GRID:
    Nx = 415
    Ny = 490

def Skagit_regrid(dateString, day_of_year, hyphenatedString, folder, fileCount, utc):
    # ========== output file headers ==========
    global Ny
    global Nx
    print('Skagit regrid(Ny={0:d},Nx={1:d})'.format(Ny,Nx))
    if EQUIDISTANT:
        wind_u_name = 'Wave_skagit/wind_{0:s}_{1:03d}_{2:02d}.amu'.format(dateString, day_of_year, utc)
        wind_v_name = 'Wave_skagit/wind_{0:s}_{1:03d}_{2:02d}.amv'.format(dateString, day_of_year, utc)
        if os.path.exists(wind_u_name) and os.path.exists(wind_v_name):
            print('Skagit .amu and .amv files found.')
            return 0
        uFile = open(wind_u_name,'w')
        vFile = open(wind_v_name,'w')

        uFile.write('### START OF HEADER\n')
        uFile.write('### This file is created for Skagit Delta model\n')
        uFile.write('FileVersion     =    1.03\n')  # Version of meteo input file, to check if the newest file format is used
        # Type of meteo input file: meteo_on_flow_grid, meteo_on_curvilinear_grid, meteo_on_rectilinear_grid or meteo_on_spiderweb_grid
        uFile.write('filetype        =    meteo_on_equidistant_grid\n')
        uFile.write('NODATA_value    =    -999.000\n')           # Value used for undefined or missing data
        uFile.write('n_cols          =    {0:3d}\n'.format(Nx))
        uFile.write('n_rows          =    {0:3d}\n'.format(Ny))
        uFile.write('grid_unit       =    m\n')
        uFile.write('x_llcorner      =    526108.0\n')
        uFile.write('y_llcorner      =    5343228.0\n')
        uFile.write('dx              =    50.0\n')
        uFile.write('dy              =    50.0\n')
        uFile.write('n_quantity      =    1\n')                  # Number of quantities prescribed in the file
        uFile.write('quantity1       =    x_wind\n')             # Name of quantity1
        uFile.write('unit1           =    m s-1\n')              # Unit of quantity1
        uFile.write('### END OF HEADER\n')

        vFile.write('### START OF HEADER\n')
        vFile.write('### This file is created for Skagit Delta model\n')
        vFile.write('FileVersion     =    1.03\n')
        vFile.write('filetype        =    meteo_on_equidistant_grid\n')
        vFile.write('NODATA_value    =    -999.000\n')
        vFile.write('n_cols          =    {0:3d}\n'.format(Nx))
        vFile.write('n_rows          =    {0:3d}\n'.format(Ny))
        vFile.write('grid_unit       =    m\n')
        vFile.write('x_llcorner      =    526108.0\n')
        vFile.write('y_llcorner      =    5343228.0\n')
        vFile.write('dx              =    50.0\n')
        vFile.write('dy              =    50.0\n')
        vFile.write('n_quantity      =    1\n')
        vFile.write('quantity1       =    y_wind\n')
        vFile.write('unit1           =    m s-1\n')
        vFile.write('### END OF HEADER\n')

    if CURVILINEAR:
        wind_u_name = 'Wave_skagit/wind_{0:s}_{1:03d}_{2:02d}.amu'.format(dateString, day_of_year, utc)
        wind_v_name = 'Wave_skagit/wind_{0:s}_{1:03d}_{2:02d}.amv'.format(dateString, day_of_year, utc)
        if os.path.exists(wind_u_name) and os.path.exists(wind_v_name):
            print('Skagit .amu and .amv files found.')
            return 0
        uFile = open(wind_u_name,'w')
        vFile = open(wind_v_name,'w')

        uFile.write('### START OF HEADER\n')
        uFile.write('### This file is created for Skagit Delta model\n')
        uFile.write('FileVersion     =    1.03\n')
        uFile.write('filetype        =    meteo_on_curvilinear_grid\n')
        uFile.write('NODATA_value    =    -9999.000\n')
        uFile.write('grid_file        =    meteo.grd\n')
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
        vFile.write('grid_file        =    meteo.grd\n')
        vFile.write('first_data_value =    grid_llcorner\n')
        vFile.write('data_row         =    grid_row\n')
        vFile.write('n_quantity      =    1\n')
        vFile.write('quantity1       =    y_wind\n')
        vFile.write('unit1           =    m s-1\n')
        vFile.write('### END OF HEADER\n')

    if ON_GRID:
        # Manual: A.2.10.1 Space-varying wind on the computational (SWAN) grid
        # Wave program: "meteo on computational grid" (flow grid) is not supported by Delft3D-WAVE

        wind_uv_name = 'Wave_skagit/wind_{0:s}_{1:03d}_{2:02d}.wnd'.format(dateString, day_of_year, utc)
        if os.path.exists(wind_uv_name):
            print('Skagit .wnd file found.')
            return 0
        uvFile = open(wind_uv_name,'w')

        uvFile.write('### START OF HEADER\n')
        uvFile.write('### This file is created for Skagit Delta model\n')
        uvFile.write('FileVersion      =    1.03\n')               # Version of meteo input file, to check if the newest file format is used
        # Type of meteo input file: meteo_on_flow_grid, meteo_on_curvilinear_grid, meteo_on_rectilinear_grid or meteo_on_spiderweb_grid
        uvFile.write('filetype         =    meteo_on_computational_grid\n')
        uvFile.write('NODATA_value     =    -999.000\n')           # Value used for undefined or missing data
        uvFile.write('n_quantity       =    3\n')                  # Number of quantities prescribed in the file
        uvFile.write('quantity1        =    x_wind\n')             # Name of quantity1
        uvFile.write('quantity2        =    y_wind\n')             # Name of quantity1
        uvFile.write('quantity3        =    air_pressure\n')             # Name of quantity1
        uvFile.write('unit1            =    m s-1\n')              # Unit of quantity1
        uvFile.write('unit2            =    m s-1\n')              # Unit of quantity1
        uvFile.write('unit3            =    Pa\n')              # Unit of quantity1
        uvFile.write('### END OF HEADER\n')

    # ============== D3D grid  ================

    gridFile = open('Wave_skagit/SKAGIT_50m.grd','r')
    lines = gridFile.readlines()
    split_line = lines[6].split()
    #Nx = int(split_line[0])
    #Ny = int(split_line[1])
    #print("Nx, Ny", Nx, Ny)
    easting  = np.zeros((Ny,Nx), dtype='d')
    northing = np.zeros((Ny,Nx), dtype='d')
    N = len(lines)
    row = 0
    offset = 8  # header length
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

    # =========================================

    # lower left corner of SWAN computational grid
    xLL =  526108.0
    yLL = 5343228.0

    #=============================================
    maxWind = 0.0
    maxHour = 0
    meanMax = 0.0
    for hour in range(fileCount):
        windFileName = 'wind_data_{0:03d}/cropped_wind_{0:03d}_{1:02d}z_{2:02d}.dat'.format(day_of_year, utc, hour)
        print('reading {0:s} '.format(windFileName))

        windFile = open(windFileName,"r")
        line = windFile.readline()
        Nyw = int(line.split()[0])
        Nxw = int(line.split()[1])
        Nw = Nyw*Nxw

        x = np.zeros(Nw, dtype='d')
        y = np.zeros(Nw, dtype='d')
        xy = np.zeros((Nw,2), dtype='d')
        u = np.zeros(Nw, dtype='d')
        v = np.zeros(Nw, dtype='d')

        for n in range(Nw):
            line = windFile.readline()
            split_line = line.split()
            x[n] = float(split_line[0])
            y[n] = float(split_line[1])
            xy[n,0] = x[n]
            xy[n,1] = y[n]
            u[n] = float(split_line[2])
            v[n] = float(split_line[3])

        # data bounds for 30 degree rotated grid: 519438.08/552480.01   5337880.74/5370825.41  1.41141/2.53641  -2.213364/-1.338364

        #xi = np.linspace( 519438.08,  552480.01, Nx)
        #yi = np.linspace(5337880.74, 5370825.41, Ny)
        if EQUIDISTANT:
            margin = 50.0
            deltax = np.linspace(0.0, (20700.0+2.0*margin), Nx)
            deltay = np.linspace(0.0, (24450.0+2.0*margin), Ny)
            xi = deltax + xLL - margin
            yi = deltay + yLL - margin

        if CURVILINEAR or ON_GRID:
            deltax = np.linspace(0.0, (20700.0), Nx)
            deltay = np.linspace(0.0, (24450.0), Ny)
            xi = deltax + xLL
            yi = deltay + yLL

        if SCIPY:
            ui = griddata(xy,  u, (xi[None,:], yi[:,None]), method='cubic')  # linear, nearest, cubic
            vi = griddata(xy,  v, (xi[None,:], yi[:,None]), method='cubic')
        else:
            ui = griddata(x, y,  u, xi, yi,interp='nn') # linear, nn
            vi = griddata(x, y,  v, xi, yi,interp='nn')

        ws = np.sqrt(ui**2 + vi**2)
        mspd = np.max(ws)
        mmax = np.mean(ws)
        if maxWind < mspd:
            maxWind = mspd
        if meanMax < mmax:
            meanMax = mmax
            maxHour = hour

        #regularFile = open('regular_wind_grid_{0:03d}_{1:02d}z_{2:02d}.dat'.format(day_of_year, utc, hour),'w')
        #for j in range(Ny):
            #for i in range(Nx):
                #if not ui[j,i]:
                    #regularFile.write('{0:9.2f} {1:11.2f} {2:12.6f} {3:12.6f}\n'.format(xi[i], yi[j], 0.0, 0.0 ))
                #elif np.isnan(ui[j,i]):
                    #regularFile.write('{0:9.2f} {1:11.2f} {2:12.6f} {3:12.6f}\n'.format(xi[i], yi[j], 0.0, 0.0 ))
                #else:
                    #regularFile.write('{0:9.2f} {1:11.2f} {2:12.6f} {3:12.6f}\n'.format(xi[i], yi[j], ui[j,i], vi[j,i] ))
        #regularFile.close()

        if EQUIDISTANT or CURVILINEAR:
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

            WNDNOW_file = open('Wave_skagit/WNDNOW_{0:02d}'.format(hour),'w')
            count = 0
            for j in range(Ny):
                for i in range(Nx):
                    if easting[j,i]*northing[j,i] > 0.0:
                        WNDNOW_file.write('{0:16.6e}'.format(ui[j,i]))
                    else:
                        WNDNOW_file.write('{0:16.6e}'.format(0.0))
                    if count > 0 and (count+1)%4 == 0:
                        WNDNOW_file.write('\n')
                    count += 1
            if (count-1)%4 != 0:
                WNDNOW_file.write('\n')
            count = 0
            for j in range(Ny):
                for i in range(Nx):
                    if easting[j,i]*northing[j,i] > 0.0:
                        WNDNOW_file.write('{0:16.6e}'.format(vi[j,i]))
                    else:
                        WNDNOW_file.write('{0:16.6e}'.format(0.0))
                    if count > 0 and (count+1)%4 == 0:
                        WNDNOW_file.write('\n')
                    count += 1
            if (count-1)%4 != 0:
                WNDNOW_file.write('\n')
            WNDNOW_file.close()

        if ON_GRID:
            uvFile.write('TIME = {0:5.1f} minutes since 2015-08-23 00:00:00 +00:00\n'.format(60.0*(hour)))
            for j in range(Ny):
                for i in range(Nx):
                    if easting[j,i]*northing[j,i] > 0.0:
                        uvFile.write('{0:16.9f}'.format(ui[j,i]))
                    else:
                        uvFile.write('{0:16.9f}'.format(-999.0))
                    if i > 0 and (i+1)%5 == 0:
                        uvFile.write('\n')
                if Nx%5 != 0:
                    uvFile.write('\n')

            for j in range(Ny):
                for i in range(Nx):
                    if easting[j,i]*northing[j,i] > 0.0:
                        uvFile.write('{0:16.9f}'.format(vi[j,i]))
                    else:
                        uvFile.write('{0:16.9f}'.format(-999.0))
                    if i > 0 and (i+1)%5 == 0:
                        uvFile.write('\n')
                if Nx%5 != 0:
                    uvFile.write('\n')

            for j in range(Ny):
                for i in range(Nx):
                    if easting[j,i]*northing[j,i] > 0.0:
                        uvFile.write('{0:16.9f}'.format(100000.0))
                    else:
                        uvFile.write('{0:16.9f}'.format(-999.0))
                    if i > 0 and (i+1)%5 == 0:
                        uvFile.write('\n')
                if Nx%5 != 0:
                    uvFile.write('\n')

    uFile.close()
    vFile.close()

    maxFileName = folder+'maximum_local_wind_{0:02d}Z.dat'.format(utc)
    maxWindFile = open(maxFileName,'w')
    maxWindFile.write('Maximum wind: {0:6.3f} m/s, maximum mean local wind {1:6.3f} m/s at {2:2d} hours\n'.format(maxWind, meanMax, maxHour))
    maxWindFile.close()

    return 0

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