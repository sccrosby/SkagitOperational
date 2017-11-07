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
import download_ncdc
import davis_weather

def wrapTo360(angle):
    while angle < 0 or angle >= 360:
        if angle < 0:
            angle = angle + 360
        else:
            angle = angle - 360
    return angle

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
def load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file):
    degLat = np.zeros((Ny,Nx), dtype='d')
    degLon = np.zeros((Ny,Nx), dtype='d')
    indexFile = open(hrdps_lamwest_file,'r')
    for line in indexFile:
        split = line.split()
        i = int(split[0])-1
        j = int(split[1])-1
        degLat[j,i] = float(split[2])
        degLon[j,i] = float(split[3])
    indexFile.close()
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
    #print("Nx, Ny", Nx, Ny)
    
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

def load_hrdps_slp(date_string, zulu_hour, param, Nx, Ny):
    # Grib cropping bounds (indices)
    bounds = param['crop_bounds'] 
    
    # file locations    
    grib_input_loc = '{0:s}/{1:s}{2:s}/'.format(param['fol_wind_grib'],param['folname_grib_prefix'],date_string)
    prefix_p = param['hrdps_PrefixP'] 
    
    Slp = []
    for hour in range(param['num_forecast_hours']):
        #Input grib file names            
        PwindFileName = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, prefix_p, date_string, zulu_hour, hour)
       
        # Open grib
        grbsp = pygrib.open(PwindFileName)
        grbp  = grbsp.select(name='Pressure reduced to MSL')[0]
        
        slp = grbp.values # same as grb['values']
        slp = np.asarray(slp)        
        
        slp = slp[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
              
        # Save all varaibles into list of arrays        
        Slp.append(slp)
        
    return Slp
    
    
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
    Dir= []
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
        direction = 90.0 - np.arctan2(v10,u10)*180.0/np.pi + 180.0# Calc direction coming from in compass coords in 0-360 range

        
        # Keep track of max speed
        new_max = np.max(speed)
        if new_max > max_speed:
            max_speed = new_max
              
        # Save all varaibles into list of arrays        
        U10.append(u10)
        V10.append(v10)
        Speed.append(speed)
        Dir.append(direction)
        
    return (Speed,Dir,U10,V10,max_speed)
    
def load_hrdps_point_hindcast(date_string, zulu_hour, param, Nx, Ny, pt_lat, pt_lon, num_goback):
    # num_goback is the number of historic forecasts to load in
    ms2mph = 2.237    
    use_forecast = [2,3,4,5,6,7] #ignore first two hours (odd)

    # Set current working forecast
    init_time = datetime.strptime('{:s} {:d}'.format(date_string,zulu_hour),'%Y%m%d %H')    
 
    # Load locations
    (degLat,degLon) = load_hrdps_lamwest_locs(Nx,Ny,param['hrdps_lamwest_file'])

    # Find closest model grid cell to ndbc     
    dist = np.add(np.square(np.array(degLon)-pt_lon),np.square(np.array(degLat)-pt_lat))
    (I_lon, I_lat) = np.where(dist == np.min(dist))   

    # Load rotations for winds
    Theta = op_functions.load_rotations(param['hrdps_rotation_file'],Ny,Nx)
    R = np.matrix([ [np.cos(Theta[I_lon, I_lat]).item(0), -np.sin(Theta[I_lon, I_lat]).item(0)], [np.sin(Theta[I_lon, I_lat]).item(0), np.cos(Theta[I_lon, I_lat]).item(0)] ])
   
    # Set grib file name prefixes
    prefix_uwnd = param['hrdps_PrefixU'] 
    prefix_vwnd = param['hrdps_PrefixV']     
    prefix_slp = param['hrdps_PrefixP']

    Speed = []
    Dir = []
    Slp = []
    Time = []
    # Loop over forecasts (earliest first)
    for forecast in range(num_goback,0,-1):
        # Step back to previous forecasts
        forecast_time = init_time-timedelta(hours=6*forecast)
        date_string_hindcast = forecast_time.strftime('%Y%m%d')
        zulu_hour_hindcast = forecast_time.hour     
        
        # file locations    
        grib_input_loc = '{0:s}/{1:s}{2:s}/'.format(param['fol_wind_grib'],param['folname_grib_prefix'],date_string_hindcast)
        
        # Loop over forecast hours
        for hour in use_forecast:
            #Input grib file names            
            UwindFileName = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, prefix_uwnd, date_string_hindcast, zulu_hour_hindcast, hour)
            VwindFileName = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, prefix_vwnd, date_string_hindcast, zulu_hour_hindcast, hour)
            PwindFileName = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, prefix_slp, date_string_hindcast, zulu_hour_hindcast, hour)
           
            # Open grib
            grbsu = pygrib.open(UwindFileName)
            grbu  = grbsu.select(name='10 metre U wind component')[0]
            grbsv = pygrib.open(VwindFileName)
            grbv  = grbsv.select(name='10 metre V wind component')[0]    
            grbsp = pygrib.open(PwindFileName)
            grbp  = grbsp.select(name='Pressure reduced to MSL')[0]   
            u10 = grbu.values # same as grb['values']
            v10 = grbv.values
            slp = grbp.values
            u10 = np.asarray(u10)
            v10 = np.asarray(v10)
            slp = np.asarray(slp)
            
            # Select location
            u10 = u10[I_lon, I_lat]
            v10 = v10[I_lon, I_lat]
            slp = slp[I_lon, I_lat]/1000 # Convert to kPa
            
            # Rotate to earth-relative
            rot = R.dot([u10.item(0),v10.item(0)])
            u10 = rot[0,0]
            v10 = rot[0,1]
                    
            # Calc Speed
            speed = ms2mph*np.sqrt(u10**2 + v10**2)
            # Calc direction coming from in compass coords in 0-360 range
            direction = wrapTo360(90.0 - np.arctan2(v10,u10)*180.0/np.pi + 180.0)
            # Set time
            time = forecast_time + timedelta(hours=hour)
                              
            # Append to growing array       
            Dir.append(direction)
            Speed.append(speed)
            Slp.append(slp)
            Time.append(time)

    return (Time, Speed, Dir, Slp)    
    
    
