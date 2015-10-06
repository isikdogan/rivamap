# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:16:41 2015

@author: leo
"""
import cv2
from ChannelNetworkExtractor import ChannelNetworkExtractor

I1 = cv2.imread("/home/leo/Desktop/Dropbox/cne2/LC81380452014304LGN00_mndwi_cropped.tif", 0)
cne = ChannelNetworkExtractor()
cne.createFilters()
psi, orient = cne.applyFilters(I1)

cv2.imwrite("pos_psi.png", cv2.normalize(psi, None, 0, 255, cv2.NORM_MINMAX))