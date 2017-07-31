# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 13:18:39 2017

@author: crosby
"""

# Standard libraries
from netCDF4 import Dataset
import pygrib
import scipy.ndimage
import shutil
import numpy as np
import pyproj
import subprocess
import os
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib import dates as mdates
from datetime import datetime, timedelta

# Custom libraries
import op_functions 
import download_ndbc

# Returns size of HRDPS predictions from LandMask
def load_hrdps_mask(date_string, zulu_hour, param):
    grib_input_loc = '{0:s}/{1:s}{2:s}/'.format(param['fol_wind_grib'],param['folname_grib_prefix'],date_string)
    maskFileName = '{0:s}/{1:s}{2:s}{3:02d}_P000-00.grib2'.format(grib_input_loc,
        param['hrdps_PrefixLAND'], date_string, zulu_hour)
    grbl = pygrib.open(maskFileName)
    grblL = grbl.select(name='Land-sea mask')[0]
    Land = grblL.values
    Land = np.asarray(Land)
    Ny = np.shape(Land)[0]
    Nx = np.shape(Land)[1]
    #Land = Land[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]   
    return (Nx,Ny)

# Returns locations of HRDPS pred in lat/lon
def load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file,bounds):
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
    degLat = degreesLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    degLon = degreesLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    return (degLat,degLon)

def load_bathy_nc(param):
    fname = '../Bathymetry/nw_pacific_crm_v1.nc'
    # For Trimming files & plots (lat/lons)
    lat_bounds = param['plot_bounds'][0]
    lon_bounds = param['plot_bounds'][1]
    fh = Dataset(fname,mode='r')
    bathy_lon = fh.variables['x'][:]
    bathy_lat = fh.variables['y'][:]
    bathy_elv = fh.variables['z'][:]
    fh.close()
    # Trim bathy file down (very large)
    lon_ind = [i for i,v in enumerate(bathy_lon) if v > lon_bounds[0] and v < lon_bounds[1]]
    lat_ind = [i for i,v in enumerate(bathy_lat) if v > lat_bounds[0] and v < lat_bounds[1]]
    p_inds = np.ix_(lat_ind,lon_ind)
    bathy_elv = bathy_elv[p_inds]
    bathy_lon = bathy_lon[lon_ind]
    bathy_lat = bathy_lat[lat_ind]
    return (bathy_elv, bathy_lat, bathy_lon)
    
def load_model_grid(param):
    # Set some constants that vary from model to model
    line_meteo_grid_size= param['line_meteo_grid_size']     # Line number in meteo grid with Nx, Ny
    line_header_skip    = param['line_header_skip']    # Number of header lines in meteo file
    fol_grid            = param['fol_grid']
    fname_meteo         = param['fname_meteo_grid']    
    
    # Load D3D grid
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
    return easting, northing, Nx, Ny
    
def load_hsig_pred(param,Nx,Ny):
    m2ft = 3.28084  # Convert meters to feet
            
    Hsig = []
    Uhsig = []
    Vhsig = []
    maxHsig = 0
    for hour in range(param['num_forecast_hours']):
        i = 0
        j = 0
        hsig   = np.zeros((Ny,Nx), dtype='d')
        azimuth = np.zeros((Ny,Nx), dtype='d')
        uhsig   = np.zeros((Ny,Nx), dtype='d')
        vhsig   = np.zeros((Ny,Nx), dtype='d')
        
        file_model_output = '{:s}/temp/SWANOUT1_{:d}'.format(param['fol_model'],hour)
        inFile = open(file_model_output,'r')        
        
        lines = inFile.readlines()
        inFile.close()
        for n in range(len(lines)):
            split_line   = lines[n].split()
            hsig[j,i]   = m2ft*float(split_line[0])
            azimuth[j,i] = float(split_line[1])
            i += 1
            if i == Nx:
                i = 0
                j += 1
        hsig = np.ma.masked_where(hsig < 0.0, hsig)
        temp = np.max(hsig)
        if temp > maxHsig:
            maxHsig = temp
        #outFile = open('hsign.dat','w')
        #outFile.write(hsign)
        #outFile.close()
        #maxElev = np.max(hsign)
        #minElev = np.min(hsign)
        #if daysMax < maxElev:
        #    daysMax = maxElev
        #print('{0:2d} {1:8.6f} {2:8.6f}'.format(hour, maxElev, daysMax))
        #azimuth = ma.masked_where(azimuth < -900.0, azimuth)
        cartesian = (450 - azimuth)%360.0
        uhsig = -np.cos(np.pi*cartesian/180.0)*hsig
        vhsig = -np.sin(np.pi*cartesian/180.0)*hsig
        Hsig.append(hsig)
        Uhsig.append(uhsig)
        Vhsig.append(vhsig)
    return (Hsig, Uhsig, Vhsig, maxHsig)
    
def load_hrdps_wind(date_string, zulu_hour, param, Nx, Ny):
    ms2mph = 2.237    
    
    # Grib cropping bounds (indices)
    bounds = param['crop_bounds'] 
    
    # file locations    
    grib_input_loc = '{0:s}/{1:s}{2:s}/'.format(param['fol_wind_grib'],param['folname_grib_prefix'],date_string)
    prefix_uwnd = param['hrdps_PrefixU'] 
    prefix_vwnd = param['hrdps_PrefixV'] 
    
    # Load rotations
    Theta = op_functions.load_rotations(param['hrdps_rotation_file'],Ny,Nx)
    Theta = Theta[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    Nyr = np.shape(Theta)[0]
    Nxr = np.shape(Theta)[1]    
    
    max_speed = 0
    U10 = []
    V10 = []
    Speed = []
    for hour in range(param['num_forecast_hours']):
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
        
    return (Speed,U10,V10,max_speed)


def plot_bbay_wind_wave(date_string, zulu_hour, param):
    # Get time offset  
    gmt_off = op_functions.get_gmt_offset()
    
    # Initialize    
    forecast_count = param['num_forecast_hours'] #Number of forecast hours
    hrdps_lamwest_file = param['hrdps_lamwest_file']
    
    # Grib cropping bounds (indices)
    bounds = param['crop_bounds']
    
    # For Trimming files & plots (lat/lons)
    lat_bounds = param['plot_bounds'][0]
    lon_bounds = param['plot_bounds'][1]

    
    #----------------------- Load up HRDP Land Mask----------------------------------------
    (Nx,Ny) = load_hrdps_mask(date_string, zulu_hour, param)
    
    #------------------------------- Load lat/lon positions of hrdps ---------------------------------
    (degLat,degLon) = load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file,bounds)
        
    #---------------------------- Load bathy ----------------------------------
    (bathy_elv, bathy_lat, bathy_lon) = load_bathy_nc(param)
       
    #--------------------------- Load D3D Grid --------------------------------
    x,y,nx,ny = load_model_grid(param)   

    #--------------------------- Load Hsig Pred--------------------------------
    (Hsig, Uhsig, Vhsig, max_hsig) = load_hsig_pred(param,nx,ny)
    
    #-------------Convert Model grid from utm to lat/lon ----------------------        
    p = pyproj.Proj(proj='utm', zone=10, ellps='WGS84')
    m_lon, m_lat = p(x,y,inverse=True) 
    
  
    # ------------ Load in All Wind Grib Data --------------------------------
    (Speed,U10,V10,max_speed) = load_hrdps_wind(date_string, zulu_hour, param, Nx, Ny)

        
    # --------------------- Set wind speed max ------------------------
    if max_speed < 15:
        max_speed_plot = 15
    elif max_speed < 30:
        max_speed_plot = 30
    elif max_speed < 45:
        max_speed_plot = 45
    else:
        max_speed_plot = 60
    
    if max_hsig < 1:
        max_hsig_plot = 1
    elif max_hsig < 3:
        max_hsig_plot = 3
    else:
        max_hsig_plot = 6
    
    #--------------------------------------------------------------------------
    #------------------------------Make Plots----------------------------------
    #--------------------------------------------------------------------------
    for hour in range(forecast_count):
        # Local Time
        time_local = datetime.strptime('{:s}{:d}'.format(date_string,zulu_hour),'%Y%m%d%H')+timedelta(hours=(hour-gmt_off))
        
        # Interp onto high res grid to smooth 3x        
        hr3_speed = scipy.ndimage.zoom(Speed[hour],3)
        hr3_lon = scipy.ndimage.zoom(degLon,3)
        hr3_lat = scipy.ndimage.zoom(degLat,3)
 
        # Interp onto high res grid to smooth 2x        
        hr2_u10 = scipy.ndimage.zoom(U10[hour],2)
        hr2_v10 = scipy.ndimage.zoom(V10[hour],2)
        hr2_lon = scipy.ndimage.zoom(degLon,2)
        hr2_lat = scipy.ndimage.zoom(degLat,2)
        
        # Set up Plots 
        fig = plt.figure(figsize=(8.,7.))

        #ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=4)   # rows, columns, row, column (0 for first)
        #ax2 = plt.subplot2grid((5, 2), (0, 1), rowspan=4)
        #ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=2, rowspan=1)
        
        gs = gridspec.GridSpec(20,2)
        gs.update(left=0.075, right=0.98, top=0.95, bottom=0.075, wspace=0.05)
        ax1 = plt.subplot(gs[:-2,0])
        ax2 = plt.subplot(gs[:-2,1])
        ax1c = plt.subplot(gs[-1,0])
        ax2c = plt.subplot(gs[-1,1])

        ax1.set_axis_bgcolor('white')
        ax2.set_axis_bgcolor('white') 
        #ax3.set_axis_bgcolor('silver')        
                
        # Plot Winds
        CS = ax1.contourf(hr3_lon, hr3_lat, hr3_speed, levels=np.linspace(0, max_speed_plot, 16))
        ax1.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        #plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),units='width')
        ax1.quiver(hr2_lon,hr2_lat,hr2_u10,hr2_v10,color=(.5, .5, .5),scale=40,scale_units='inches')
        ax1.contourf(bathy_lon,bathy_lat,bathy_elv,levels=[0, 5000],hatches=['...'],alpha=0)
        #cbar = plt.colorbar(CS, ax=ax1, orientation='horizontal')
        cbar = plt.colorbar(CS, cax=ax1c, orientation='horizontal', )        
        cbar.ax.set_xlabel('Wind Speed [mph]')
        CS.ax.ticklabel_format(useOffset=False)
        CS.ax.get_xaxis().get_major_formatter().set_scientific(False)
        CS.ax.set_ylim(lat_bounds[0], lat_bounds[1])
        CS.ax.set_xlim(lon_bounds[0], lon_bounds[1])
        CS.ax.set_xticks([-122.6, -122.5])
        CS.ax.set_xticklabels(['122.6$^\circ$W', '122.5$^\circ$W'])
        CS.ax.set_yticks([48.6, 48.7])
        CS.ax.set_yticklabels(['48.6$^\circ$N', '48.7$^\circ$N'])
        #CS.ax.set_title('Init: {:s} Z{:02d} - FCST HR {:d}, Local Time: {:s}'.format(date_string,zulu_hour,hour,time_local.strftime('%b %d %I:%S%p')))              
        plt.suptitle('Init: {:s} Z{:02d} - FCST HR {:d}, Local Time: {:s}'.format(date_string,zulu_hour,hour,time_local.strftime('%b %d %I:%S%p')))              
        
        quiver_skip = 6
        CS = ax2.contourf(m_lon, m_lat, Hsig[hour], levels=np.linspace(0, max_hsig_plot, 31))  
        ax2.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        ax2.quiver(m_lon[::quiver_skip,::quiver_skip], m_lat[::quiver_skip,::quiver_skip],
                   Uhsig[hour][::quiver_skip,::quiver_skip],Vhsig[hour][::quiver_skip,::quiver_skip]
                   ,color=(.5, .5, .5))#,scale=2,scale_units='inches')
        ax2.contourf(bathy_lon,bathy_lat,bathy_elv,levels=[0, 5000],hatches=['...'],alpha=0)
        cbar = plt.colorbar(CS, cax=ax2c, orientation='horizontal')
        cbar.ax.set_xlabel('Wave Height [ft]')
        CS.ax.ticklabel_format(useOffset=False)
        CS.ax.get_xaxis().get_major_formatter().set_scientific(False)
        CS.ax.set_ylim(lat_bounds[0], lat_bounds[1])
        CS.ax.set_xlim(lon_bounds[0], lon_bounds[1])
        CS.ax.set_xticks([-122.6, -122.5])
        CS.ax.set_xticklabels(['122.6$^\circ$W', '122.5$^\circ$W'])
        CS.ax.set_yticks([48.6, 48.7])
        CS.ax.set_yticklabels([])     
        
        fname = '{:s}/{:s}/{:s}WindWave'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'])
        fig.savefig('{:s}_{:02d}.png'.format(fname,hour),dpi=150)
        plt.close()
        
    # Use ffmpeg to make animation
    os.chdir('{:s}/{:s}/'.format(param['fol_google'],param['folname_google']))
    ffmpegCommand = r'ffmpeg -f image2 -r 1 -i {0:s}WindWave_%02d.png -vcodec mpeg4 -y -vb 700k {0:s}WindWave.mp4'.format(param['fname_prefix_plot'])    
    subprocess.check_call(ffmpegCommand, shell=True)
    os.chdir('../../SkagitOperational')
                
    # Move png files to image folder
    for hour in range(forecast_count):
        fname_src = '{:s}/{:s}/{:s}WindWave_{:02d}.png'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'],hour)
        fname_dest = '{:s}/{:s}/ImageFiles/{:s}WindWave_{:02d}.png'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'],hour)
        shutil.move(fname_src,fname_dest)
                
                
def plot_bbay_wind_wave_obs(date_string, zulu_hour, param):
    # Get time offset  
    gmt_off = op_functions.get_gmt_offset()
    
    # Initialize    
    forecast_count = param['num_forecast_hours'] #Number of forecast hours
    hrdps_lamwest_file = param['hrdps_lamwest_file']
    
    # Grib cropping bounds (indices)
    bounds = param['crop_bounds']
    
    # For Trimming files & plots (lat/lons)
    lat_bounds = param['plot_bounds'][0]
    lon_bounds = param['plot_bounds'][1]
   
    #----------------------- Load up HRDP Land Mask----------------------------------------
    (Nx,Ny) = load_hrdps_mask(date_string, zulu_hour, param)
    
    #------------------------------- Load lat/lon positions of hrdps ---------------------------------
    (degLat,degLon) = load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file,bounds)
        
    #---------------------------- Load bathy ----------------------------------
    (bathy_elv, bathy_lat, bathy_lon) = load_bathy_nc(param)
       
    #--------------------------- Load D3D Grid --------------------------------
    x,y,nx,ny = load_model_grid(param)   

    #--------------------------- Load Hsig Pred--------------------------------
    (Hsig, Uhsig, Vhsig, max_hsig) = load_hsig_pred(param,nx,ny)
    
    #-------------Convert Model grid from utm to lat/lon ----------------------        
    p = pyproj.Proj(proj='utm', zone=10, ellps='WGS84')
    m_lon, m_lat = p(x,y,inverse=True) 
    
    # ------------ Load in All Wind Grib Data --------------------------------
    (Speed,U10,V10,max_speed) = load_hrdps_wind(date_string, zulu_hour, param, Nx, Ny)

    # ----------------Grab NDBC Data ------------------------------------------
    (ndbc_time,ndbc_speed,ndbc_dir) = download_ndbc.get_ndbc_realtime(param['ndbc_sta_id'])
    ndbc_time = [t - timedelta(hours=gmt_off) for t in ndbc_time] # Convert from UTC to local

    #----------------- Find close model grid cell to ndbc ---------------------    
    dist = np.add(np.square(np.array(degLon)-param['ndbc_lon']),np.square(np.array(degLat)-param['ndbc_lat']))
    (I_lon, I_lat) = np.where(dist == np.min(dist))
    ndbc_pred = [s[I_lon, I_lat] for s in Speed]        
        
    # -------------- Set wind speed and wave height max ------------------------
    if max_speed < 15:
        max_speed_plot = 15
    elif max_speed < 30:
        max_speed_plot = 30
    elif max_speed < 45:
        max_speed_plot = 45
    else:
        max_speed_plot = 60
    
    if max_hsig < 1:
        max_hsig_plot = 1
        bins_hsig_plot = 21
    elif max_hsig < 3:
        max_hsig_plot = 3
        bins_hsig_plot = 31
    else:
        max_hsig_plot = 6
        bins_hsig_plot = 31
    
    time_vec_local = [datetime.strptime('{:s}{:d}'.format(date_string,zulu_hour),'%Y%m%d%H')+timedelta(hours=(hour-gmt_off)) for hour in range(48)]    
    
    #--------------------------------------------------------------------------
    #------------------------------Make Plots----------------------------------
    #--------------------------------------------------------------------------  
    for hour in range(forecast_count):
        # Local Time
        time_local = datetime.strptime('{:s}{:d}'.format(date_string,zulu_hour),'%Y%m%d%H')+timedelta(hours=(hour-gmt_off))
                      
        # Interp onto high res grid to smooth 3x        
        hr3_speed = scipy.ndimage.zoom(Speed[hour],3)
        hr3_lon = scipy.ndimage.zoom(degLon,3)
        hr3_lat = scipy.ndimage.zoom(degLat,3)
 
        # Interp onto high res grid to smooth 2x        
        hr2_u10 = scipy.ndimage.zoom(U10[hour],2)
        hr2_v10 = scipy.ndimage.zoom(V10[hour],2)
        hr2_lon = scipy.ndimage.zoom(degLon,2)
        hr2_lat = scipy.ndimage.zoom(degLat,2) 
        
        # Set up Plots 
        fig = plt.figure(figsize=(8.,8.))

        #ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=4)   # rows, columns, row, column (0 for first)
        #ax2 = plt.subplot2grid((5, 2), (0, 1), rowspan=4)
        #ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=2, rowspan=1)
        
        gs = gridspec.GridSpec(30,2)
        gs.update(left=0.075, right=0.98, top=0.95, bottom=0.075, wspace=0.05)
        ax1 = plt.subplot(gs[:-9,0])
        ax2 = plt.subplot(gs[:-9,1])
        ax1c = plt.subplot(gs[-8,0])
        ax2c = plt.subplot(gs[-8,1])
        ax3 = plt.subplot(gs[-5:,:])

        ax1.set_axis_bgcolor('white')
        ax2.set_axis_bgcolor('white') 
        #ax3.set_axis_bgcolor('silver')        
                
        # Plot Winds
        CS = ax1.contourf(hr3_lon, hr3_lat, hr3_speed, levels=np.linspace(0, max_speed_plot, 16))
        ax1.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        #plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),units='width')
        ax1.quiver(hr2_lon,hr2_lat,hr2_u10,hr2_v10,color=(.5, .5, .5),scale=40,scale_units='inches')
        ax1.contourf(bathy_lon,bathy_lat,bathy_elv,levels=[0, 5000],hatches=['...'],alpha=0)
        ax1.plot(param['ndbc_lon'],param['ndbc_lat'],'m*',markersize=15,)
        #cbar = plt.colorbar(CS, ax=ax1, orientation='horizontal')
        cbar = plt.colorbar(CS, cax=ax1c, orientation='horizontal', )        
        cbar.ax.set_xlabel('Wind Speed [mph]')
        CS.ax.ticklabel_format(useOffset=False)
        CS.ax.get_xaxis().get_major_formatter().set_scientific(False)
        CS.ax.set_ylim(lat_bounds[0], lat_bounds[1])
        CS.ax.set_xlim(lon_bounds[0], lon_bounds[1])
        CS.ax.set_xticks([-122.6, -122.5])
        CS.ax.set_xticklabels(['122.6$^\circ$W', '122.5$^\circ$W'])
        CS.ax.set_yticks([48.6, 48.7])
        CS.ax.set_yticklabels(['48.6$^\circ$N', '48.7$^\circ$N'])
        #CS.ax.set_title('Init: {:s} Z{:02d} - FCST HR {:d}, Local Time: {:s}'.format(date_string,zulu_hour,hour,time_local.strftime('%b %d %I:%S%p')))              
        plt.suptitle('Init: {:s} Z{:02d} - FCST HR {:d}, Local Time: {:s}'.format(date_string,zulu_hour,hour,time_local.strftime('%b %d %I:%S%p')))              
        
        quiver_skip = 6
        CS = ax2.contourf(m_lon, m_lat, Hsig[hour], levels=np.linspace(0, max_hsig_plot, bins_hsig_plot))  
        ax2.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        ax2.quiver(m_lon[::quiver_skip,::quiver_skip], m_lat[::quiver_skip,::quiver_skip],
                   Uhsig[hour][::quiver_skip,::quiver_skip],Vhsig[hour][::quiver_skip,::quiver_skip]
                   ,color=(.5, .5, .5))#,scale=2,scale_units='inches')
        ax2.contourf(bathy_lon,bathy_lat,bathy_elv,levels=[0, 5000],hatches=['...'],alpha=0)
        cbar = plt.colorbar(CS, cax=ax2c, orientation='horizontal')
        cbar.ax.set_xlabel('Wave Height [ft]')
        CS.ax.ticklabel_format(useOffset=False)
        CS.ax.get_xaxis().get_major_formatter().set_scientific(False)
        CS.ax.set_ylim(lat_bounds[0], lat_bounds[1])
        CS.ax.set_xlim(lon_bounds[0], lon_bounds[1])
        CS.ax.set_xticks([-122.6, -122.5])
        CS.ax.set_xticklabels(['122.6$^\circ$W', '122.5$^\circ$W'])
        CS.ax.set_yticks([48.6, 48.7])
        CS.ax.set_yticklabels([])     
        
        ax3.plot(ndbc_time,ndbc_speed,'k.',label='Observations')        
        ax3.plot(time_vec_local,ndbc_pred,'b',label='Predictions')
        ax3.set_ylabel('Wind Speed [mph]')
        ax3.legend(frameon=False, prop={'size':10})
                
        y_top = ax3.get_ylim()
        ax3.plot([time_vec_local[hour],time_vec_local[hour]],[0,y_top[1]],color=(.5,.5,.5),zorder=0)

        days = mdates.DayLocator()
        hours = mdates.HourLocator()
        days_fmt = mdates.DateFormatter('%m/%d %H:%M')
        ax3.xaxis.set_major_locator(days)
        ax3.xaxis.set_major_formatter(days_fmt)
        ax3.xaxis.set_minor_locator(hours)
              

        
        fname = '{:s}/{:s}/{:s}WindWave'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'])
        fig.savefig('{:s}_{:02d}.png'.format(fname,hour),dpi=150)
        plt.close()
        
    # Use ffmpeg to make animation
    os.chdir('{:s}/{:s}/'.format(param['fol_google'],param['folname_google']))
    ffmpegCommand = r'ffmpeg -f image2 -r 1 -i {0:s}WindWave_%02d.png -vcodec mpeg4 -y -vb 700k {0:s}WindWave.mp4'.format(param['fname_prefix_plot'])    
    subprocess.check_call(ffmpegCommand, shell=True)
    os.chdir('../../SkagitOperational')
                
    # Move png files to image folder
    for hour in range(forecast_count):
        fname_src = '{:s}/{:s}/{:s}WindWave_{:02d}.png'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'],hour)
        fname_dest = '{:s}/{:s}/ImageFiles/{:s}WindWave_{:02d}.png'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'],hour)
        shutil.move(fname_src,fname_dest)               
     
     
     
# Use for debugging     
if __name__ == '__main__':
    import get_param
    (date_string, zulu_hour) = op_functions.latest_hrdps_forecast()
    #date_string = '20170731'
    #zulu_hour = 0
    param = get_param.get_param_bbay()
    plot_bbay_wind_wave_obs(date_string, zulu_hour, param)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    