# Plot Bellingham Bay Winds (both Regional and Zoom)
def plot_bbay_wind(date_string, zulu_hour, param):
#    from netCDF4 import Dataset
#    import pygrib
#    import scipy.ndimage
#    import shutil

    from op_functions import load_rotations    
    
    gmt_off = op_functions.get_gmt_offset()
    
    # Initialize    
    forecast_count = param['num_forecast_hours'] #Number of forecast hours
    hrdps_lamwest_file = param['hrdps_lamwest_file']
    hrdps_rotation_file = param['hrdps_rotation_file']
    bounds = param['crop_bounds']
    
    
    # For Trimming plots
    llcorner_plot = [48.42, -122.83]
    urcorner_plot = [48.79, -122.40]
    llcorner_plot_zoom = [48.64, -122.65]
    urcorner_plot_zoom = [48.785, -122.47]
    
    #----------------------- Load up HRDP Land Mask----------------------------------------
    (Nx,Ny) = load_hrdps_mask(date_string, zulu_hour, param)
  
    #------------------------------- Load lat/lon positions of hrdps ---------------------------------
    (degLat,degLon) = load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file)
    degLat = degLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    degLon = degLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    
    #---------------------------- Load rotations---------------------
    Theta = load_rotations(hrdps_rotation_file,Ny,Nx)
    Theta = Theta[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    
    #---------------------------- Load bathy ------------------------
    fname = '../Bathymetry/nw_pacific_crm_v1.nc'
    fh = Dataset(fname,mode='r')
    bathy_lon = fh.variables['x'][:]
    bathy_lat = fh.variables['y'][:]
    bathy_elv = fh.variables['z'][:]
    fh.close()
    
    # Trim bathy file down (very large)
    lon_ind = [i for i,v in enumerate(bathy_lon) if v > llcorner_plot[1] and v < urcorner_plot[1]]
    lat_ind = [i for i,v in enumerate(bathy_lat) if v > llcorner_plot[0] and v < urcorner_plot[0]]
    p_inds = np.ix_(lat_ind,lon_ind)
    bathy_elv = bathy_elv[p_inds]
    bathy_lon = bathy_lon[lon_ind]
    bathy_lat = bathy_lat[lat_ind]
    
   
    # ------------ Load in All Wind Grib Data --------------------------------
    (Speed,Dir,U10,V10,max_speed) = load_hrdps_wind(date_string, zulu_hour, param, Nx, Ny)

    
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
        hr3_lon = scipy.ndimage.zoom(degLon,3)
        hr3_lat = scipy.ndimage.zoom(degLat,3)
 
        # Interp onto high res grid to smooth 2x        
        hr2_u10 = scipy.ndimage.zoom(U10[hour],2)
        hr2_v10 = scipy.ndimage.zoom(V10[hour],2)
        hr2_lon = scipy.ndimage.zoom(degLon,2)
        hr2_lat = scipy.ndimage.zoom(degLat,2)
        
        # Make REGIONAL BELLINGHAM Plot
        plt.figure(figsize=(7,6))
        #CS = plt.contourf(degreesLon, degreesLat, Speed[hour], levels=np.linspace(0, max_speed_plot, 16))
        CS = plt.contourf(hr3_lon, hr3_lat, hr3_speed, levels=np.linspace(0, max_speed_plot, 16))
        plt.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        #plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),units='width')
        plt.quiver(degLon,degLat,U10[hour],V10[hour],color=(.9, .9, .9),scale=20,scale_units='inches')
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
        CS.ax.set_title('Init: {:s} {:02d}:00     Forecast Time: {:s} PDT'.format(date_string,zulu_hour,time_local.strftime('%b %d %I:%S%p')))              
        plt.savefig('../GoogleDrive/BellinghamBay/Regional_Wind_HR{:02d}.png'.format(hour),dpi=200)
        plt.close()
        
        # Make ZOOMED BELLINGHAM Bay Plot
        plt.figure(figsize=(7,6))
        #CS = plt.contourf(degreesLon, degreesLat, Speed[hour], levels=np.linspace(0, max_speed_plot, 16))
        CS = plt.contourf(hr3_lon, hr3_lat, hr3_speed, levels=np.linspace(0, max_speed_plot, 16))
        plt.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        #plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),units='width')
        plt.quiver(hr2_lon,hr2_lat,hr2_u10,hr2_v10,color=(.9, .9, .9),scale=20,scale_units='inches')
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
        CS.ax.set_title('Init: {:s} {:02d}:00     Forecast Time: {:s} PDT'.format(date_string,zulu_hour,time_local.strftime('%b %d %I:%S%p')))              

        plt.savefig('../GoogleDrive/BellinghamBay/BBay_Wind_HR{:02d}.png'.format(hour),dpi=200)
        plt.close()
        
        
    # Use ffmpeg to make animation
    os.chdir('../GoogleDrive/BellinghamBay/')
    ffmpegCommand = 'ffmpeg -f image2 -r 1 -i Regional_Wind_HR%02d.png -vcodec mpeg4 -y -vb 700k Regional_Wind.mp4'    
    subprocess.check_call(ffmpegCommand, shell=True)
    ffmpegCommand = 'ffmpeg -f image2 -r 1 -i BBay_Wind_HR%02d.png -vcodec mpeg4 -y -vb 700k BBay_Wind.mp4'    
    subprocess.check_call(ffmpegCommand, shell=True)
    os.chdir('../../SkagitOperational')
                
    # Move png files to image folder
    for hour in range(forecast_count):
        fname_src = '../GoogleDrive/BellinghamBay/Regional_Wind_HR{:02d}.png'.format(hour)
        os.remove(fname_src)             
        fname_src = '../GoogleDrive/BellinghamBay/BBay_Wind_HR{:02d}.png'.format(hour)
        os.remove(fname_src)  
#        shutil.move('../GoogleDrive/BellinghamBay/Regional_Wind_HR{:02d}.png'.format(hour),
#                    '../GoogleDrive/BellinghamBay/ImageFiles/Regional_Wind_HR{:02d}.png'.format(hour))
#        shutil.move('../GoogleDrive/BellinghamBay/BBay_Wind_HR{:02d}.png'.format(hour),
#                    '../GoogleDrive/BellinghamBay/ImageFiles/BBay_Wind_HR{:02d}.png'.format(hour))


def plot_bbay_wind_wave(date_string, zulu_hour, param):
    # Get time offset  
    gmt_off = op_functions.get_gmt_offset()
    m2ft = 3.28084     
    
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
    (degLat,degLon) = load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file)
    degLat = degLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    degLon = degLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
        
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
    (Speed,Dir,U10,V10,max_speed) = load_hrdps_wind(date_string, zulu_hour, param, Nx, Ny)

    # ---------------------Load Tide ----------------------------------------
    (tide_time, tide) = op_functions.get_tides(date_string, zulu_hour, param)
    tide = [t*m2ft for t in tide]
    tide_time = [t-timedelta(hours=gmt_off) for t in tide_time]
    
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
        bins_hsig_plot = 21
    elif max_hsig < 3:
        max_hsig_plot = 3
        bins_hsig_plot = 31
    else:
        max_hsig_plot = 6
        bins_hsig_plot = 31
    
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
        
        gs = gridspec.GridSpec(25,2)
        gs.update(left=0.075, right=0.98, top=0.95, bottom=0.005, wspace=0.05)
        ax1 = plt.subplot(gs[:-8,0])
        ax2 = plt.subplot(gs[:-8,1])
        ax1c = plt.subplot(gs[-7,0])
        ax2c = plt.subplot(gs[-7,1])
        ax3 = plt.subplot(gs[-4:-1,:])

        ax1.set_axis_bgcolor('white')
        ax2.set_axis_bgcolor('white')
        
        ax3.set_axis_bgcolor('white')        
                
        # Plot Winds
        CS = ax1.contourf(hr3_lon, hr3_lat, hr3_speed, levels=np.linspace(0, max_speed_plot, 16))
        ax1.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        #plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),units='width')
        ax1.quiver(hr2_lon,hr2_lat,hr2_u10,hr2_v10,color=(.9, .9, .9),width=0.004,scale=40,scale_units='inches')
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
        plt.suptitle('Init: {:s} {:02d}:00     Forecast Time: {:s} PDT'.format(date_string,zulu_hour,time_local.strftime('%b %d %I:%S%p')))              
        
        quiver_skip = 6
        CS = ax2.contourf(m_lon, m_lat, Hsig[hour], levels=np.linspace(0, max_hsig_plot, bins_hsig_plot))  
        ax2.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        ax2.quiver(m_lon[::quiver_skip,::quiver_skip], m_lat[::quiver_skip,::quiver_skip],
                   Uhsig[hour][::quiver_skip,::quiver_skip],Vhsig[hour][::quiver_skip,::quiver_skip]
                   ,color=(.9, .9, .9),width=0.004)#,scale=2,scale_units='inches')
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
        
        ax3.plot(tide_time,tide,label='tide')
        ax3.set_ylabel('Tide [ft]')
        y_top = ax3.get_ylim()
        ax3.plot([tide_time[hour],tide_time[hour]],[y_top[0],y_top[1]],color=(.5,.5,.5),zorder=0)
        # Make x-axis nice 
        days = mdates.DayLocator()
        hours = mdates.HourLocator()
        
        days_fmt = mdates.DateFormatter('%m/%d %H:%M')
        ax3.xaxis.set_major_locator(days)
        ax3.xaxis.set_major_formatter(days_fmt)
        ax3.xaxis.set_minor_locator(hours)
        #ax3.tick_params(labelbottom='off')
        
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
        os.remove(fname_src)        
        #fname_dest = '{:s}/{:s}/ImageFiles/{:s}WindWave_{:02d}.png'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'],hour)
        #shutil.move(fname_src,fname_dest)
                
                
