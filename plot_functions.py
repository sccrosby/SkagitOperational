# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 12:09:18 2017

@author: crosby
"""


import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm

import matplotlib.gridspec as gridspec
from matplotlib.colors import LightSource
from datetime import datetime, timedelta
import subprocess
from poly_mask import Polygon
import os
from scipy.interpolate import griddata

# Custom libraries
import op_functions
import show_grid 


# Returns GMT offset to PST/PDT 
#def get_gmt_offset_2():
#    # Works through 2019, HARDCODED
#    myTime = datetime.utcnow()
#    if datetime(2015,3,8,2,0,0) < myTime < datetime(2015,11,1,2,0,0):
#        GMT2PST = 7 #hr
#    elif datetime(2016,3,13,2,0,0) < myTime < datetime(2016,11,6,2,0,0):
#        GMT2PST = 7 #hr
#    elif datetime(2017,3,12,2,0,0) < myTime < datetime(2017,11,5,2,0,0):
#        GMT2PST = 7 #hr
#    elif datetime(2018,3,11,2,0,0) < myTime < datetime(2018,11,4,2,0,0):
#        GMT2PST = 7 #hr
#    elif datetime(2019,3,10,2,0,0) < myTime < datetime(2019,11,3,2,0,0):
#        GMT2PST = 7 #hr
#    else:
#        GMT2PST = 8 #hr
#    return GMT2PST

def plot_skagit_hsig(date_string, zulu_hour, maxWind, tide, param):
    # Constants
    m2ft = 3.28084  # Convert meters to feet
    
    print 'Entering plotting function for BBay'
    
    #-------------Plotting file locations-------------------------
    file_grid_crop = '../Plots/skagit_50m/plotting_files/cropped_two_meter.dat'
    file_shore_mask = '../Plots/skagit_50m/plotting_files/SKAGIT_shore_mask.dat'    

    #-------------Model Files-------------------------------------
    file_grid = '{:s}/{:s}'.format(param['fol_grid'],param['fname_grid'])

    # Time variables
    time_start_utc = datetime.strptime('{:s}{:02d}'.format(date_string,zulu_hour),'%Y%m%d%H')
    time_vec_utc = [time_start_utc + timedelta(hours=x) for x in range(param['num_forecast_hours'])]    
    time_vec_local = [time_start_utc - timedelta(hours=(x-param['gmt_offset'])) for x in range(param['num_forecast_hours'])]  
    
    #================== Skagit topography ========================
    NxT = 2500
    NyT = 2400
    Nx = 415
    Ny = 490
    xT = np.zeros((NyT,NxT), dtype='d')
    yT = np.zeros((NyT,NxT), dtype='d')
    zT = np.zeros((NyT,NxT), dtype='d')
    cropFile = open(file_grid_crop,'r')
    for j in range(NyT):
        for i in range(NxT):
            line = cropFile.readline()
            split = line.split()
            xT[j,i] = float(split[0])
            yT[j,i] = float(split[1])
            zT[j,i] = float(split[2])
    zT = np.ma.masked_where(zT <= 1.4, zT)
    ls = LightSource(azdeg=225, altdeg=60)


    hours = np.linspace(-7.0, 40.0, 48)

    plt.style.use( 'ggplot')

    x,y,nx,ny = show_grid.Grid(file_grid)
    dy = [-0.75,4.1]    # y-axis range for tide graph
    Vmax = 1.00         # wave height limit
    Scale = 9
    
    #Vmax = 0.70  # Nov 4: 0.32  # Nov 2: 0.4
    Levels = np.arange(0.0,Vmax,0.02)


    ewMin = 525000.0
    ewMax = 550000.0
    nsMin = 5343000.0
    nsMax = 5367000.0

    xLL =  param['xLL']
    yLL =  param['yLL']
    skip = 19

    daysMax = 0.0

    #deltax = np.linspace(0.0, (20700.0), Nx)
    deltax = np.linspace(0.0, (22000.0), Nx)
    deltay = np.linspace(0.0, (24450.0), Ny)
    
    xi = deltax + xLL
    yi = deltay + yLL
    
    
    # ===================================== wind grid ==============================
    hour = 0
    file_wind_crop = '{0:s}/{1:s}{2:s}/{3:s}{2:s}_{4:02d}z_{5:02d}.dat'.format(param['fol_wind_crop'],
        param['folname_crop_prefix'],date_string,param['fname_prefix_wind'], zulu_hour, hour)
    
    windFile = open(file_wind_crop,"r")
    line = windFile.readline()
    Nyw = int(line.split()[0])
    Nxw = int(line.split()[1])
    Nw = Nyw*Nxw
    print('Nxw {0:3d} Nyw {1:3d} Nw {2:5d}'.format(Nxw, Nyw, Nw))
    xw = np.zeros(Nw, dtype='d')
    yw = np.zeros(Nw, dtype='d')
    xyw = np.zeros((Nw,2), dtype='d')
    for n in range(Nw):
        line = windFile.readline()
        split_line = line.split()
        xw[n] = float(split_line[0])
        yw[n] = float(split_line[1])
        xyw[n,0] = xw[n]
        xyw[n,1] = yw[n]
        

    # =============================== lowlands mask ==========================
    shoreFile = open(file_shore_mask,'r')
    slines = shoreFile.readlines()
    shoreFile.close()
    xvert = []
    yvert = []
    for line in slines:
        splitLine = line.split()
        xvert.append(float(splitLine[0]))
        yvert.append(float(splitLine[1]))
    xx, yy = np.meshgrid(xi, yi)

    poly = Polygon(xvert, yvert)
    grid = poly.is_inside(xx, yy)
    #debugFile = open('grid_debug.dat','w')
    #debugFile.write('grid minimum {0:15.3f} grid maximum {1:15.3f}'.format( np.min(grid), np.max(grid)) )
    #debugFile.write(grid)
    #debugFile.close()
    
    # =========================================================================
    for hour in range(param['num_forecast_hours']):
        pnwDateString = datetime.strftime(time_vec_local[hour], "%Y-%m-%d %H:%M")
        
        file_wind_crop = '{0:s}/{1:s}{2:s}/{3:s}{2:s}_{4:02d}z_{5:02d}.dat'.format(param['fol_wind_crop'],
        param['folname_crop_prefix'],date_string,param['fname_prefix_wind'], zulu_hour, hour)
  
        windFile = open(file_wind_crop,"r")
        line = windFile.readline()
        u = np.zeros(Nw, dtype='d')
        v = np.zeros(Nw, dtype='d')

        for n in range(Nw):
            line = windFile.readline()
            split_line = line.split()
            u[n] = float(split_line[2])
            v[n] = float(split_line[3])

        wsp = np.sqrt(u**2 + v**2)


        wind = griddata(xyw,  wsp, (xi[None,:], yi[:,None]), method='cubic')
        uWind = griddata(xyw,  u, (xi[None,:], yi[:,None]), method='cubic')  # linear, nearest, cubic
        vWind = griddata(xyw,  v, (xi[None,:], yi[:,None]), method='cubic')

        # =============================== lowlands mask ==========================
        wind = ma.masked_where(grid < 0.0, wind)
        uWind = ma.masked_where(grid < 0.0, uWind)
        vWind = ma.masked_where(grid < 0.0, vWind)


        # ===================================== waves =============================
        i = 0
        j = 0
        hsign   = np.zeros((ny,nx), dtype='d')
        azimuth = np.zeros((ny,nx), dtype='d')
        uhsig   = np.zeros((ny,nx), dtype='d')
        vhsig   = np.zeros((ny,nx), dtype='d')
        
        file_model_output = '{:s}/temp/SWANOUT1_{:d}'.format(param['fol_model'],hour)
        inFile = open(file_model_output,'r')        
        
        lines = inFile.readlines()
        inFile.close()
        for n in range(len(lines)):
            split_line   = lines[n].split()
            hsign[j,i]   = m2ft*float(split_line[0])
            azimuth[j,i] = float(split_line[1])
            i += 1
            if i == Nx:
                i = 0
                j += 1
        hsign = ma.masked_where(hsign < 0.0, hsign)
        outFile = open('hsign.dat','w')
        outFile.write(hsign)
        outFile.close()
        maxElev = np.max(hsign)
        minElev = np.min(hsign)
        if daysMax < maxElev:
            daysMax = maxElev
        print('{0:2d} {1:8.6f} {2:8.6f}'.format(hour, maxElev, daysMax))
        azimuth = ma.masked_where(azimuth < -900.0, azimuth)
        cartesian = (450 - azimuth)%360.0
        uhsig = -np.cos(np.pi*cartesian/180.0)*hsign
        vhsig = -np.sin(np.pi*cartesian/180.0)*hsign
        
        # ===================================== plot =============================

        fig = plt.figure(figsize=(18.7,10.0))

        ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=4)   # rows, columns, row, column (0 for first)
        ax2 = plt.subplot2grid((5, 2), (0, 1), rowspan=4)
        ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=2, rowspan=1)

        #ax1.set_facecolor('slategray')
        #ax2.set_facecolor('slategray') # darkslategray
        #ax3.set_facecolor('silver')
        ax1.set_axis_bgcolor('white')
        ax2.set_axis_bgcolor('white') # darkslategray
        ax3.set_axis_bgcolor('silver')

        ax1.imshow(ls.hillshade(zT), cmap=cm.gray, extent=[ewMin, ewMax, nsMin, nsMax], zorder=4)

        #=============================================================================
        ax1.quiver(xw, yw, u, v, color='w', width=0.003, scale=100.0, zorder=6)
        sp = ax1.streamplot(xx, yy, uWind, vWind, color='w', density=1.5, arrowsize=0.01, zorder=6)
        levels = np.linspace(0.0, maxWind, 30)

        cs0 = ax1.contour( xx, yy, wind, levels, colors=['0.0', '0.5', '0.5', '0.5', '0.5'], zorder=7)   # linewidths=0.5, colors='k'
        plt.clabel(cs0, fmt='%4.2f', inline=True, fontsize=10)
        cs1 = ax1.contourf(xx, yy, wind, levels, cmap=plt.cm.jet, zorder=5)
        cb1 = plt.colorbar(cs1, ax=ax1)

        cb1.set_label('Wind Speed [m/s]')
        ax1.scatter(xw, yw, marker='o', c='k', s=10, zorder=3)
        ax1.set_title('Wind Forecast for {0:s} UTC'.format(pnwDateString))
        ax1.grid(True, zorder=6)
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax1.get_yticklabels(), visible=False)
        ax1.axis('equal')
        ax1.set_adjustable('box-forced')

        ax1.set_xlim(ewMin,ewMax)
        ax1.set_ylim(nsMin,nsMax)
        # =============================================================================
        ax2.imshow(ls.hillshade(zT), cmap=cm.gray, extent=[ewMin, ewMax, nsMin, nsMax])
        ax2.quiver(x[::skip,::skip], y[::skip,::skip], uhsig[::skip,::skip], vhsig[::skip,::skip], color='w', pivot='middle', width=0.003, scale=Scale, zorder=10)
        cs = ax2.contour(x, y, hsign, levels=Levels, colors=['0.0', '0.5', '1'], zorder=5)

        cs2 = ax2.contourf(x, y, hsign, levels=Levels, cmap=cm.jet, zorder=1)
        cb2 = plt.colorbar(cs2, ax=ax2)   # label='Pascal'

        cb2.set_label('Significant Wave Height [ft]')
        ax2.set_title('Wave Forecast for {0:s}'.format(pnwDateString))
        ax2.grid(True)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax2.get_yticklabels(), visible=False)
        ax2.axis('equal')
        ax2.set_adjustable('box-forced')

        ax2.set_xlim(ewMin,ewMax)
        ax2.set_ylim(nsMin,nsMax)

        # =============================================================================
        ax3.plot(time_vec_local,tide,'b-',lw=2)
        ax3.plot(time_vec_local[hour],tide[hour],'ro',ms=10)
#        ax3.set_xlim(-8.0,41.0)
        ax3.set_xlabel('Time in UTC')
        ax3.set_ylabel('Tide Prediction NAVD88 [m]')
#        ax3.set_ylim(dy[0],dy[1])
        ax3.grid(True)

        fileName = '{0:s}/wind_wave_skagit{1:s}_{2:02d}z_{3:02d}.png'.format(param['fol_plots'],date_string, zulu_hour, hour)
        plt.tight_layout()
        fig.savefig(fileName)
        #plt.show()
        plt.close(fig)
        #quit()


# General Forecast Plotting function
def plot_wind_wave_tide(date_string, zulu_hour, param, tide):
    # Constants
    m2ft = 3.28084  # Convert meters to feet
     
    #-------------Model Files-------------------------------------
    file_grid = '{:s}/{:s}'.format(param['fol_grid'],param['fname_grid'])

    # Time variables
    time_start_utc = datetime.strptime('{:s}{:02d}'.format(date_string,zulu_hour),'%Y%m%d%H')
    time_vec_utc = [time_start_utc + timedelta(hours=x) for x in range(param['num_forecast_hours'])]    
    time_vec_local = [time_start_utc - timedelta(hours=(x-param['gmt_offset'])) for x in range(param['num_forecast_hours'])]  
    
    #================== Skagit topography ========================
    NxT = 2500
    NyT = 2400
    Nx = 415
    Ny = 490
    xT = np.zeros((NyT,NxT), dtype='d')
    yT = np.zeros((NyT,NxT), dtype='d')
    zT = np.zeros((NyT,NxT), dtype='d')
    cropFile = open(file_grid_crop,'r')
    for j in range(NyT):
        for i in range(NxT):
            line = cropFile.readline()
            split = line.split()
            xT[j,i] = float(split[0])
            yT[j,i] = float(split[1])
            zT[j,i] = float(split[2])
    zT = np.ma.masked_where(zT <= 1.4, zT)
    ls = LightSource(azdeg=225, altdeg=60)


    hours = np.linspace(-7.0, 40.0, 48)

    plt.style.use('ggplot')

    x,y,nx,ny = show_grid.Grid(file_grid)
    dy = [-0.75,4.1]    # y-axis range for tide graph
    Vmax = 1.00         # wave height limit
    Scale = 9
    
    #Vmax = 0.70  # Nov 4: 0.32  # Nov 2: 0.4
    Levels = np.arange(0.0,Vmax,0.02)


    ewMin = 525000.0
    ewMax = 550000.0
    nsMin = 5343000.0
    nsMax = 5367000.0

    xLL =  param['xLL']
    yLL =  param['yLL']
    skip = 19

    daysMax = 0.0

    #deltax = np.linspace(0.0, (20700.0), Nx)
    deltax = np.linspace(0.0, (22000.0), Nx)
    deltay = np.linspace(0.0, (24450.0), Ny)
    
    xi = deltax + xLL
    yi = deltay + yLL
    
    
    # ===================================== wind grid ==============================
    hour = 0
    file_wind_crop = '{0:s}/{1:s}{2:s}/{3:s}{2:s}_{4:02d}z_{5:02d}.dat'.format(param['fol_wind_crop'],
        param['folname_crop_prefix'],date_string,param['fname_prefix_wind'], zulu_hour, hour)
    
    windFile = open(file_wind_crop,"r")
    line = windFile.readline()
    Nyw = int(line.split()[0])
    Nxw = int(line.split()[1])
    Nw = Nyw*Nxw
    print('Nxw {0:3d} Nyw {1:3d} Nw {2:5d}'.format(Nxw, Nyw, Nw))
    xw = np.zeros(Nw, dtype='d')
    yw = np.zeros(Nw, dtype='d')
    xyw = np.zeros((Nw,2), dtype='d')
    for n in range(Nw):
        line = windFile.readline()
        split_line = line.split()
        xw[n] = float(split_line[0])
        yw[n] = float(split_line[1])
        xyw[n,0] = xw[n]
        xyw[n,1] = yw[n]
        

    # =============================== lowlands mask ==========================
    shoreFile = open(file_shore_mask,'r')
    slines = shoreFile.readlines()
    shoreFile.close()
    xvert = []
    yvert = []
    for line in slines:
        splitLine = line.split()
        xvert.append(float(splitLine[0]))
        yvert.append(float(splitLine[1]))
    xx, yy = np.meshgrid(xi, yi)

    poly = Polygon(xvert, yvert)
    grid = poly.is_inside(xx, yy)
    #debugFile = open('grid_debug.dat','w')
    #debugFile.write('grid minimum {0:15.3f} grid maximum {1:15.3f}'.format( np.min(grid), np.max(grid)) )
    #debugFile.write(grid)
    #debugFile.close()
    
    # =========================================================================
    for hour in range(param['num_forecast_hours']):
        pnwDateString = datetime.strftime(time_vec_local[hour], "%Y-%m-%d %H:%M")
        
        file_wind_crop = '{0:s}/{1:s}{2:s}/{3:s}{2:s}_{4:02d}z_{5:02d}.dat'.format(param['fol_wind_crop'],
        param['folname_crop_prefix'],date_string,param['fname_prefix_wind'], zulu_hour, hour)
  
        windFile = open(file_wind_crop,"r")
        line = windFile.readline()
        u = np.zeros(Nw, dtype='d')
        v = np.zeros(Nw, dtype='d')

        for n in range(Nw):
            line = windFile.readline()
            split_line = line.split()
            u[n] = float(split_line[2])
            v[n] = float(split_line[3])

        wsp = np.sqrt(u**2 + v**2)


        wind = griddata(xyw,  wsp, (xi[None,:], yi[:,None]), method='cubic')
        uWind = griddata(xyw,  u, (xi[None,:], yi[:,None]), method='cubic')  # linear, nearest, cubic
        vWind = griddata(xyw,  v, (xi[None,:], yi[:,None]), method='cubic')

        # =============================== lowlands mask ==========================
        wind = ma.masked_where(grid < 0.0, wind)
        uWind = ma.masked_where(grid < 0.0, uWind)
        vWind = ma.masked_where(grid < 0.0, vWind)


        # ===================================== waves =============================
        i = 0
        j = 0
        hsign   = np.zeros((ny,nx), dtype='d')
        azimuth = np.zeros((ny,nx), dtype='d')
        uhsig   = np.zeros((ny,nx), dtype='d')
        vhsig   = np.zeros((ny,nx), dtype='d')
        
        file_model_output = '{:s}/temp/SWANOUT1_{:d}'.format(param['fol_model'],hour)
        inFile = open(file_model_output,'r')        
        
        lines = inFile.readlines()
        inFile.close()
        for n in range(len(lines)):
            split_line   = lines[n].split()
            hsign[j,i]   = m2ft*float(split_line[0])
            azimuth[j,i] = float(split_line[1])
            i += 1
            if i == Nx:
                i = 0
                j += 1
        hsign = ma.masked_where(hsign < 0.0, hsign)
        outFile = open('hsign.dat','w')
        outFile.write(hsign)
        outFile.close()
        maxElev = np.max(hsign)
        minElev = np.min(hsign)
        if daysMax < maxElev:
            daysMax = maxElev
        print('{0:2d} {1:8.6f} {2:8.6f}'.format(hour, maxElev, daysMax))
        azimuth = ma.masked_where(azimuth < -900.0, azimuth)
        cartesian = (450 - azimuth)%360.0
        uhsig = -np.cos(np.pi*cartesian/180.0)*hsign
        vhsig = -np.sin(np.pi*cartesian/180.0)*hsign
        
        # ===================================== plot =============================

        fig = plt.figure(figsize=(18.7,10.0))

        ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=4)   # rows, columns, row, column (0 for first)
        ax2 = plt.subplot2grid((5, 2), (0, 1), rowspan=4)
        ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=2, rowspan=1)

        #ax1.set_facecolor('slategray')
        #ax2.set_facecolor('slategray') # darkslategray
        #ax3.set_facecolor('silver')
        ax1.set_axis_bgcolor('white')
        ax2.set_axis_bgcolor('white') # darkslategray
        ax3.set_axis_bgcolor('silver')

        ax1.imshow(ls.hillshade(zT), cmap=cm.gray, extent=[ewMin, ewMax, nsMin, nsMax], zorder=4)

        #=============================================================================
        ax1.quiver(xw, yw, u, v, color='w', width=0.003, scale=100.0, zorder=6)
        sp = ax1.streamplot(xx, yy, uWind, vWind, color='w', density=1.5, arrowsize=0.01, zorder=6)
        levels = np.linspace(0.0, maxWind, 30)

        cs0 = ax1.contour( xx, yy, wind, levels, colors=['0.0', '0.5', '0.5', '0.5', '0.5'], zorder=7)   # linewidths=0.5, colors='k'
        plt.clabel(cs0, fmt='%4.2f', inline=True, fontsize=10)
        cs1 = ax1.contourf(xx, yy, wind, levels, cmap=plt.cm.jet, zorder=5)
        cb1 = plt.colorbar(cs1, ax=ax1)

        cb1.set_label('Wind Speed [m/s]')
        ax1.scatter(xw, yw, marker='o', c='k', s=10, zorder=3)
        ax1.set_title('Wind Forecast for {0:s} UTC'.format(pnwDateString))
        ax1.grid(True, zorder=6)
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax1.get_yticklabels(), visible=False)
        ax1.axis('equal')
        ax1.set_adjustable('box-forced')

        ax1.set_xlim(ewMin,ewMax)
        ax1.set_ylim(nsMin,nsMax)
        # =============================================================================
        ax2.imshow(ls.hillshade(zT), cmap=cm.gray, extent=[ewMin, ewMax, nsMin, nsMax])
        ax2.quiver(x[::skip,::skip], y[::skip,::skip], uhsig[::skip,::skip], vhsig[::skip,::skip], color='w', pivot='middle', width=0.003, scale=Scale, zorder=10)
        cs = ax2.contour(x, y, hsign, levels=Levels, colors=['0.0', '0.5', '1'], zorder=5)

        cs2 = ax2.contourf(x, y, hsign, levels=Levels, cmap=cm.jet, zorder=1)
        cb2 = plt.colorbar(cs2, ax=ax2)   # label='Pascal'

        cb2.set_label('Significant Wave Height [ft]')
        ax2.set_title('Wave Forecast for {0:s}'.format(pnwDateString))
        ax2.grid(True)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax2.get_yticklabels(), visible=False)
        ax2.axis('equal')
        ax2.set_adjustable('box-forced')

        ax2.set_xlim(ewMin,ewMax)
        ax2.set_ylim(nsMin,nsMax)

        # =============================================================================
        ax3.plot(time_vec_local,tide,'b-',lw=2)
        ax3.plot(time_vec_local[hour],tide[hour],'ro',ms=10)
#        ax3.set_xlim(-8.0,41.0)
        ax3.set_xlabel('Time in UTC')
        ax3.set_ylabel('Tide Prediction NAVD88 [m]')
#        ax3.set_ylim(dy[0],dy[1])
        ax3.grid(True)

        fileName = '{0:s}/wind_wave_skagit{1:s}_{2:02d}z_{3:02d}.png'.format(param['fol_plots'],date_string, zulu_hour, hour)
        plt.tight_layout()
        fig.savefig(fileName)
        #plt.show()
        plt.close(fig)
        #quit()
    
# Plot Bellingham Bay Winds
def plot_bbay_wind(date_string, zulu_hour, param):
    from netCDF4 import Dataset
    import pygrib
    import scipy.ndimage
    import shutil

    from op_functions import load_rotations    
    
    gmt_off = op_functions.get_gmt_offset()
    ms2mph = 2.237
    
    # Initialize    
    forecast_count = param['num_forecast_hours'] #Number of forecast hours
    hrdps_lamwest_file = param['hrdps_lamwest_file']
    hrdps_rotation_file = param['hrdps_rotation_file']
    grib_input_loc = '{0:s}/{1:s}{2:s}/'.format(param['fol_wind_grib'],param['folname_grib_prefix'],date_string)
    prefix_uwnd = param['hrdps_PrefixU'] 
    prefix_vwnd = param['hrdps_PrefixV'] 
    #bounds = param['crop_bounds']
    bounds = np.asarray([[270,117],[288,141]]) # Bellingham Bay
    
    # For Trimming files
    llcorner = [48.39, -122.88]
    urcorner = [48.87, -122.28]
    
    # For Trimming plots
    llcorner_plot = [48.42, -122.83]
    urcorner_plot = [48.79, -122.44]
    llcorner_plot_zoom = [48.64, -122.65]
    urcorner_plot_zoom = [48.785, -122.47]
    
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
    
    #---------------------------- Load bathy ------------------------
    fname = '../Bathymetry/nw_pacific_crm_v1.nc'
    fh = Dataset(fname,mode='r')
    bathy_lon = fh.variables['x'][:]
    bathy_lat = fh.variables['y'][:]
    bathy_elv = fh.variables['z'][:]
    fh.close()
    
    # Trim bathy file down (very large)
    lon_ind = [i for i,v in enumerate(bathy_lon) if v > llcorner[1] and v < urcorner[1]]
    lat_ind = [i for i,v in enumerate(bathy_lat) if v > llcorner[0] and v < urcorner[0]]
    p_inds = np.ix_(lat_ind,lon_ind)
    bathy_elv = bathy_elv[p_inds]
    bathy_lon = bathy_lon[lon_ind]
    bathy_lat = bathy_lat[lat_ind]
    
    
    #--------------------------------------------- UTM ----------------------------------------------
    #p = Proj(proj='utm', zone=10, ellps='WGS84')
    #degreesLat = np.zeros((Ny,Nx), dtype='d')
    #degreesLon = np.zeros((Ny,Nx), dtype='d')
    # Lons, Lats = p(degreesLon, degreesLat)  # note the capital L
    

    
    # ------------ Load in All Data --------------------------------
    # Will allow setting of max colorbar to be constant throughout
    max_speed = 0
    U10 = []
    V10 = []
    Speed = []
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
        
        u10 = u10[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
        v10 = v10[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
        
        
        # Rotate to earth relative with Bert-Derived rotations based on grid poitns (increased accuracy was derived for grid locations)
        for j in range(Nyr):
            for i in range(Nxr):
                R = np.matrix([ [np.cos(Theta[j,i]), -np.sin(Theta[j,i])], [np.sin(Theta[j,i]), np.cos(Theta[j,i])] ])
                rot = R.dot([u10[j,i],v10[j,i]])
                u10[j,i] = rot[0,0]
                v10[j,i] = rot[0,1]
                
        speed = ms2mph*np.sqrt(u10**2 + v10**2)
        
        # Keep track of max speed
        new_max = np.max(speed)
        if new_max > max_speed:
            max_speed = new_max
        
       
        # Save all varaibles into list of arrays        
        U10.append(u10)
        V10.append(v10)
        Speed.append(speed)
    
    # Control wind speed colors
    if max_speed < 15:
        max_speed_plot = 15
    elif max_speed < 30:
        max_speed_plot = 30
    elif max_speed < 45:
        max_speed_plot = 45
    else:
        max_speed_plot = 60
    
    #----------------------Make Plots----------------------------------
    for hour in range(forecast_count):
        # Local Time
        time_local = datetime.strptime('{:s}{:d}'.format(date_string,zulu_hour),'%Y%m%d%H')+timedelta(hours=(hour-gmt_off))
        
        # Interp onto high res grid to smooth 3x        
        hr3_speed = scipy.ndimage.zoom(Speed[hour],3)
        hr3_lon = scipy.ndimage.zoom(degreesLon,3)
        hr3_lat = scipy.ndimage.zoom(degreesLat,3)
 
        # Interp onto high res grid to smooth 2x        
        hr2_u10 = scipy.ndimage.zoom(U10[hour],2)
        hr2_v10 = scipy.ndimage.zoom(V10[hour],2)
        hr2_lon = scipy.ndimage.zoom(degreesLon,2)
        hr2_lat = scipy.ndimage.zoom(degreesLat,2)
        
        # Make REGIONAL BELLINGHAM Plot
        plt.figure(figsize=(7,6))
        #CS = plt.contourf(degreesLon, degreesLat, Speed[hour], levels=np.linspace(0, max_speed_plot, 16))
        CS = plt.contourf(hr3_lon, hr3_lat, hr3_speed, levels=np.linspace(0, max_speed_plot, 16))
        plt.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        #plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),units='width')
        plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),scale=20,scale_units='inches')
        plt.contourf(bathy_lon,bathy_lat,bathy_elv,levels=[0, 5000],hatches=['...'],alpha=0)
        cbar = plt.colorbar(CS)
        cbar.ax.set_ylabel('Wind Speed [mph]')
        CS.ax.ticklabel_format(useOffset=False)
        CS.ax.get_xaxis().get_major_formatter().set_scientific(False)
        CS.ax.set_ylim(llcorner_plot[0], urcorner_plot[0])
        CS.ax.set_xlim(llcorner_plot[1], urcorner_plot[1])
        CS.ax.set_xticks([-122.8, -122.6, -122.4])
        CS.ax.set_xticklabels(['122.8$^\circ$W', '122.6$^\circ$W', '122.4$^\circ$W'])
        CS.ax.set_yticks([48.5, 48.7])
        CS.ax.set_yticklabels(['48.5$^\circ$N', '48.7$^\circ$N'])
        CS.ax.set_title('Init: {:s} Z{:02d} - FCST HR {:d},  Local Time: {:s}'.format(date_string,zulu_hour,hour,time_local.strftime('%b %d %I:%S%p')))              
        plt.savefig('../GoogleDrive/BellinghamBay/Regional_Wind_HR{:02d}.png'.format(hour),dpi=200)
        plt.close()
        
        # Make ZOOMED BELLINGHAM Bay Plot
        plt.figure(figsize=(7,6))
        #CS = plt.contourf(degreesLon, degreesLat, Speed[hour], levels=np.linspace(0, max_speed_plot, 16))
        CS = plt.contourf(hr3_lon, hr3_lat, hr3_speed, levels=np.linspace(0, max_speed_plot, 16))
        plt.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        #plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),units='width')
        plt.quiver(hr2_lon,hr2_lat,hr2_u10,hr2_v10,color=(.5, .5, .5),scale=20,scale_units='inches')
        plt.contourf(bathy_lon,bathy_lat,bathy_elv,levels=[0, 5000],hatches=['...'],alpha=0)
        cbar = plt.colorbar(CS)
        cbar.ax.set_ylabel('Wind Speed [mph]')
        CS.ax.ticklabel_format(useOffset=False)
        CS.ax.get_xaxis().get_major_formatter().set_scientific(False)
        CS.ax.set_ylim(llcorner_plot_zoom[0], urcorner_plot_zoom[0])
        CS.ax.set_xlim(llcorner_plot_zoom[1], urcorner_plot_zoom[1])
        CS.ax.set_xticks([-122.6, -122.5])
        CS.ax.set_xticklabels(['122.6$^\circ$W', '122.5$^\circ$W'])
        CS.ax.set_yticks([48.65, 48.7, 48.75])
        CS.ax.set_yticklabels(['48.65$^\circ$N', '48.7$^\circ$N','48.75$^\circ$N'])
        CS.ax.set_title('Init: {:s} Z{:02d} - FCST HR {:d},  Local Time: {:s}'.format(date_string,zulu_hour,hour,time_local.strftime('%b %d %I:%S%p')))              
        plt.savefig('../GoogleDrive/BellinghamBay/BBay_Wind_HR{:02d}.png'.format(hour),dpi=200)
        plt.close()
        
        
    # Use ffmpeg to make animation
    os.chdir('../GoogleDrive/BellinghamBay/')
    ffmpegCommand = 'ffmpeg -f image2 -r 1 -i Regional_Wind_HR%02d.png -vcodec mpeg4 -y -vb 700k Regional_Wind.mp4'    
    err = subprocess.check_call(ffmpegCommand, shell=True)
    ffmpegCommand = 'ffmpeg -f image2 -r 1 -i BBay_Wind_HR%02d.png -vcodec mpeg4 -y -vb 700k BBay_Wind.mp4'    
    err = subprocess.check_call(ffmpegCommand, shell=True)
    os.chdir('../../SkagitOperational')
                
    # Move png files to image folder
    for hour in range(forecast_count):
        shutil.move('../GoogleDrive/BellinghamBay/Regional_Wind_HR{:02d}.png'.format(hour),
                    '../GoogleDrive/BellinghamBay/ImageFiles/Regional_Wind_HR{:02d}.png'.format(hour))
        shutil.move('../GoogleDrive/BellinghamBay/BBay_Wind_HR{:02d}.png'.format(hour),
                    '../GoogleDrive/BellinghamBay/ImageFiles/BBay_Wind_HR{:02d}.png'.format(hour))
                
                
                
