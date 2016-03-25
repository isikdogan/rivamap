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

# Read the input image
I1 = cv2.imread("1000.tif", cv2.IMREAD_UNCHANGED)
gm = georef.loadGeoMetadata("1000.tif")

# Create the filters that are needed to compute the singularity index
filters = singularity_index.SingularityIndexFilters()

# Compute the modified multiscale singularity index
psi, widthMap, orient = singularity_index.applyMMSI(I1, filters)

# Extract channel centerlines
nms = delineate.extractCenterlines(orient, psi)
centerlines = delineate.thresholdCenterlines(nms, tLow=0.01, tHigh=0.08)

# remove the overlapping response
numRow, numCol = centerlines.shape
padRow = numRow/10
padCol = numCol/10
centerlines[0:padRow, :] = 0
centerlines[:, 0:padCol] = 0
centerlines[-padRow:, :] = 0
centerlines[:, -padCol:] = 0

# Generate a raster map of the extracted channels
raster = delineate.generateRasterMap(centerlines, orient, widthMap, thickness=1)

# Save the images that are created at the intermediate steps
cv2.imwrite("mndwi.TIF", cv2.normalize(I1, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("nms.TIF", cv2.normalize(nms, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("centerlines.TIF", centerlines.astype(int)*255)

# An example of exporting a geotiff file
raster = preprocess.contrastStretch(raster)
raster = preprocess.double2im(raster, 'uint16')
georef.saveAsGeoTiff(gm, raster, "raster_geotagged.TIF")

# Export the (coordinate, width) pairs to a comma separated text file
georef.exportCSVfile(centerlines, widthMap, gm, "results.csv")

# Quiver plot
psi_s = psi[50:-150:4,250:-250:4]
orient_s = orient[50:-150:4,250:-250:4]

U = -psi_s * np.sin(orient_s)
V = psi_s * np.cos(orient_s)

plt.figure(figsize=(9,9))
ax = plt.gca()
ax.invert_yaxis()
Q = plt.quiver(U, V, scale=4, width=0.001, pivot='mid', headwidth=0, minlength=0)
plt.savefig("quiver.pdf")
