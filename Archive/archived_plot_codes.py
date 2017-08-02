# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 15:10:13 2017

@author: crosby
"""

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