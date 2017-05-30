# -*- coding: utf-8 -*-
"""
Created on Tue May 30 12:47:59 2017

@author: crosby
"""

import sys
import numpy as np

# Make meteo grid

# Add open earth python tools for D3D
sys.path.append('../openearthtools/python/OpenEarthTools/openearthtools/io/delft3d')
from grid import Grid


# Random grid
x = range(10)
y = range(10)
xgr, ygr = np.meshgrid(x,y)

# set x-origin, y-origin, and alf origin?, and coordinate system
properties = {'xori':0, 'yori':0, 'alfori':0, 'Coordinate System':'Cartesian'}

# Create grid object
test = Grid(x=xgr,y=ygr,properties=properties)

# Write to file  
test.write('test.grd')


