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

I1 = cv2.imread("./samples/MNDWI.tif", 0)

t = time.time()
cne = ChannelNetworkExtractor()
cne.createFilters()
#I1     = cne.mndwi(B3, B6)
psi, _ = cne.applyFilters(I1)
nms    = cne.extractCenterlines()
tnms   = cne.thresholdCenterlines()
raster = cne.generateRasterMap()
print time.time() - t

cv2.imwrite("psi.png", cv2.normalize(psi, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("nms.png", cv2.normalize(nms, None, 0, 255, cv2.NORM_MINMAX))
cv2.imwrite("tnms.png", tnms.astype(int)*255)
cv2.imwrite("raster.png", cv2.normalize(raster, None, 0, 255, cv2.NORM_MINMAX))