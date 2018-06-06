#import plot_functions
import numpy as np
import get_param
import op_functions
import SWAN_functions
import argparse

def main():
   param = get_param.get_param_Puget()
   date_string, zulu_hour = op_functions.latest_hrdps_forecast()
   test_file = '{0:s}/{1:s}{2:s}/{3:s}{2:s}{4:02d}_P047-00.grib2'.format(param['fol_wind_grib'], param['folname_grib_prefix'],date_string,param['hrdps_PrefixP'],zulu_hour)
   if os.path.isfile(test_file):
      print 'Grib files already downloaded, skipping'
   else:
      op_functions.get_hrdps(date_string, zulu_hour, param)

main()
