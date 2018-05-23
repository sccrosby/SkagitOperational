#import plot_functions
import numpy as np
import get_param
import op_functions
import SWAN_functions

def main():
   param = get_param.get_param_Puget()
   date_string, zulu_hour = op_functions.latest_hrdps_forecast()
#   fcst = 0
   # load times
   tide_time, tide = op_functions.get_tides(date_string, zulu_hour, param)
   #Load SWAN grids
   op_functions.get_hrdps(date_string, zulu_hour, param)
   #load depth grid
   #dep_nm = '/home/groberts/workspace/senior_project/SWAN_bbay/bbay_150m_bathy.bot'
   #dep = np.loadtxt(dep_nm)
   #dep = -dep
   #[p, q] = dep.shape
#   p, q = SWAN_functions.load_depth_grid(dep_nm = 'PugetSound2.bot')
   p, q = SWAN_functions.load_depth_grid()

   #Load SWAN grid
   #grd_nm = '/home/groberts/workspace/senior_project/SWAN_bbay/bbay_150m_coord.grd'
   #grd = np.loadtxt(grd_nm)
   #print(grd.shape)
   #x = grd[:p*q]
   #y = grd[p*q:]
   #X = np.reshape(x, (q,p))
   #Y = np.reshape(y, (q,p))
  # X, Y = SWAN_functions.load_SWAN_grid(p, q, grd_nm = 'PugetSound2.grd')
   X, Y = SWAN_functions.load_SWAN_grid(p, q)
   #ncvar = 'VGRD_10maboveground'
   #op_functions.get_hrdps(date_string, zulu_hour, param)
   #lat, lon, var = plot_functions.load_hrdps_grib(date_string, zulu_hour, fcst, ncvar, param)
   #print('lat {0}\nlon {1}\n var{2}'.format(lat.shape, lon.shape, var.shape))
   #plot_functions.make_wnd(date_string, zulu_hour, param, X, Y, fcst)
   for fcst in range(47): 
  #    SWAN_functions.make_wnd(date_string, zulu_hour, param, X, Y, fcst, grid_units = 'deg')
      SWAN_functions.make_wnd(date_string, zulu_hour, param, X, Y, fcst)
       
   return

main()