def plot_bbay_wind_val(date_string, zulu_hour, param):
    # Get time offset  
    gmt_off = op_functions.get_gmt_offset()
    
    # Initialize    
    hrdps_lamwest_file = param['hrdps_lamwest_file']
    
    # Grib cropping bounds (indices)
    bounds = param['crop_bounds']
       
    #----------------------- Load up HRDP Land Mask----------------------------------------
    (Nx,Ny) = load_hrdps_mask(date_string, zulu_hour, param)
    
    #------------------------------- Load lat/lon positions of hrdps ---------------------------------
    (degLat,degLon) = load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file)
    degLat = degLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    degLon = degLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    
    #---------------------------- Load bathy ----------------------------------
    (bathy_elv, bathy_lat, bathy_lon) = load_bathy_nc(param)
          
    # ------------ Load in HRDPS Wind & Pressure Grib Data --------------------------------
    (Speed,Dir,U10,V10,max_speed) = load_hrdps_wind(date_string, zulu_hour, param, Nx, Ny)
    Slp = load_hrdps_slp(date_string, zulu_hour, param, Nx, Ny)
    
    # -------------------- Load Concatenated Hindcast ------------------------
    num_goback = 8;    
    (hind_time, hind_speed, hind_dir, hind_slp) = load_hrdps_point_hindcast(date_string, zulu_hour, param, Nx, Ny, param['ndbc_lat'], param['ndbc_lon'], num_goback)
    hind_time = [x - timedelta(hours=gmt_off) for x in hind_time] # Convert from UTC to local

    # ----------------Grab NDBC Data ------------------------------------------
    (ndbc_time,ndbc_speed,ndbc_dir,ndbc_slp) = download_ndbc.get_ndbc_realtime(param['ndbc_sta_id'],56)
    ndbc_time = [t - timedelta(hours=gmt_off) for t in ndbc_time] # Convert from UTC to local
    #----------------- Find closest model grid cell on HRDPS Forecast---------------------    
    dist = np.add(np.square(np.array(degLon)-param['ndbc_lon']),np.square(np.array(degLat)-param['ndbc_lat']))
    (I_lon, I_lat) = np.where(dist == np.min(dist))
    ndbc_speed_pred = [s[I_lon, I_lat] for s in Speed]        
    ndbc_dir_pred = [wrapTo360(s[I_lon, I_lat]) for s in Dir]       
    ndbc_slp_pred = [s[I_lon, I_lat]/1000 for s in Slp] # units in hPa    
       
    
    # ------------------Get Davis Winds---------------------------------------
    sta_name = 'bellinghamkite'
    days_back = 4
    df_bk = davis_weather.get_davis_latest(date_string,zulu_hour,sta_name,days_back)
    df_bk['time'] = df_bk['time']-timedelta(hours=7)
    # Get preditions nearest
    dist = np.add(np.square(np.array(degLon)-df_bk.lon),np.square(np.array(degLat)-df_bk.lat))
    (I_lon, I_lat) = np.where(dist == np.min(dist))
    df_bk_speed_pred = [s[I_lon, I_lat] for s in Speed]        
    df_bk_dir_pred = [wrapTo360(s[I_lon, I_lat]) for s in Dir]       
    df_bk_slp_pred = [s[I_lon, I_lat]/1000 for s in Slp] # units in hPa    

    # ----------------------GRab NCDC Data------------------------------------
