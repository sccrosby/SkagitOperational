# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 10:49:03 2017

@author: crosby
"""

import op_functions
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

fname = 'tide_pred_9448576.txt'

# Load Tide File
with open(fname) as fid:
    content = fid.readlines()

# Disregard Header    
content.pop(0)

# Format of time data
t_format = '%Y-%m-%d-%H-%M-%S'

# Parse time and tide data 
time = [datetime.strptime(x.split()[0],t_format) for x in content]    
tide = [float(x.split()[1]) for x in content]


# Plot Histogram of tide levels
plt.hist(tide,50,normed=1)
plt.show()



#%% Examine Likelihood of tide level exceedence for various durations and levels

t_file = 'tide_pred_9448576.txt'

t_level = np.arange(0,5,.25)
duration = [1, 3, 6]

prob = np.zeros([len(duration), len(t_level)])
for ti, tl in enumerate(t_level):
    for di, d in enumerate(duration):
        prob[di][ti] = op_functions.tide_exc_prob(t_file, tl, d)


import seaborn
plt.plot(t_level,prob[0],label='1-hour')
plt.plot(t_level,prob[1],label='3-hour')
plt.plot(t_level,prob[2],label='6-hour')
plt.legend()
plt.xlabel('Tide Level [m] NAVD88')
plt.ylabel('Probability of Exceedence')
#plt.grid()
#plt.show()
plt.savefig('TideLevelExceedenceProb.pdf')
























