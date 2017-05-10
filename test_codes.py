# -*- coding: utf-8 -*-
"""
Created on Thu May 04 13:49:35 2017

@author: Crosby
"""
# Clear workspace
import my_utilities
my_utilities.clear_all()
my_utilities.reset()

# Import libaraies
import op_functions
from datetime import datetime, timedelta

# Test functions
print op_functions.get_gmt_offset()

date_requested = datetime.utcnow() - timedelta(days=0)
#op_functions.get_hrdps(date_requested)

# Find latest
#from seek_latest_canadian_data import find_latest_canadian_data
#gribPrefix = 'CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_'
#(x,y) = find_latest_canadian_data(gribPrefix)

from op_functions import latest_hrdps_forecast
print latest_hrdps_forecast()



#http://dd.weather.gc.ca/model_hrdps/west/grib2/18/000/CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_2017050800_P000-00.grib2
#http://dd.weather.gc.ca/model_hrdps/west/grib2/18/000/CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_2017050818_P000-00.grib2

#http://dd.weather.gc.ca/model_hrdps/west/grib2/18/000/CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_2017050818_P000-00.grib2
#http://dd.weather.gc.ca/model_hrdps/west/grib2/18/048/CMC_hrdps_west_PRMSL_MSL_0_ps2.5km_2017050818_P048-00.grib2