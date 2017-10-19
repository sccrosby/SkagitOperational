# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 10:55:05 2017

@author: crosby
"""

import plot_functions
import get_param
import op_functions

(date_string, zulu_hour) = op_functions.latest_hrdps_forecast()

date_string = '20171017'
zulu_hour = 6

param = get_param.get_param_bbay()

# Make Validation Plots
print 'Making Validation Plots'
plot_functions.plot_bbay_wind_val(date_string, zulu_hour, param)
