# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 15:53:15 2017

@author: crosby
"""

try:
    x = 2
    y = x/0
except Exception as inst:
    print 'message is {:s}'.format(inst)
    