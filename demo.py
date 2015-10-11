# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:16:41 2015

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/

Example use of the channel network extraction framework
"""

import cv2
from cne import ChannelNetworkExtractor
import time

#I1 = cv2.imread("./samples/MNDWI.tif", 0)
B3 = cv2.imread("./samples/B3.jpg", 0)
B6 = cv2.imread("./samples/B6.jpg", 0)

t = time.time()
cne = ChannelNetworkExtractor()
mndwi  = cne.mndwi(B3, B6)
cne.createFilters()
psi, _ = cne.applyFilters(mndwi)
nms    = cne.extractCenterlines()
tnms   = cne.thresholdCenterlines()
raster = cne.generateRasterMap()
print time.time() - t

cv2.imwrite("mndwi.png", cv2.normalize(mndwi, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("psi.png", cv2.normalize(psi, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("nms.png", cv2.normalize(nms, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("tnms.png", tnms.astype(int)*255)
cv2.imwrite("raster.png", cv2.normalize(raster, None, 0, 255, cv2.NORM_MINMAX))