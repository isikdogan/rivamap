# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:16:41 2015

@author: leo
"""
import cv2
from cne import ChannelNetworkExtractor
import time

I1 = cv2.imread("/home/leo/Desktop/Dropbox/cne2/LC81380452014304LGN00_mndwi_cropped.tif", 0)

t = time.time()
cne = ChannelNetworkExtractor()
cne.createFilters()
psi, _ = cne.applyFilters(I1)
nms    = cne.extractCenterlines()
tnms   = cne.thresholdCenterlines()
raster = cne.generateRasterMap()
print time.time() - t

cv2.imwrite("psi.png", cv2.normalize(psi, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("nms.png", cv2.normalize(nms, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("tnms.png", tnms.astype(int)*255)
cv2.imwrite("raster.png", cv2.normalize(raster, None, 0, 255, cv2.NORM_MINMAX))