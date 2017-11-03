# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 15:12:17 2017

@author: crosby
"""

def plot_bbay_wind_val(date_string, zulu_hour, param):
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
    (degLat,degLon) = load_hrdps_lamwest_locs(Nx,Ny,hrdps_lamwest_file)
    degLat = degLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    degLon = degLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    
    #---------------------------- Load bathy ----------------------------------
    (bathy_elv, bathy_lat, bathy_lon) = load_bathy_nc(param)
       
    #--------------------------- Load D3D Grid --------------------------------
    # x,y,nx,ny = load_model_grid(param)   

    #--------------------------- Load Hsig Pred--------------------------------
    #(Hsig, Uhsig, Vhsig, max_hsig) = load_hsig_pred(param,nx,ny)
    
    #-------------Convert Model grid from utm to lat/lon ----------------------        
    #p = pyproj.Proj(proj='utm', zone=10, ellps='WGS84')
    #m_lon, m_lat = p(x,y,inverse=True) 
    
    # ------------ Load in All Wind & Pressure Grib Data --------------------------------
    (Speed,Dir,U10,V10,max_speed) = load_hrdps_wind(date_string, zulu_hour, param, Nx, Ny)
    Slp = load_hrdps_slp(date_string, zulu_hour, param, Nx, Ny)
    
    # -------------------- Load Concatenated Hindcast ------------------------
    num_goback = 8;    
    (hind_time, hind_speed, hind_dir, hind_slp) = load_hrdps_point_hindcast(date_string, zulu_hour, param, Nx, Ny, param['ndbc_lat'], param['ndbc_lon'], num_goback)
    hind_time = [x - timedelta(hours=gmt_off) for x in hind_time] # Convert from UTC to local

    # ----------------Grab NDBC Data ------------------------------------------
    (ndbc_time,ndbc_speed,ndbc_dir,ndbc_slp) = download_ndbc.get_ndbc_realtime(param['ndbc_sta_id'],56)
    ndbc_time = [t - timedelta(hours=gmt_off) for t in ndbc_time] # Convert from UTC to local
    
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

    # ------------------------ Load concatenated hindcast at ndbc ------------------
#    (hind_time, hind_speed2, hind_dir2) = load_hrdps_point_hindcast(date_string, zulu_hour, param, Nx, Ny, ncdc_lat, ncdc_lon, num_goback)
#    hind_time = [x - timedelta(hours=gmt_off) for x in hind_time] # Convert from UTC to local


    #----------------- Find closest model grid cell to ndbc ---------------------    
    dist = np.add(np.square(np.array(degLon)-param['ndbc_lon']),np.square(np.array(degLat)-param['ndbc_lat']))
    (I_lon, I_lat) = np.where(dist == np.min(dist))
    ndbc_speed_pred = [s[I_lon, I_lat] for s in Speed]        
    ndbc_dir_pred = [wrapTo360(s[I_lon, I_lat]) for s in Dir]       
    ndbc_slp_pred = [s[I_lon, I_lat]/1000 for s in Slp] # units in hPa
    
    # -------------- Set wind speed plotting max ------------------------
    if max_speed < 15:
        max_speed_plot = 15
    elif max_speed < 30:
        max_speed_plot = 30
    elif max_speed < 45:
        max_speed_plot = 45
    else:
        max_speed_plot = 60
    
    # ------------------- Time Vec -------------------
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
        CS.ax.set_title('Init: {:s} Z{:02d} - FCST HR {:d}, Local Time: {:s}'.format(date_string,zulu_hour,hour,time_local.strftime('%b %d %I:%S%p')))              
        
   
        
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
        fig.savefig('{:s}_{:02d}.png'.format(fname,hour),dpi=150)
        plt.close()
        
    # Use ffmpeg to make animation
    os.chdir('{:s}/{:s}/'.format(param['fol_google'],param['folname_google']))
    ffmpegCommand = r'ffmpeg -f image2 -r 1 -i {0:s}Wind_val_%02d.png -vcodec mpeg4 -y -vb 700k {0:s}Wind_val.mp4'.format(param['fname_prefix_plot'])    
    subprocess.check_call(ffmpegCommand, shell=True)
    os.chdir('../../SkagitOperational')
                
    # Move png files to image folder
    for hour in range(forecast_count):
        fname_src = '{:s}/{:s}/{:s}Wind_val_{:02d}.png'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'],hour)
        #fname_dest = '{:s}/{:s}/ImageFiles/{:s}Wind_val_{:02d}.png'.format(param['fol_google'],param['folname_google'],param['fname_prefix_plot'],hour)
        os.remove(fname_src)        
        #shutil.move(fname_src,fname_dest)  