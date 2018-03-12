import numpy as np
import utm
from netCDF4 import Dataset
import os
from scipy import interpolate

def load_depth_grid(dep_nm = '../SWAN_runs/SWAN_0/bbay_150m_bathy.bot'):
   dep = np.loadtxt(dep_nm)
   dep = -dep
   [p, q] = dep.shape
   return(p, q)

def load_SWAN_grid(p, q, grd_nm = '../SWAN_runs/SWAN_0/bbay_150m_coord.grd'):
   grd = np.loadtxt(grd_nm)
   x = grd[:p*q]
   y = grd[p*q:]
   X = np.reshape(x, (q,p))
   Y = np.reshape(y, (q,p))
   return(X,Y) 

def make_wnd(date_string, zulu_hour, param, X, Y, fcst):
   slp_varname = 'PRMSL_meansealevel'
   u10_varname = 'UGRD_10maboveground'
   v10_varname = 'VGRD_10maboveground'
# load model domain grid, just mass grid where output has been averaged to
   met_slp_lat, met_slp_lon, met_slp_var = load_hrdps_grib(date_string, zulu_hour, fcst, slp_varname, param)
   met_u10_lat, met_u10_lon, met_u10_var = load_hrdps_grib(date_string, zulu_hour, fcst, u10_varname, param)
   met_v10_lat, met_v10_lon, met_v10_var = load_hrdps_grib(date_string, zulu_hour, fcst, v10_varname, param)
   (q, p) = met_slp_lat.shape
   Met_slp = met_slp_var[0]
   Met_slp_x = np.reshape(met_slp_lat, (q*p))
   Met_slp_y = np.reshape(met_slp_lon, (q*p))-360.
   Met_u10 = np.reshape(met_u10_var[0], (q*p))
   Met_u10_x = np.reshape(met_u10_lat, (q*p))
   Met_u10_y = np.reshape(met_u10_lon, (q*p))-360.
   Met_v10 = np.reshape(met_v10_var[0], (q*p))
   Met_v10_x = np.reshape(met_v10_lat, (q*p))
   Met_v10_y = np.reshape(met_v10_lon, (q*p))-360.
   #interpolate onto meteo grid
   Met_u10_stack = np.stack((Met_u10_x, Met_u10_y))
   print(Met_u10_stack)
   Met_u10_xy = np.array([utm.from_latlon(i[0],i[1])[:2] for i in np.transpose(np.stack((Met_u10_x, Met_u10_y)))])
   Met_v10_xy = np.array([utm.from_latlon(i[0],i[1])[:2] for i in np.transpose(np.stack((Met_v10_x, Met_v10_y)))])
   print(Met_u10_xy[0])
   u = interpolate.griddata(Met_u10_xy, Met_u10, (X,Y))
   v = interpolate.griddata(Met_v10_xy, Met_v10, (X,Y))
   #convert nans to 9999
   u_nan = np.isnan(u)
   print(u)
   v_nan = np.isnan(v)

   #u[u_nan] = 9999
   #v[v_nan] = 9999

   [n,m] = u.shape
   print('n {0} m {1}'.format(n, m))
   fid = open('../SWAN_runs/SWAN_{0}/nnrp_wind.wnd'.format(fcst), 'w')
   for i1 in range(m):
      for i2 in range(n):
         fid.write('   {0:12.8f}'.format(u[i2, i1]))
      fid.write('\n')
   for i1 in range(m):
      for i2 in range(n):
         fid.write('   {0:12.8f}'.format(v[i2, i1]))
      fid.write('\n')
   fid.close()
   return

def load_hrdps_grib(date_string, zulu_hour, fcst, ncvar, param):    
    # Hardcoded location of wgrib2 software    
    loc_wgrib2 = '/home/robertg4/grib2/wgrib2'    
    
    # Use to find grib file prefix from ncvar selection
    def get_prefix(argument):
        switcher = {
            'PRMSL_meansealevel':'hrdps_PrefixP',
            'UGRD_10maboveground':'hrdps_PrefixU',
            'VGRD_10maboveground':'hrdps_PrefixV',
        }
        return switcher.get(argument, "nothing")        

    # File name and locations
    grib_input_loc = '{0:s}/{1:s}{2:s}/'.format(param['fol_wind_grib'],param['folname_grib_prefix'],date_string)
    fname_grib = '{0:s}{1:s}{2:s}{3:02d}_P{4:03d}-00.grib2'.format(grib_input_loc, param[get_prefix(ncvar)], date_string, zulu_hour, fcst)
    fname_gribtemp = 'temp.grib2'
        
    # Set extents of grib data request
    lat_min = param['lats'][0]
    lat_max = param['lats'][1]
    lon_min = param['lons'][0]
    lon_max = param['lons'][1]
    
    # Extract subset to smaller grib file 
    cmd = '{:s}/wgrib2 {:s} -set_grib_type c2 -small_grib {:4.3f}:{:4.3f} {:4.3f}:{:4.3f} {:s}'.format(loc_wgrib2,fname_grib,lon_min,lon_max,lat_min,lat_max,fname_gribtemp)
    print(cmd)
    os.system(cmd)

    # Convert smaller extract to netcdf     
    cmd = '{:s}/wgrib2 {:s} -netcdf temp.nc'.format(loc_wgrib2,fname_gribtemp)
    os.system(cmd)
        
    # Read in netcdf        
    dataset = Dataset('temp.nc','r')
    var = dataset.variables[ncvar][:]    
    lat = dataset.variables['latitude'][:]
    lon = dataset.variables['longitude'][:]
    
    return (lat, lon, var)
