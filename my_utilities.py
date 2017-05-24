# -*- coding: utf-8 -*-
"""
Created on Thu May 04 12:54:17 2017

@author: Crosby
"""

def clear_all():
    """Clears all the variables from the workspace of the spyder application."""
    gl = globals().copy()
    for var in gl:
        if var[0] == '_': continue
        if 'func' in str(globals()[var]): continue
        if 'module' in str(globals()[var]): continue

        del globals()[var]
        
#def reset():
#    from IPython import get_ipython
#    get_ipython().magic('reset -sf')
