import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import re

xOffset = 0.0
yOffset = 0.0

def Grid(fileName):
    gridFile = open(fileName,'r')
    lines = gridFile.readlines()
    count = 0
    for line in lines:
        m = re.search("Missing", line)
        if m:
            break
        count += 1
    split_line = lines[count+1].split()
    Nx = int(split_line[0])
    Ny = int(split_line[1])
    print("Grid(Nx, Ny): ",Nx,Ny)
    easting  = np.zeros((Ny,Nx), dtype='d')
    northing = np.zeros((Ny,Nx), dtype='d')
    N = len(lines)
    row = 0
    offset = count + 3  # header length

    #print(offset,offset+(N-offset)/2)
    for n in range(offset,offset+(N-offset)/2):
        split_line = lines[n].split()
        if split_line[0] == 'ETA=':
            j = int(split_line[1]) - 1
            for i in range(5):
                easting[j,i] = float(split_line[i+2]) - xOffset
            row = 1
        else:
            for i in range(len(split_line)):
                easting[j,i+5*row] = float(split_line[i]) - xOffset
            row += 1

    #print(offset+(N-offset)/2,N)
    for n in range(offset+(N-offset)/2,N):
        split_line = lines[n].split()
        if split_line[0] == 'ETA=':
            j = int(split_line[1]) - 1
            for i in range(5):
                northing[j,i] = float(split_line[i+2]) - yOffset
            row = 1
        else:
            for i in range(len(split_line)):
                northing[j,i+5*row] = float(split_line[i]) - yOffset
            row += 1

    return easting, northing, Nx, Ny
    #x = ma.masked_where(easting == 0.0, easting)
    #y = ma.masked_where(northing == 0.0, northing)
    #plt.figure()
    #plt.plot(x, y, 'k.')#, ms=0.5)
    #plt.grid(True)
    #plt.show()
