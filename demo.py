# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:16:41 2015

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/

Example use of the channel network extraction framework
"""

import cv2
from cne import singularity_index, delineate, preprocess, georef

# Read bands 3 and 6 of an example Landsat 8 image
B3 = cv2.imread("LC81380452015067LGN00_B3.TIF", cv2.IMREAD_UNCHANGED)
B6 = cv2.imread("LC81380452015067LGN00_B6.TIF", cv2.IMREAD_UNCHANGED)

# Compute the modified normalized difference water index of the input
# and contrast stretch the result
I1 = preprocess.mndwi(B3, B6)
I1 = preprocess.contrastStretch(I1)

# Create the filters that are needed to compute the singularity index
filters = singularity_index.SingularityIndexFilters()

# Compute the modified multiscale singularity index
psi, widthMap, orient = singularity_index.applyMMSI(I1, filters)

# Extract channel centerlines
nms = delineate.extractCenterlines(orient, psi)
centerlines = delineate.thresholdCenterlines(nms)

# Generate a raster map of the extracted channels
raster = delineate.generateRasterMap(centerlines, orient, widthMap)

# Save the images that are created at the intermediate steps
cv2.imwrite("mndwi.TIF", cv2.normalize(I1, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("psi.TIF", cv2.normalize(psi, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("nms.TIF", cv2.normalize(psi, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("centerlines.TIF", centerlines.astype(int)*255)
cv2.imwrite("rasterMap.TIF", cv2.normalize(I1, None, 0, 255, cv2.NORM_MINMAX))

# An example of exporting a geotiff file
gm = georef.loadGeoMetadata("LC81380452015067LGN00_B6.TIF")
psi = preprocess.contrastStretch(psi)
psi = preprocess.double2im(psi, 'uint16')
georef.saveAsGeoTiff(gm, psi, "psi_geotagged.TIF")

# Export the (coordinate, width) pairs to a comma separated text file
georef.exportCSVfile(centerlines, widthMap, gm, "results.csv")