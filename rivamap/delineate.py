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
from rivamap import preprocess

def extractCenterlines(orient, psi):
    """ Uses the previously computed singularity index response (psi)
    and the dominant orientation (orient) to extract centerlines.
    
    Inputs: (can be obtained by running applyMMSI function)
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


def thresholdCenterlines(nms, tLow=0.012, tHigh=0.12, bimodal=True):
    """ Uses a continuity-preserving hysteresis thresholding to classify
    centerlines.
    
    Inputs:
    nms -- Non-maxima suppressed singularity index response

    Keyword Arguments:
    bimodal -- true if the areas of rivers in the image are sufficiently
               large that the distribution of ψ is bimodal
    tLow -- lower threshold (automatically set if bimodal=True)
    tHigh -- higher threshold (automatically set if bimodal=True)

    Returns:
    centerlines -- a binary matrix that indicates centerline locations
    """

    if bimodal:
        #Otsu's algorithm
        nms = preprocess.double2im(nms, 'uint8')
        tHigh,_ = cv2.threshold(nms, nms.min(), nms.max(), cv2.THRESH_OTSU)
        tLow = tHigh * 0.1

    strongCenterline    = nms >= tHigh
    centerlineCandidate = nms >= tLow

    # Find connected components that has at least one strong centerline pixel
    strel = np.ones((3, 3), dtype=bool)
    cclabels, numcc = ndlabel(centerlineCandidate, strel)
    sumstrong = ndsum(strongCenterline, cclabels, range(1, numcc+1))
    centerlines = np.hstack((0, sumstrong > 0)).astype('bool')
    centerlines = centerlines[cclabels]

    return centerlines