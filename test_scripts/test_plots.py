# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 14:37:47 2017

@author: crosby
"""

# -*- coding: utf-8 -*-
"""
#---------------------------------------------------------------------#
#----------------------Skagit Operational Model-----------------------#
#---------------------------------------------------------------------#

#-----------------------Assumed File Structure------------------------#

Documents/
    SkagitOperational/  (git repo)
        Archive/
        
    Grids/
        delft3d/
            skagit/
        delftfm/
        suntans/
        
    Data/
        raw_downloads/
            hrdps/
                max_files/
                hrdps_grib_xxxxx/            
        crop/
            hrdps/
                hrdps_crop_xxxxx/
        d3d_input/
            skagit/    
    
    ModelRuns/
        skagit_wave_50m/
    
    Plots/
        skagit_50m/
            plotting_files/
    
    GoogleDrive/
        SkagitPlots/
                   
    openearthtools/ (svn repo)
    
@author: S. C. Crosby
"""

#http://dd.weather.gc.ca/model_hrdps/west/grib2/12/031/CMC_hrdps_west_UGRD_TGL_10_ps2.5km_2017061312_P031-00.grib2
#http://dd.weather.gc.ca/model_hrdps/west/grib2/12/031/CMC_hrdps_west_UGRD_TGL_10_ps2.5km_2017061312_P031-00.grib2

# Import custom libaraies
import op_functions
import crop_functions
import d3d_functions
import misc_functions
import plot_functions

# Import standard libraries
import numpy as np
import os
import subprocess
import shutil
import time

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from show_grid import Grid
import matplotlib.gridspec as gridspec
from matplotlib.colors import LightSource
from datetime import datetime, timedelta
import subprocess
from poly_mask import Polygon
import os
from scipy.interpolate import griddata

# ---------------------- SELECT DATE FOR MODsEL RUN ----------------------------

# OPTION 1: Specifiy date and zulu hour
date_string = '20170614'
zulu_hour = 12


# ------------------------ SET GOOGLE DRIVE OUTPUT ----------------------------
google_drive = '../GoogleDrive'
google_drive_fol = 'SkagitPlots'

# ---------------------- INITIALIZE MODEL -------------------------------------

# Model parameters contained in this dictionary, paths, file names, etc
param = {}

# Length of forecast
param['num_forecast_hours']     = 1    # numer of files [hours]
param['crop_bounds']            = np.asarray([[207,56],[287,219]]) # Salish Sea region
param['tide_file']              = 'tide_pred_9448576.txt' # Set tide file to use

# Set some constants for creating amu/avu files
param['line_meteo_grid_size']   = 2     # Line number in meteo grid with Nx, Ny
param['line_header_skip']       = 4     # Number of header lines in meteo file
param['xLL']                    = 526108.0  # lower left corner of SWAN computational grid
param['yLL']                    = 5343228.0

# Set locations
param['fol_model']              = '../ModelRuns/skagit_wave_50m'
param['fol_wind_grib']          = '../Data/downloads/hrdps'
param['fol_wind_crop']          = '../Data/crop/hrdps'
param['fol_grid']               = '../Grids/delft3d/skagit'
param['fol_plots']              = '../Plots/skagit_50m'
    
# Set file names and prefixes
param['folname_crop_prefix']    = 'hrdps_crop_'
param['folname_grib_prefix']    = 'hrdps_grib_'
param['fname_prefix_wind']      = 'wind_crop_' #{0:s}_{1:02d}z'.format(dateString,zulu_hour)
param['fname_meteo_grid']       = 'skagit_meteo_50m.grd'
param['fname_meteo_enc']        = 'skagit_meteo_50m.enc'
param['fname_grid']             = 'skagit_50m.grd'
param['fname_dep']              = 'skagit_50m.dep'
param['fname_enc']              = 'skagit_50m.enc'
param['wind_u_name']            = 'wind_skagit.amu'    
param['wind_v_name']            = 'wind_skagit.amv'
param['fname_mdw']              = 'skagit_50m.mdw'
param['run_script']             = 'run_wave.sh'

# Set Output Locs
param['output_locs']            = []
#param['output_locs']            = ['LongB.loc',
#                                   'CrossBN.loc',
#                                   'CrossBS.loc']   
                                   
# HRDPS prefixes and url
param['hrdps_PrefixP']          = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_' 
param['hrdps_PrefixU']          = 'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_'
param['hrdps_PrefixV']          = 'CMC_hrdps_west_VGRD_TGL_10_ps2.5km_'
param['hrdps_PrefixLAND']       = 'CMC_hrdps_west_LAND_SFC_0_ps2.5km_'
param['hrdps_url']              = 'http://dd.weather.gc.ca/model_hrdps/west/grib2'
param['hrdps_lamwest_file']     = '../Data/downloads/hrdps/lamwestpoints.dat'
param['hrdps_rotation_file']    = '../Data/downloads/hrdps/rotations.dat'

# Set GMT offset to local time
param['gmt_offset']             = op_functions.get_gmt_offset_2()


# Start timer
start_time = time.time()


# Plot 
print 'Plotting'
maxWind = 10
#plot_functions.plot_skagit_hsig(date_string, zulu_hour, max_wind, tide, param)

# Constants
m2ft = 3.28084  # Convert meters to feet

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

x,y,nx,ny = Grid(file_grid)
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
#%%

p_left = 0.1
p_rigth = 0.1
p_bot = 0.1
p_top = 0.1
p_pspace = 0.05
p_cbar = 0.05
p_wid = (1-p_left-p_rigth-p_pspace-2*(p_cbar+p_pspace))/2
p_wid2 = 1-p_left-p_rigth
p_tide = 0.175
p_height = (1-p_bot-p_top-p_pspace-p_tide)

# Initialize Figure and subplots
fig = plt.figure(figsize=(18.7,10.0))
ax1 = fig.add_axes([p_left, p_bot+p_pspace+p_tide, p_wid, p_height])

#[plot2grid((5, 2), (0, 0), rowspan=4)   # rows, columns, row, column (0 for first)
#ax2 = plt.subplot2grid((5, 2), (0, 1), rowspan=4)
#ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=2, rowspan=1)

#ax1.set_facecolor('slategray')
#ax2.set_facecolor('slategray') # darkslategray
#ax3.set_facecolor('silver')
ax1.set_axis_bgcolor('white')
#ax2.set_axis_bgcolor('white') # darkslategray
#ax3.set_axis_bgcolor('silver')

ax1.imshow(ls.hillshade(zT), cmap=cm.gray, extent=[ewMin, ewMax, nsMin, nsMax], zorder=4)
ax1.quiver(xw, yw, u, v, color='w', width=0.003, scale=100.0, zorder=6)
sp = ax1.streamplot(xx, yy, uWind, vWind, color='w', density=1.5, arrowsize=0.01, zorder=6)
plt.setp(ax1.get_xticklabels(), visible=False)
plt.setp(ax1.get_yticklabels(), visible=False)

levels = np.linspace(0.0, maxWind, 30)
cs1 = ax1.contourf(xx, yy, wind, levels, cmap=plt.cm.jet, zorder=5)
cbaxes = fig.add_axes([p_left+p_pspace+p_wid, p_bot+p_pspace+p_tide, 0.03, .8])
cb1 = plt.colorbar(cs1, ax=ax1, cax=cbaxes)
cb1.set_label('Wind Speed [m/s]')

#ax1.scatter(xw, yw, marker='o', c='k', s=10, zorder=3)
ax1.set_title('Wind Forecast for {0:s} UTC'.format(pnwDateString))
ax1.grid(True, zorder=6)
plt.setp(ax1.get_xticklabels(), visible=False)
plt.setp(ax1.get_yticklabels(), visible=False)
ax1.axis('equal')
ax1.set_adjustable('box-forced')

ax1.set_xlim(ewMin,ewMax)
ax1.set_ylim(nsMin,nsMax)


ax2 = fig.add_axes([p_left+p_pspace+p_wid, p_bot+p_pspace+p_tide, p_wid, p_height])

# =============================================================================
ax2.imshow(ls.hillshade(zT), cmap=cm.gray, extent=[ewMin, ewMax, nsMin, nsMax])
ax2.quiver(x[::skip,::skip], y[::skip,::skip], uhsig[::skip,::skip], vhsig[::skip,::skip], color='w', pivot='middle', width=0.003, scale=Scale, zorder=10)
cs = ax2.contour(x, y, hsign, levels=Levels, colors=['0.0', '0.5', '1'], zorder=5)

cs2 = ax2.contourf(x, y, hsign, levels=Levels, cmap=cm.jet, zorder=1)
cb2 = plt.colorbar(cs2, ax=ax2)   # label='Pascal'

cb2.set_label('Significant Wave Height [ft]')
ax2.set_title('Wave Forecast for {0:s}'.format(pnwDateString))
ax2.grid(True)

ax2.axis('equal')
ax2.set_adjustable('box-forced')

ax2.set_xlim(ewMin,ewMax)
ax2.set_ylim(nsMin,nsMax)

#%%

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

    
# End timer
print 'Total time elapsed: {0:.2f} minutes'.format(((time.time() - start_time)/60.))







































