# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 08:09:53 2017

@author: crosby
"""
from matplotlib import pyplot as plt
from netCDF4 import Dataset
import pygrib
import scipy.ndimage
import shutil


hrdps_lamwest_file = '../Data/downloads/hrdps/lamwestpoints.dat'

# Trimming bounds for HDRPS predictions (Manual because not on regular grid)
bounds = np.asarray([[207,56],[287,219]])  # Salish Sea
bounds = np.asarray([[270,117],[288,141]]) # Bellingham Bay
#bounds = np.asarray([[275,109],[285,124]]) # Skagit


# For Trimming files for bathy contour
llcorner = [48.39, -122.88] # Bellingham Bay
urcorner = [48.87, -122.28]
#llcorner = [48.2, -122.7] # Skagit 
#urcorner = [48.55, -122.30]

# Size of HDRPS file
Nx = 685
Ny = 485


#------------------- Load HRDPS lat/lon positions---------------------------
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


# Trim HRDPS
degreesLat = degreesLat[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
degreesLon = degreesLon[bounds[0,1]:bounds[1,1], bounds[0,0]:bounds[1,0]]
   
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



# Make plot of bathy and HRDPS locs
plt.figure(figsize=(7,6))
plt.contour(bathy_lon,bathy_lat,bathy_elv,levels=[0],colors='k') #[0, 50, 100, 500, 750, 1000]
plt.plot(degreesLon,degreesLat,'b.')

plt.show()
plt.close()





