# -*- coding: utf-8 -*-
"""
"""

import glob, os
import zipfile

base_dir = "/home/leo/landsat8_1x1_grid/"

landsat_images = glob.glob(base_dir + '*.zip')

count_bad = 0

for landsat_image in landsat_images:

	try:
		zf = zipfile.ZipFile(landsat_image)
		ret = zf.testzip()
	except Exception, e:
		count_bad = count_bad + 1
		print str(count_bad) + ". " + landsat_image + " is bad"
		os.remove(landsat_image)
		ret = None

	if ret is not None:
		count_bad = count_bad + 1
		print str(count_bad) + ". " + landsat_image + " is bad"
		os.remove(landsat_image)