#    usaf = '727976'
#    wban = '24217'
#    year = '2017'
#    hours = 48
#    sta_name = 'bham_air'   
#    ncdc_lat = 48.794
#    ncdc_lon = -122.537
#    (ncdc_time, ncdc_speed, ncdc_dir) = download_ncdc.get_ncdc_met(usaf, wban, year, hours, sta_name)
#    ncdc_time = [t - timedelta(hours=gmt_off) for t in ncdc_time] # Convert from UTC to local


        
    # ------------------- Time Vec -------------------
    time_vec_local = [datetime.strptime('{:s}{:d}'.format(date_string,zulu_hour),'%Y%m%d%H')+timedelta(hours=(hour-gmt_off)) for hour in range(48)]    
    
    #--------------------------------------------------------------------------
    #------------------------------Make Plot-----------------------------------
    #--------------------------------------------------------------------------         
    # Set up Plots 
    fig = plt.figure(figsize=(10.,7.))

    #ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=4)   # rows, columns, row, column (0 for first)
    #ax2 = plt.subplot2grid((5, 2), (0, 1), rowspan=4)
    #ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=2, rowspan=1)
    
    gs = gridspec.GridSpec(30,2)
    gs.update(left=0.075, right=0.98, top=0.95, bottom=0.075, wspace=0.15, hspace=0.05)
    ax1 = plt.subplot(gs[:-4,0])
    ax1c = plt.subplot(gs[-2,0])        
    ax2 = plt.subplot(gs[2:10,1])
    ax3 = plt.subplot(gs[11:19,1])        
    ax4 = plt.subplot(gs[20:28,1])
    
    #plt.tight_layout()
    #ax2c = plt.subplot(gs[-8,1])
    #ax3 = plt.subplot(gs[-5:,:])
    

    #ax1.set_axis_bgcolor('white')
    ax2.set_axis_bgcolor('white') 
    #ax3.set_axis_bgcolor('silver')        
    
      
    ax2.plot(ndbc_time,ndbc_speed,'k.-',label='Observations')        
    ax2.plot(time_vec_local,ndbc_speed_pred,'b',label='Predictions')
    ax2.plot(hind_time,hind_speed,'r',label='Hindcast')
    ax2.set_ylabel('Wind Speed [mph]')
    ax2.legend(frameon=False, prop={'size':10}, bbox_to_anchor=(1, 1.3), ncol=3 )
    y_top = ax2.get_ylim()
    ax2.plot([time_vec_local[hour],time_vec_local[hour]],[0,y_top[1]],color=(.5,.5,.5),zorder=0)
    
    ax3.plot(ndbc_time,ndbc_dir,'k.-',label='Observations')        
    ax3.plot(time_vec_local,ndbc_dir_pred,'b',label='Predictions')
    ax3.plot(hind_time,hind_dir,'r',label='Hindcast')
    ax3.set_ylabel('Wind Dir [deg]')
    y_top = ax3.get_ylim()
    ax3.plot([time_vec_local[hour],time_vec_local[hour]],[0,y_top[1]],color=(.5,.5,.5),zorder=0)
    
    ax4.plot(ndbc_time,ndbc_slp,'k.-',label='Observations')        
    ax4.plot(time_vec_local,ndbc_slp_pred,'b',label='Predictions')
    ax4.plot(hind_time,hind_slp,'r',label='Hindcast')
    ax4.set_ylabel('Pressure [kPa]')
    y_top = ax4.get_ylim()
    ax4.plot([time_vec_local[hour],time_vec_local[hour]],[y_top[0],y_top[1]],color=(.5,.5,.5),zorder=0)


    # Make x-axis nice 
    days = mdates.DayLocator()
    hours = mdates.HourLocator()
    
    days_fmt = mdates.DateFormatter('%m/%d %H:%M')
    ax2.xaxis.set_major_locator(days)
    ax2.xaxis.set_major_formatter(days_fmt)
    ax2.xaxis.set_minor_locator(hours)
    ax2.tick_params(labelbottom='off')

    ax3.xaxis.set_major_locator(days)
    ax3.xaxis.set_major_formatter(days_fmt)
    ax3.xaxis.set_minor_locator(hours)              
    ax3.tick_params(labelbottom='off')

    ax4.xaxis.set_major_locator(days)
    ax4.xaxis.set_major_formatter(days_fmt)
    ax4.xaxis.set_minor_locator(hours)              

    fname = '{:s}/{:s}/{:s}Wind_val'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'])
    fig.savefig('{:s}.png'.format(fname),dpi=200)
    plt.close()
    
     
     
