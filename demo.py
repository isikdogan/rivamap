# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:16:41 2015

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/

Example use of the channel network extraction framework
"""

import cv2
import numpy as np
from cne import singularity_index, delineate, preprocess
#from skimage.morphology import remove_small_objects

# Read bands 3 and 6 of an example Landsat 8 image
B3 = cv2.imread("LC80270392014118LGN00_B3.TIF", 0)
B6 = cv2.imread("LC80270392014118LGN00_B6.TIF", 0)

# Compute the modified normalized difference water index of the input
I1 = preprocess.mndwi(B3, B6)

# Create the filters that are needed to compute the singularity index
filters = singularity_index.SingularityIndexFilters()

# Compute the modified multiscale singularity index
psi, widthMap, orient = singularity_index.applyMMSI(I1, filters)

# Extract channel centerlines
nms = delineate.extractCenterlines(orient, psi)

# Create a mask of valid pixels
val_mask = B6 > 0
val_mask = cv2.erode(np.array(val_mask, np.uint8), np.ones((221,221),np.uint8))
nms[val_mask == 0] = 0

centerlines = delineate.thresholdCenterlines(nms, tLow=0.01, tHigh=0.2)
#centerlines = remove_small_objects(centerlines, min_size=16)

# Save the images that are created at the intermediate steps
cv2.imwrite("mndwi.png", cv2.normalize(I1, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("psi.png", cv2.normalize(psi, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("nms.png", cv2.normalize(nms, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("centerlines.png", centerlines.astype(int)*255)