# -*- coding: utf-8 -*-
"""
"""

import os
import glob
import cv2
import numpy as np
from cne import singularity_index, delineate, preprocess, georef
from multiprocessing import Process
import time
import zipfile
import shutil
import ntpath

base_dir = "/home/leo/landsat8_median/"
save_dir = "/home/leo/csv/" #"/home/leo/geotiff/"
landsat_images = glob.glob(base_dir + '*.zip')

def chunks(l, n):
	n = max(1, n)
	return [l[i:i + n] for i in range(0, len(l), n)]

def batch_compute(landsat_images):

	print len(landsat_images)

	filters = singularity_index.SingularityIndexFilters(minScale=1.2, nrScales=16)

	for landsat_image in landsat_images:

		temp_dir = os.path.join(base_dir, 'temp')
		if not os.path.exists(temp_dir):
			os.makedirs(temp_dir)

		with zipfile.ZipFile(landsat_image) as zf:
			zf.extractall(temp_dir)

		temp_im_dir = glob.glob(temp_dir + '/*.tif')[0]
		I1 = cv2.imread(temp_im_dir, cv2.IMREAD_UNCHANGED)
		#adjust input
		mask = I1 == 0
		I1 = I1 + 0.5
		I1[I1<0] = 0
		I1[mask] = 0
		I1 = I1/1.5

		gm = georef.loadGeoMetadata(temp_im_dir)
		shutil.rmtree(temp_dir)

		psi, widthMap, orient = singularity_index.applyMMSI(I1, filters)

		nms = delineate.extractCenterlines(orient, psi)

		#nms = cv2.normalize(nms, None, 0, 255, cv2.NORM_MINMAX)
		#nms = cv2.equalizeHist(np.array(nms, dtype='uint8'))

		# Create a mask of valid pixels
		val_mask = I1 != 0
		val_mask = cv2.erode(np.array(val_mask, np.uint8), np.ones((44,44),np.uint8))
		nms[val_mask == 0] = 0

		centerlines = delineate.thresholdCenterlines(nms, tLow=0.01, tHigh=0.1)
		nms[centerlines == 0] = 0
		centerlines = nms
		#save results
		wrsname = ntpath.basename(landsat_image)
		georef.exportCSVfile(centerlines, widthMap, gm, os.path.join(save_dir, wrsname[:-4] + '.csv'))

		nms = nms * 16 #12 to 16 bit range
		nms = preprocess.double2im(nms, 'uint16')
		georef.saveAsGeoTiff(gm, nms, os.path.join(save_dir, wrsname[:-4] + '.tif'))

if __name__ == '__main__':
	batch_compute(landsat_images)