def plot_skagit_wind_wave(date_string, zulu_hour, param):
    # Get time offset  
    gmt_off = op_functions.get_gmt_offset()
    m2ft = 3.28084     
    
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
    (degLat,degLon) = load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file)
    degLat = degLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    degLon = degLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
        
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
    (Speed,Dir,U10,V10,max_speed) = load_hrdps_wind(date_string, zulu_hour, param, Nx, Ny)

    # ---------------------Load Tide ----------------------------------------
    (tide_time, tide) = op_functions.get_tides(date_string, zulu_hour, param)
    tide = [t*m2ft for t in tide]
    tide_time = [t-timedelta(hours=gmt_off) for t in tide_time]
    
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
        bins_hsig_plot = 21
    elif max_hsig < 3:
        max_hsig_plot = 3
        bins_hsig_plot = 31
    else:
        max_hsig_plot = 6
        bins_hsig_plot = 31
    
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
        fig = plt.figure(figsize=(10.,6.))

        #ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=4)   # rows, columns, row, column (0 for first)
        #ax2 = plt.subplot2grid((5, 2), (0, 1), rowspan=4)
        #ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=2, rowspan=1)
        
        gs = gridspec.GridSpec(25,2)
        gs.update(left=0.075, right=0.98, top=0.95, bottom=0.005, wspace=0.05)
        ax1 = plt.subplot(gs[:-8,0])
        ax2 = plt.subplot(gs[:-8,1])
        ax1c = plt.subplot(gs[-7,0])
        ax2c = plt.subplot(gs[-7,1])
        ax3 = plt.subplot(gs[-4:-1,:])

        ax1.set_axis_bgcolor('white')
        ax2.set_axis_bgcolor('white')
        
        ax3.set_axis_bgcolor('white')        
                
        # Plot Winds
        CS = ax1.contourf(hr3_lon, hr3_lat, hr3_speed, levels=np.linspace(0, max_speed_plot, 16))
        ax1.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        #plt.quiver(degreesLon,degreesLat,U10[hour],V10[hour],color=(.5, .5, .5),units='width')
        ax1.quiver(hr2_lon,hr2_lat,hr2_u10,hr2_v10,color=(.9, .9, .9),width=0.004,scale=40,scale_units='inches')
        ax1.contourf(bathy_lon,bathy_lat,bathy_elv,levels=[0, 5000],hatches=['...'],alpha=0)
        #cbar = plt.colorbar(CS, ax=ax1, orientation='horizontal')
        cbar = plt.colorbar(CS, cax=ax1c, orientation='horizontal', )        
        cbar.ax.set_xlabel('Wind Speed [mph]')
        CS.ax.ticklabel_format(useOffset=False)
        CS.ax.get_xaxis().get_major_formatter().set_scientific(False)
        CS.ax.set_ylim(lat_bounds[0], lat_bounds[1])
        CS.ax.set_xlim(lon_bounds[0], lon_bounds[1])
        CS.ax.set_xticks([-122.6, -122.5, -122.4])
        CS.ax.set_xticklabels(['122.6$^\circ$W', '122.5$^\circ$W', '122.4$^\circ$W'])
        CS.ax.set_yticks([48.3, 48.4])
        CS.ax.set_yticklabels(['48.3$^\circ$N', '48.4$^\circ$N'])
        #CS.ax.set_title('Init: {:s} Z{:02d} - FCST HR {:d}, Local Time: {:s}'.format(date_string,zulu_hour,hour,time_local.strftime('%b %d %I:%S%p')))              
        plt.suptitle('Init: {:s} {:02d}:00     Forecast Time: {:s} PDT'.format(date_string,zulu_hour,time_local.strftime('%b %d %I:%S%p')))              
        
        quiver_skip = 6
        CS = ax2.contourf(m_lon, m_lat, Hsig[hour], levels=np.linspace(0, max_hsig_plot, bins_hsig_plot))  
        ax2.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
        ax2.quiver(m_lon[::quiver_skip,::quiver_skip], m_lat[::quiver_skip,::quiver_skip],
                   Uhsig[hour][::quiver_skip,::quiver_skip],Vhsig[hour][::quiver_skip,::quiver_skip]
                   ,color=(.9, .9, .9),width=0.004)#,scale=2,scale_units='inches')
        ax2.contourf(bathy_lon,bathy_lat,bathy_elv,levels=[0, 5000],hatches=['...'],alpha=0)
        cbar = plt.colorbar(CS, cax=ax2c, orientation='horizontal')
        cbar.ax.set_xlabel('Wave Height [ft]')
        CS.ax.ticklabel_format(useOffset=False)
        CS.ax.get_xaxis().get_major_formatter().set_scientific(False)
        CS.ax.set_ylim(lat_bounds[0], lat_bounds[1])
        CS.ax.set_xlim(lon_bounds[0], lon_bounds[1])
        CS.ax.set_xticks([-122.6, -122.5, -122.4])
        CS.ax.set_xticklabels(['122.6$^\circ$W', '122.5$^\circ$W', '122.4$^\circ$W'])
        CS.ax.set_yticks([48.3, 48.4])
        CS.ax.set_yticklabels([])             
        ax3.plot(tide_time,tide,label='tide')
        ax3.set_ylabel('Tide [ft]')
        y_top = ax3.get_ylim()
        ax3.plot([tide_time[hour],tide_time[hour]],[y_top[0],y_top[1]],color=(.5,.5,.5),zorder=0)
        # Make x-axis nice 
        days = mdates.DayLocator()
        hours = mdates.HourLocator()
        
        days_fmt = mdates.DateFormatter('%m/%d %H:%M')
        ax3.xaxis.set_major_locator(days)
        ax3.xaxis.set_major_formatter(days_fmt)
        ax3.xaxis.set_minor_locator(hours)
        #ax3.tick_params(labelbottom='off')
        
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
        os.remove(fname_src)        
        #fname_dest = '{:s}/{:s}/ImageFiles/{:s}WindWave_{:02d}.png'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'],hour)
        #shutil.move(fname_src,fname_dest) 

    
# Use for debugging     
if __name__ == '__main__':    
    import get_param
    #(date_string, zulu_hour) = op_functions.latest_hrdps_forecast()
    #param = get_param.get_param_skagit_SC100m()       
    #param = get_param.get_param_skagitE_200m()    
    param = get_param.get_param_bbay()    
    Nx = 685  
    Ny = 485
    num_goback = 4 #Number of forecasts to go back to
    #param['num_forecast_hours'] = 1
   
    date_string = '20171101'
    zulu_hour = 0
    
    # -------------------- TEST FUNCTIONS ----------------------------    
    #plot_bbay_wind_wave(date_string, zulu_hour, param)
    #plot_bbay_wind(date_string, zulu_hour, param)
    plot_bbay_wind_val(date_string, zulu_hour, param)
    #plot_skagit_wind_wave(date_string, zulu_hour, param)
    
    
    # Test hindcast loading and concatenating
#    (Time, Speed, Dir, slp) = load_hrdps_point_hindcast(date_string, zulu_hour, param, Nx, Ny, param['ndbc_lat'], param['ndbc_lon'], num_goback)
#    plt.plot(Time,slp)
#    plt.show()
#    plt.close()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
