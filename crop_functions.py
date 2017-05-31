# setup lambert conformal basemap.
# lat_1 is first standard parallel.
# lat_2 is second standard parallel (defaults to lat_1).
# lon_0,lat_0 is central point.
# rsphere=(6378137.00,6356752.3142) specifies WGS4 ellipsoid
# area_thresh=1000 means don't plot coastline features less than 1000 km^2 in area.
#----------------------------------------------------------------------------------

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
#import matplotlib.gridspec
import matplotlib.cm as cm
import re
import os
import subprocess
import pygrib
from pyproj import Proj
from datetime import datetime, timedelta
from pytz import timezone
from scipy.interpolate import griddata
import scipy.io as sio
from matplotlib.colors import LightSource
import matplotlib.gridspec as gridspec

def region_crop(dateString, zulu_hour, param):
    #Hardcoded variables    
    maxFileName = '../Data/crop/hrdps/max_files/max_regional_wind_{0:s}_{1:02d}Z.dat'.format(dateString, zulu_hour) #Short file with max wind speeds    
    
    # Initialize    
    fileCount = param['num_forecast_hours'] #Number of forecast hours
    hrdps_lamwest_file = param['hrdps_lamwest_file']
    hrdps_rotation_file = param['hrdps_rotation_file']
    grib_input_loc = '{0:s}/{1:s}{2:s}'.format(param['fol_wind_grib'],param['folname_grib_prefix'],dateString)
    crop_output_loc = '{0:s}/{1:s}{2:s}'.format(param['fol_wind_crop'],param['folname_crop_prefix'],dateString)
    prefix_uwnd = param['hrdps_PrefixU'] 
    prefix_vwnd = param['hrdps_PrefixV'] 
    
    #----------------------- setup mask for sea level wind ------------------------------------------------
    maskFileName = '{0:s}/CMC_hrdps_west_LAND_SFC_0_ps2.5km_{1:s}{2:02d}_P000-00.grib2'.format(grib_input_loc, dateString, zulu_hour)
    grbl = pygrib.open(maskFileName)
    grblL = grbl.select(name='Land-sea mask')[0]
    Land = grblL.values
    Land = np.asarray(Land)
    print('Land-sea mask shape',np.shape(Land)),
    Ny = np.shape(Land)[0]
    Nx = np.shape(Land)[1]
    land = Land[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]    # reduce to Salish Sea region
    print('Reduced land-sea mask shape',np.shape(land))
    
    #------------------------------- prepare for translations ---------------------------------------------
    p = Proj(proj='utm', zone=10, ellps='WGS84')
    degreesLat = np.zeros((Ny,Nx), dtype='d')
    degreesLon = np.zeros((Ny,Nx), dtype='d')
    
    # Load lat/lon positions of hrps
    indexFile = open(hrdps_lamwest_file,'r')
    for line in indexFile:
        split = line.split()
        i = int(split[0])-1
        j = int(split[1])-1
        degreesLat[j,i] = float(split[2])
        degreesLon[j,i] = float(split[3])
    indexFile.close()

    reducedLat = degreesLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    reducedLon = degreesLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
    Nyr = np.shape(reducedLat)[0]
    Nxr = np.shape(reducedLat)[1]
    
    #--------------------------------------------- UTM ----------------------------------------------
    Lons, Lats = p(degreesLon, degreesLat)  # note the capital L
    lons, lats = p(reducedLon, reducedLat)  # and the lower case l

    #-------------------------------------- rotation to earth ---------------------------------------
    Theta = np.zeros((Ny,Nx), dtype='d')
    RotationFile = open(hrdps_rotation_file,'r')
    Lines = RotationFile.readlines()
    RotationFile.close()
    for Line in Lines:
        LineSplit = Line.split()
        i = int(LineSplit[0])
        j = int(LineSplit[1])
        Theta[j,i] = -float(LineSplit[2])

    #---------------------------------------- surface wind ------------------------------------------
    maxWind = 0.0
    maxHour = 0
    meanMax = 0.0
    
    # Loop over hours in forecast
    for hour in range(fileCount):
        # Make directory if needed        
        if not os.path.exists(crop_output_loc):
            os.mkdir( crop_output_loc)
        
        # Output file name
        windFileName = '{0:s}wind_{1:s}_{2:02d}z_{3:02d}.dat'.format( crop_output_loc, dateString, zulu_hour, hour)
        croppedFileName = '{0:s}cropped_wind_{1:s}_{2:02d}z_{3:02d}.dat'.format( crop_output_loc, dateString, zulu_hour, hour)

        #Input grib file names            
        UwindFileName = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, prefix_uwnd, dateString, zulu_hour, hour)
        VwindFileName = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, prefix_vwnd, dateString, zulu_hour, hour)

        # Open grib
        grbsu = pygrib.open(UwindFileName)
        grbu  = grbsu.select(name='10 metre U wind component')[0]
        grbsv = pygrib.open(VwindFileName)
        grbv  = grbsv.select(name='10 metre V wind component')[0]

        u10 = grbu.values # same as grb['values']
        v10 = grbv.values
        u10 = np.asarray(u10)
        v10 = np.asarray(v10)
        
        # Rotate to earth relative with Bert-Derived rotations based on grid poitns (increased accuracy was derived for grid locations)
        for j in range(Ny):
            for i in range(Nx):
                R = np.matrix([ [np.cos(Theta[j,i]), -np.sin(Theta[j,i])], [np.sin(Theta[j,i]), np.cos(Theta[j,i])] ])
                rot = R.dot([u10[j,i],v10[j,i]])
                u10[j,i] = rot[0,0]
                v10[j,i] = rot[0,1]
                
        #---------------------------- reduce geographic scope (crop)-------------------
        u10r = u10[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
        v10r = v10[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
        #----------------------------------------------------------------------------------
        
        # --------------write rotated winds-----------------------------
#        windFile = open(windFileName,'w')
#        windFile.write('{0:d} {1:d}\n'.format(Ny, Nx))
#        for j in range(Ny):
#            for i in range(Nx):
#                if u10[j,i] < 9000.0 and v10[j,i] < 9000.0:
#                    windFile.write('{0:9.2f} {1:10.2f} {2:10.6f} {3:10.6f}\n'.format(Lons[j,i],Lats[j,i],u10[j,i],v10[j,i]))
#                else:
#                    windFile.write('{0:9.2f} {1:10.2f} {2:10.6f} {3:10.6f}\n'.format(Lons[j,i],Lats[j,i],0.0,0.0))
#        windFile.close()
#        print(windFileName)

        #--------------write cropped (reduced) rotated winds----------------------------
        croppedWindFile = open(croppedFileName,'w')
        croppedWindFile.write('{0:d} {1:d}\n'.format(Nyr, Nxr))
        for j in range(Nyr):
            for i in range(Nxr):
                if u10r[j,i] < 9000.0 and v10r[j,i] < 9000.0:
                    croppedWindFile.write('{0:9.2f} {1:10.2f} {2:10.6f} {3:10.6f}\n'.format(lons[j,i],lats[j,i],u10r[j,i],v10r[j,i]))
                else:
                    croppedWindFile.write('{0:9.2f} {1:10.2f} {2:10.6f} {3:10.6f}\n'.format(lons[j,i],lats[j,i],0.0,0.0))
        croppedWindFile.close()
        print 'writing %s' % croppedFileName
        #----------------------------------------------------------------------------------
        
        #------------write compressed matlab file (compression modest 20%)-------------------
        # sio.savemat(croppedWindFile,{'lat':lats,'lon':lons,'u10':u10r,'v10':v10r})

#            if os.path.exists(maxFileName):
#               print('Cropped wind data found.')
#               return Nx, Ny, Nxr, Nyr
#            print('File {0:s} exists.'.format(croppedFileName))            
#            croppedWindFile = open(croppedFileName,'r')
#            line = croppedWindFile.readline()
#            Nyr = int(line.split()[0])
#            Nxr = int(line.split()[1])
#            u10r  = np.zeros((Nyr,Nxr), dtype='d')
#            v10r  = np.zeros((Nyr,Nxr), dtype='d')
#            for j in range(Nyr):
#                for i in range(Nxr):
#                    line = croppedWindFile.readline()
#                    u10r[j,i]  = float(line.split()[2])
#                    v10r[j,i]  = float(line.split()[3])
#            croppedWindFile.close()
            
        speed = np.sqrt(u10r**2 + v10r**2)
        speed_p = ma.array(speed, mask=land)
        mspd = np.max(speed_p)
        mmax = np.mean(speed_p)
        if maxWind < mspd:
            maxWind = mspd
        if meanMax < mmax:
            meanMax = mmax
            maxHour = hour

    # Write maximum wind speed in forecast to file
    maxWindFile = open(maxFileName,'w')
    maxWindFile.write('Maximum wind: {0:6.3f} m/s, maximum mean wind {1:6.3f} at {2:2d} hours\n'.format(maxWind,meanMax,maxHour))
    maxWindFile.close()
    
    return Nx, Ny, Nxr, Nyr

#
#def Region_plot(day_of_year, dateString, maxWind, Nx, Ny, zulu_hour, tTide):
#    fileCount = 48
#    #=============================================
#    nShorePts = np.zeros(2748, dtype='i')
#    shoreFile = open('PNW_shore.dat','r')
#    shoreLines = shoreFile.readlines()
#    #=============================================
#
#    #------------------------------- prepare for translations ---------------------------------------------
#    p = Proj(proj='utm', zone=10, ellps='WGS84')
#    degreesLat = np.zeros((Ny,Nx), dtype='d')
#    degreesLon = np.zeros((Ny,Nx), dtype='d')
#    indexFile = open('lamwestpoints.dat','r')
#    for line in indexFile:
#        split = line.split()
#        i = int(split[0])-1
#        j = int(split[1])-1
#        degreesLat[j,i] = float(split[2])
#        degreesLon[j,i] = float(split[3])
#    indexFile.close()
#    #---------------------------------------------- UTM --------------------------------------------------
#    lons, lats = p(degreesLon, degreesLat)
#    #------------------------------------------- surface wind ---------------------------------------------
#    lonMinMax = [-130.5,-122.0]
#    latMinMax = [47.0,51.1]
#    xLimits, yLimits = p(lonMinMax, latMinMax)
#    # find new grid dimensions
#    NxNew = int((xLimits[1] - xLimits[0])/2500.0)
#    NyNew = int((yLimits[1] - yLimits[0])/2500.0)
#    x = np.linspace(xLimits[0], xLimits[1], NxNew)
#    y = np.linspace(yLimits[0], yLimits[1], NyNew)
#    xi, yi = np.meshgrid(x, y)
#    px = lons.flatten()
#    py = lats.flatten()
#
#    uLast      = np.zeros(np.shape(px), dtype='d')
#    vLast      = np.zeros(np.shape(py), dtype='d')
#    speedLast  = np.zeros(np.shape(py), dtype='d')
#    uMid       = np.zeros(np.shape(px), dtype='d')
#    vMid       = np.zeros(np.shape(py), dtype='d')
#    speedMid   = np.zeros(np.shape(py), dtype='d')
#
#    for hour in range(fileCount):     # Start at 1
#        windFolder = 'wind_data_{0:03d}'.format(day_of_year)
#        croppedFileName = '{0:s}/wind_{1:03d}_{2:02d}z_{3:02d}.dat'.format(windFolder, day_of_year, zulu_hour, hour)
#        dt = timedelta(hours=hour)
#        Next  = tTide + dt
#        nameString = datetime.strftime(Next, "%Y_%B_%d_%H")
#        figureName = 'regional_wind_field_{0:s}_{1:02d}z.png'.format(nameString, zulu_hour)
#        if not os.path.exists(figureName):
#            Scale = 400.0
#            #----------------------------------------------------------------------------------
#            croppedWindFile = open(croppedFileName,'r')
#            #prevLine = previousWindFile.readline()
#            line = croppedWindFile.readline()
#            Ny = int(line.split()[0])
#            Nx = int(line.split()[1])
#            u10  = np.zeros((Ny,Nx), dtype='d')
#            v10  = np.zeros((Ny,Nx), dtype='d')
#            for j in range(Ny):
#                for i in range(Nx):
#                    line = croppedWindFile.readline()
#                    u10[j,i]  = float(line.split()[2])
#                    v10[j,i]  = float(line.split()[3])
#
#            croppedWindFile.close()
#            #----------------------------------------------------------------------------------
#            speed = np.sqrt(u10**2 + v10**2)
#
#            pu = u10.flatten()
#            pv = v10.flatten()
#            pspeed = speed.flatten()
#
#            if hour > 0:
#                uMid = (pu + uLast)*0.5
#                vMid = (pv + vLast)*0.5
#                speedMid = (pspeed + speedLast)*0.5
#
#            uLast  = pu
#            vLast  = pv
#            speedLast = pspeed
#
#            # interpolate data to new grid
#            gu = griddata(zip(px,py), pu, (xi,yi))
#            gv = griddata(zip(px,py), pv, (xi,yi))
#            gspeed = griddata(zip(px,py), pspeed, (xi,yi))
#
#            fig = plt.figure(figsize=(18.0,10.0))
#
#            #================== shoreline ================
#            first = True
#            n = 0
#            for line in shoreLines:
#                if re.search('#', line):
#                    if not first:
#                        n += 1
#                        xs,ys = p(slon,slat)
#                        plt.plot(xs, ys, 'r-', lw=1.1)
#                    slon = []
#                    slat = []
#                    first = False
#                else:
#                    nShorePts[n] += 1
#                    slon.append(float(line.split()[0]))
#                    slat.append(float(line.split()[1]))
#
#            pnwDateString = datetime.strftime(Next, "%Y-%m-%d %H:%M")
#
#            skip = 10
#            plt.quiver(xi[::skip,::skip], yi[::skip,::skip], gu[::skip,::skip], gv[::skip,::skip], color='w', width=0.002, scale=Scale, zorder=5)
#            sp = plt.streamplot(x, y, gu, gv, color='w', density=3.0, linewidth=1.1, arrowsize=0.01, zorder=5)
#            levels = np.linspace(0.0, maxWind, int(maxWind)+1)
#            plt.contourf(xi,yi, gspeed, levels, cmap=cm.jet)
#            cb = plt.colorbar()
#            cb.set_label('meters/second')
#            #cb.set_clim(0.0, 10.0)
#            plt.xlim(xLimits[0], xLimits[1])
#            plt.ylim(yLimits[0], yLimits[1])
#
#            if hour == 0:
#                plt.title('Wind Field, {0:s} analysis'.format(pnwDateString))
#            else:
#                plt.title('Wind Field, {0:s} forecast'.format(pnwDateString))
#            plt.grid(True)
#            plt.tight_layout(w_pad=0.1)
#            print(figureName)
#            plt.savefig(figureName)
#            plt.savefig('AnimationFiles/regional_wind_field_{0:02d}'.format(hour)) # This is a title that works with ffmpeg.
#            #plt.show()
#            plt.close()
#
#        else:
#            print('File {0:s} found.'.format(figureName))
#
#def SalishSea_plot(day_of_year, dateString, maxWind, Nx, Ny, zulu_hour, tTide, mean_local_eta):
#    fileCount = 48
#    bellinghamLL = [525344.26343279483, 5377953.9857531404]
#    bellinghamUR = [542676.92825374531, 5403346.4520918326]
#
#    #============================================
#    Nxs = 1163
#    Nys = 1199
#    easting  = np.zeros((Nys,Nxs), 'd')
#    northing = np.zeros((Nys,Nxs), 'd')
#    height   = np.zeros((Nys,Nxs), 'd')
#    topoFile = open('PNW_SRTM3.dat','r')
#    topoLines = topoFile.readlines()
#    topoFile.close()
#    for j in range(Nys):
#        for i in range(Nxs):
#            split = topoLines[j*Nxs+i].split()
#            easting[j,i]  = float(split[0])
#            northing[j,i] = float(split[1])
#            height[j,i]   = float(split[2])
#
#    ewMin = np.min(easting)
#    ewMax = np.max(easting)
#    nsMin = np.min(northing)
#    nsMax = np.max(northing)
#
#    height = ma.masked_where(height <= 0.0, height)
#    ls = LightSource(azdeg=315, altdeg=60)
#
#    #================ Tides =====================
#    # for representative tides:
#    location_str = "Bellingham, Bellingham Bay, Washington"
#    dt = timedelta(days=2,hours=1)
#    Start = tTide
#    Next  = tTide + dt
#
#    # hour-by-hour tides
#    command_str = 'tide -b \"{0:s}\" -e \"{1:s}\" -l \"{2:s}\" -mr -um -s 01:00'.\
#        format( datetime.strftime(Start,"%Y-%m-%d %H:%M"), datetime.strftime(Next,"%Y-%m-%d %H:%M"), location_str )
#    tidesStr = subprocess.check_output(command_str, shell=True)
#    tides = tidesStr.split()
#    Ntides = len(tides) # combined number of dates and elevations
#    print('Number of tide elevations {0:0d}'.format(Ntides))
#    if Ntides > 96:
#        Ntides = 96
#    tide = np.empty(Ntides/2, dtype='d')
#    for n in range(0,Ntides,2):
#        tide[n/2] = (float(tides[n+1])) # every-other entry is an elevation
#    surTide = tide + mean_local_eta*0.01    # convert barometric tide to meters
#    hours = np.linspace(-7.0, 40.0, 48)
#    #=============================================
#    #plt.style.use( 'seaborn-ticks')
#    #plt.style.use( 'ggplot')
#
#    #------------------------------- prepare for translations ---------------------------------------------
#    p = Proj(proj='utm', zone=10, ellps='WGS84')
#    degreesLat = np.zeros((Ny,Nx), dtype='d')
#    degreesLon = np.zeros((Ny,Nx), dtype='d')
#    indexFile = open('lamwestpts_reduced.dat','r')
#
#    for line in indexFile:
#        split = line.split()
#        i = int(split[0])-1
#        j = int(split[1])-1
#        degreesLat[j,i] = float(split[2])
#        degreesLon[j,i] = float(split[3])
#    indexFile.close()
#    #-------------------------------------- UTM ---------------------------------------
#    lons, lats = p(degreesLon, degreesLat)
#    NxTemp = np.shape(lons)[1]
#    NyTemp = np.shape(lons)[0]
#
#    Index = []
#    for j in range(NyTemp):
#        for i in range(NxTemp):
#            if lons[j,i] >= bellinghamLL[0] and lons[j,i] <= bellinghamUR[0] and lats[j,i] >= bellinghamLL[1] and lats[j,i] <= bellinghamUR[1]:
#                Index.append([j,i])
#    #----------------------------------- surface wind ---------------------------------
#    lonMinMax = [-123.3,-122.3]
#    latMinMax = [48.0,49.0]
#    xLimits, yLimits = p(lonMinMax, latMinMax)
#    # find new grid dimensions
#    NxNew = int((xLimits[1] - xLimits[0])/2500.0)
#    NyNew = int((yLimits[1] - yLimits[0])/2500.0)
#    x = np.linspace(xLimits[0], xLimits[1], NxNew)
#    y = np.linspace(yLimits[0], yLimits[1], NyNew)
#    xi, yi = np.meshgrid(x, y)
#    px = lons.flatten()
#    py = lats.flatten()
#    skip = 2
#    Scale = 200.0
#    bellinghamMeans = []
#    bellinghamMaxes = []
#    labels = []
#    hourCount = 0
#    for hour in range(fileCount):
#        windFolder = 'wind_data_{0:03d}'.format(day_of_year)
#        croppedFileName = '{0:s}/cropped_wind_{1:03d}_{2:02d}z_{3:02d}.dat'.format(windFolder, day_of_year, zulu_hour, hour)
#        dt = timedelta(hours=hour)
#        Next  = tTide + dt
#        pnwDateString = datetime.strftime(Next, "%Y-%m-%d %H:%M")
#        nameString = datetime.strftime(Next, "%Y_%B_%d_%H")
#        figureName = 'SalishSea_wind_field_{0:s}_{1:02d}z.png'.format(nameString, zulu_hour)
#        if not os.path.exists(figureName):
#
#            #----------------------------------------------------------------------------------
#
#            croppedWindFile = open(croppedFileName,'r')
#            line = croppedWindFile.readline()
#            Ny = int(line.split()[0])
#            Nx = int(line.split()[1])
#
#            u10  = np.zeros((Ny,Nx), dtype='d')
#            v10  = np.zeros((Ny,Nx), dtype='d')
#            for j in range(Ny):
#                for i in range(Nx):
#                    line = croppedWindFile.readline()
#                    u10[j,i]  = float(line.split()[2])
#                    v10[j,i]  = float(line.split()[3])
#
#            croppedWindFile.close()
#            #----------------------------------------------------------------------------------
#            speed = np.sqrt(u10**2 + v10**2)
#            bellinghamMean = []
#            for j,i in Index:
#                bellinghamMean.append(speed[j,i])
#            MeanWind = np.mean(bellinghamMean)
#            MaxWind  = np.max( bellinghamMean)
#            bellinghamMeans.append(MeanWind)
#            bellinghamMaxes.append(MaxWind)
#
#            dhour = timedelta(hours=hour)
#            hourStr = datetime.strftime(Start+dhour,"%d %H")
#            labels.append(hourStr)
#            print('{0:s} {1:6.3f} {2:6.3f} '.format(hourStr, MeanWind, MaxWind)),
#
#            pu = u10.flatten()
#            pv = v10.flatten()
#            pspeed = speed.flatten()
#
#            # px,py,pu,pv,pspeed
#            # interpolate old data to new grid
#            gu = griddata(zip(px,py), pu, (xi,yi))
#            gv = griddata(zip(px,py), pv, (xi,yi))
#            gu = np.ma.fix_invalid(gu)
#            gv = np.ma.fix_invalid(gv)
#            gspeed = griddata(zip(px,py), pspeed, (xi,yi))
#
#            plt.figure(figsize=(8.24,11.6))
#            gs = gridspec.GridSpec(2, 1, height_ratios=[5,1])
#            ax1 = plt.subplot(gs[0])
#            ax1.set_aspect('equal')
#            ax2 = plt.subplot(gs[1])
#
#            #================== topography ================
#            ax1.imshow(ls.hillshade(height), cmap=cm.gray, extent=[ewMin, ewMax, nsMin, nsMax], zorder=11)
#            #================== shoreline ================
#
#            ax1.quiver(xi[::skip,::skip], yi[::skip,::skip], gu[::skip,::skip], gv[::skip,::skip], color='w', pivot='middle', width=0.003, scale=Scale, zorder=6)
#            sp = ax1.streamplot(x, y, gu, gv, color='w', density=2.0, linewidth=1.1, arrowsize=0.01, zorder=5)
#            Levels1 = np.linspace(0.0, maxWind, 2*int(maxWind)+1)
#            Levels2 = np.linspace(0.0, maxWind, int(maxWind)+1)
#            cs1 = ax1.contourf(xi,yi, gspeed, levels=Levels1, cmap=cm.jet)
#            cb = plt.colorbar(cs1, ax=ax1)
#            cb.set_label('meters / second')
#            cs2 = ax1.contour(xi, yi, gspeed, levels=Levels2, colors=['0.0', '0.5', '0.5', '0.5', '0.5'], zorder=7)
#            ax1.clabel(cs2, fmt='%2.0f', inline=1, fontsize=10, zorder=7)
#            #cb.set_clim(0.0, 10.0)
#            #ax1.set_xlim(xLimits[0], xLimits[1])
#            #ax1.set_ylim(yLimits[0], yLimits[1])
#            ax1.set_xlim(ewMin, ewMax)
#            ax1.set_ylim(nsMin, nsMax)
#            if hour == 0:
#                ax1.set_title('Wind Field, {0:s} analysis'.format(pnwDateString))
#            else:
#                ax1.set_title('Wind Field, {0:s} forecast'.format(pnwDateString))
#            ax1.grid(True, zorder=10)
#            # =============================== Tide Plot ==========================
#            ax2.plot(hours, tide, 'b-', lw=2)
#            ax2.plot(hours, surTide, 'r-', lw=0.5)
#            ax2.plot(hours[hour],tide[hour],'ro',ms=12)
#            ax2.set_xlim(-8.0,41.0)
#            ax2.set_xlabel('hours')
#            ax2.set_ylabel('Bellingham tide in meters')
#            ax2.set_ylim(-0.75,3.0)
#            ax2.grid(True)
#
#            plt.tight_layout()
#            print(figureName)
#            plt.savefig(figureName)
#            plt.savefig('AnimationFiles/SalishSea_wind_field_{0:02d}'.format(hour)) # This is a title that works with ffmpeg.
#            #plt.show()
#            plt.close()
#            hourCount += 1
#        else:
#            print('File {0:s} found.'.format(figureName))

