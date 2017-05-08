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
op_functions.get_hrdps(date_requested)

