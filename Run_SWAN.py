#import plot_functions
import numpy as np
import get_param
import op_functions
import SWAN_functions
import argparse

def parse_all_arguments():
   parser = argparse.ArgumentParser();
   parser.add_argument("grid")
   return(parser.parse_args())

def build_puget_wind():
   param = get_param.get_param_Puget()
   date_string, zulu_hour = op_functions.latest_hrdps_forecast()
   tide_time, tide = op_functions.get_tides(date_string, zulu_hour, param)
   p, q = SWAN_functions.load_depth_grid(dep_nm = 'PugetSound2.bot')
   X, Y = SWAN_functions.load_SWAN_grid(p, q, grd_nm = 'PugetSound2.grd')
   for fcst in range(47): 
      SWAN_functions.make_wnd(date_string, zulu_hour, param, X, Y, fcst, grid_units = 'deg')
   return

def build_bbay_wind():
   param = get_param.get_param_bbay()
   date_string, zulu_hour = op_functions.latest_hrdps_forecast()
   tide_time, tide = op_functions.get_tides(date_string, zulu_hour, param)
   p, q = SWAN_functions.load_depth_grid(dep_nm = 'bbay_150m_bathy.bot')
   X, Y = SWAN_functions.load_SWAN_grid(p, q, grd_nm = 'bbay_150m_coord.grd')
   for fcst in range(47): 
      SWAN_functions.make_wnd(date_string, zulu_hour, param, X, Y, fcst)
   return

def main():
   args = parse_all_arguments()
   if args.grid == 'puget':
      build_puget_wind()
   elif args.grid == 'bbay':
      build_bbay_wind()
   else:
      print("Please input either bbay or puget as an argument")
main()
