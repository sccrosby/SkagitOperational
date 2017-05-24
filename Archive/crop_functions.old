# -*- coding: utf-8 -*-
# Created 5/8/2017
# Author S. C. Crosby

# Add libraries
import sys
sys.path.append('C:\Users\Crosby\Anaconda2\Lib\site-packages')
from osgeo import gdal  
from osgeo.gdalconst import GA_ReadOnly
from mpl_toolkits.basemap.pyproj import Proj
from datetime import datetime, timedelta


#def Skagit_crop_canada(dateString, dateStringCanada, utcCanada, fileCount, 
#                latMin, latMax, lonMin, lonMax, gribPrefixU, gribPrefixV):
#    p = Proj(proj='utm', zone=10, ellps='WGS84')
#=

fname_grib = r'CMC_hrdps_west_UGRD_TGL_10_ps2.5km_2017050800_P000-00.grib2'
fol_grib = r'D:/SkagitOperational/hrdps_grib_20170508/'

# Initialize
maxWind = 0.0
maxHour = 0
meanMax = 0.0





###
datasetU = gdal.Open(fol_grib + fname_grib, GA_ReadOnly )  

rband = datasetU.GetRasterBand(1)

Nx = band.XSize  
Ny = band.YSize


U10 = np.flipud(band_u.ReadAsArray(0,0))


# # # # # # # # # 
Lats = np.zeros((Ny,Nx), dtype='d')
Lons = np.zeros((Ny,Nx), dtype='d')
indexFile = open('lamwestpoints.dat','r')
for line in indexFile:
    split = line.split()
    i = int(split[0])-1
    j = int(split[1])-1
    Lats[j,i] = float(split[2])
    Lons[j,i] = float(split[3])
indexFile.close()
#-------------------------------------- UTM -----------------------
lons, lats = p(Lons, Lats)
###################################################################
lonLatLimits = np.where((Lats >= latMin) & (Lats <= latMax) & 
        (Lons >= lonMin) & (Lons <= lonMax))
il = min(lonLatLimits[1])
ir = max(lonLatLimits[1])
jb = min(lonLatLimits[0])
jt = max(lonLatLimits[0])
Nx = ir-il
Ny = jt-jb
NxNyFile = open('NxNyCanada.dat','w')
NxNyFile.write('{0:03d} {1:03d}'.format(Nx , Ny))
NxNyFile.close()
#######################################################################
u10 = U10[jb:jt,il:ir]
v10 = V10[jb:jt,il:ir]  
lons, lats = p(Lons[jb:jt,il:ir], Lats[jb:jt,il:ir])
# End: added by Abbas
croppedWindFile = open(croppedFileName,'w')
for j in range(Ny):
    for i in range(Nx):
        croppedWindFile.write('{0:9.2f} {1:10.2f} {2:10.6f} {3:10.6f}\n'.format(lons[j,i],lats[j,i],u10[j,i],v10[j,i]))
croppedWindFile.close()
#----------------------------------------------------------------------------------
speed = np.sqrt(u10**2 + v10**2)
mspd = np.max(speed)
mmax = np.mean(speed)
if maxWind < mspd:
    maxWind = mspd
if meanMax < mmax:
    mmax = meanMax
    maxHour = hour

#return maxWind, Nx, Ny, maxHour
