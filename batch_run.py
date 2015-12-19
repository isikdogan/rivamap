# -*- coding: utf-8 -*-
"""
"""

import os
import cv2
import numpy as np
from cne import singularity_index, delineate, preprocess, georef
from skimage.morphology import remove_small_objects
from multiprocessing import Process
import time

base_dir = "/run/media/leo/Backup/landsat8_north_america/"
save_dir = "/home/leo/csv/" #"/home/leo/geotiff/"
landsat_images = os.listdir(base_dir)

def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def batch_compute(landsat_images):

	print len(landsat_images)

	filters = singularity_index.SingularityIndexFilters(minScale=1.2, nrScales=16)

	for landsat_image in landsat_images:

	    B3 = cv2.imread(os.path.join(base_dir, landsat_image, landsat_image + '_B3.TIF'), 0)
	    B6 = cv2.imread(os.path.join(base_dir, landsat_image, landsat_image + '_B6.TIF'), 0)

	    I1 = preprocess.mndwi(B3, B6)
	    #I1 = preprocess.contrastStretch(I1)

	    psi, widthMap, orient = singularity_index.applyMMSI(I1, filters)

	    nms = delineate.extractCenterlines(orient, psi)

	    #nms = cv2.normalize(nms, None, 0, 255, cv2.NORM_MINMAX)
	    #nms = cv2.equalizeHist(np.array(nms, dtype='uint8'))

	    # Create a mask of valid pixels
	    val_mask = B6 > 0
	    val_mask = cv2.erode(np.array(val_mask, np.uint8), np.ones((221,221),np.uint8))
	    nms[val_mask == 0] = 0

	    #centerlines = delineate.thresholdCenterlines(nms, tLow=0.05, tHigh=0.3)
	    #centerlines = remove_small_objects(centerlines, min_size=8)
	    centerlines = nms

	    gm = georef.loadGeoMetadata(os.path.join(base_dir, landsat_image, landsat_image + '_B6.TIF'))
	    georef.exportCSVfile(centerlines, widthMap, gm, os.path.join(save_dir, landsat_image + '.csv'))

	    #georef.saveAsGeoTiff(gm, nms, os.path.join(save_dir, landsat_image + '_NMS.TIF'))

	    #cv2.imwrite(os.path.join(save_dir, landsat_image + '_NMS.TIF'), nms)

if __name__ == '__main__':

	nrCores = 3
	filelist_parts = chunks(landsat_images, (len(landsat_images)+1)/nrCores)

	p0 = Process(target=batch_compute, args=([filelist_parts[0]]))
	p0.start()

	time.sleep(60)

	p1 = Process(target=batch_compute, args=([filelist_parts[1]]))
	p1.start()

	time.sleep(45)

	p2 = Process(target=batch_compute, args=([filelist_parts[2]]))
	p2.start()
