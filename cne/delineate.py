# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 12:59:51 2015

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/
"""

import cv2
import numpy as np
from scipy.ndimage import sum as ndsum
from scipy.ndimage import label as ndlabel


def extractCenterlines(orient, psi):
    """ Use non-maxima suppression to extract centerlines.
    This function uses the previously computed singularity index response (psi)
    and the dominant orientation (orient).
    
    Inputs: (can be obtained by running the mmSingularityIndex function)
    psi -- the singularity index response
    orient -- local orientation at each spatial location (x,y)    
    
    Returns:
    nms -- Non-maxima suppressed singularity index response (centerlines)
    """

    # Bin orientation values
    Q = ((orient + np.pi/2) * 4 / np.pi + 0.5).astype('int') % 4

    # Handle borders
    mask = np.zeros(psi.shape, dtype='bool')
    mask[1:-1, 1:-1] = True

    # Find maxima along local orientation
    nms = np.zeros(psi.shape)
    for q, (di, dj) in zip(range(4), ((1, 0), (1, 1), (0, 1), (-1, 1))):
        for i, j in zip(*np.nonzero(np.logical_and(Q == q, mask))):
            if psi[i, j] > psi[i + di, j + dj] and psi[i, j] > psi[i - di, j - dj]:
                nms[i, j] = psi[i,j]

    return nms


def thresholdCenterlines(nms, tLow=0.1, tHigh=0.3):
    """ Use a continuity-preserving hysteresis thresholding to classify
    centerlines.
    
    Inputs:
    nms -- Non-maxima suppressed singularity index response

    Keyword Arguments:
    tLow -- lower threshold (default 0.1)
    tHigh -- higher threshold (default 0.3)

    Returns:
    centerlines -- a binary matrix that indicates centerline locations
    """
    
    # TODO: tune parameters on a dataset
    
    maxVal = np.max(nms)
    strongCenterline    = nms >= tHigh * maxVal
    centerlineCandidate = nms >= tLow * maxVal

    # Find connected components that has at least one strong centerline pixel
    strel = np.ones((3, 3), dtype=bool)
    cclabels, numcc = ndlabel(centerlineCandidate, strel)
    sumstrong = ndsum(strongCenterline, cclabels, range(1, numcc+1))
    centerlines = np.hstack((0, sumstrong > 0)).astype('bool')
    centerlines = centerlines[cclabels]

    return centerlines


def generateRasterMap(centerlines, orient, widthMap, thickness=5):
    """ Generate a raster map of channels. It draws a line of length
    w(x, y) and orientation θ(x, y) at each spatial location.
    
    Inputs:
    centerlines -- a binary matrix that indicates centerline locations
    orient -- local orientation at each spatial location (x,y)
    widthMap -- estimated width at each spatial location (x,y)
    
    Keyword Argument:
    thickness -- thickness of the lines (default 5)

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
