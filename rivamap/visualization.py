# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def generateRasterMap(centerlines, orient, widthMap, thickness=3):
    """ Generates a raster map of channels. It draws a line of length
    w(x, y) and orientation θ(x, y) at each spatial location.
    
    Inputs:
    centerlines -- a binary matrix that indicates centerline locations
    orient -- local orientation at each spatial location (x,y)
    widthMap -- estimated width at each spatial location (x,y)
    
    Keyword Argument:
    thickness -- thickness of the lines (default 3)

    Returns:
    raster -- the raster map
    """

    centerlineWidth       = widthMap[centerlines]
    centerlineOrientation = orient[centerlines]

    [row,col] = np.where(centerlines)

    x_off = -centerlineWidth * np.cos(centerlineOrientation)
    y_off =  centerlineWidth * np.sin(centerlineOrientation)
    lines = np.vstack((col-x_off, row-y_off, col+x_off, row+y_off)).T

    raster = np.zeros(centerlines.shape)

    for i in range(0, len(lines)):
        cv2.line(raster, (int(lines[i,0]), int(lines[i,1])), \
                         (int(lines[i,2]), int(lines[i,3])), 255, thickness)

    return raster


def generateVectorMap(centerlines, orient, widthMap, saveDest, thickness=0.2):
    """ Generates a vector map of channels. It draws a line of length
    w(x, y) and orientation θ(x, y) at each spatial location.
    
    Inputs:
    centerlines -- a binary matrix that indicates centerline locations
    orient -- local orientation at each spatial location (x,y)
    widthMap -- estimated width at each spatial location (x,y)
    saveDest -- output figure save destination
    
    Keyword Argument:
    thickness -- thickness of the lines (default 0.2)

    Returns:
    None (saves the figure at saveDest)
    """

    centerlineWidth       = widthMap[centerlines]
    centerlineOrientation = orient[centerlines]

    [row,col] = np.where(centerlines)

    x_off = -centerlineWidth * np.cos(centerlineOrientation)
    y_off =  centerlineWidth * np.sin(centerlineOrientation)
    lines = np.vstack((col-x_off, row-y_off, col+x_off, row+y_off)).T

    xlist = []
    ylist = []
    for line_segment in lines:
        xlist.append(line_segment[0])
        xlist.append(line_segment[2])
        xlist.append(None)
        ylist.append(line_segment[1])
        ylist.append(line_segment[3])
        ylist.append(None)

    R, C = widthMap.shape
    aspect_ratio = float(R)/C

    plt.figure(figsize=(10, 10*aspect_ratio))
    ax = plt.gca()
    ax.invert_yaxis()
    plt.plot(xlist, ylist,'b-', linewidth=thickness)
    #plt.plot(col, row,'k.', markersize=thickness)
    plt.axis('off')
    plt.savefig(saveDest)


def quiverPlot(psi, orient, saveDest):
    """ Generates a quiver plot that shows channel orientation
    and singularity index response strength.

    Inputs:
    psi -- singularity index response
    orient -- local orientation at each spatial location (x,y)
    saveDest -- output figure save destination

    Returns:
    None (saves the figure at saveDest)
    """

    # downsample
    psi_s = psi[::4,::4]
    orient_s = orient[::4,::4]

    U = -psi_s * np.sin(orient_s)
    V = psi_s * np.cos(orient_s)

    R, C = psi.shape
    aspect_ratio = float(R)/C

    plt.figure(figsize=(10, 10*aspect_ratio))
    ax = plt.gca()
    ax.invert_yaxis()
    plt.quiver(U, V, scale=4, width=0.001, pivot='mid', headwidth=0, minlength=0)
    plt.axis('off')
    plt.savefig(saveDest)