# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 18:32:19 2015

@author: leo
"""

from landsat import search, downloader
import cv2
import numpy as np
import os, glob
import shutil
import csv
import tarfile
import requests
requests.packages.urllib3.disable_warnings()

download_dest = "/home/leo/landsat8_median/"

#read the list of tiles
with open('NARWidth_scene_list.csv', 'rb') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		path_row = "%03d,%03d" % (int(row['PATH']), int(row['ROW']))
		print 'downloading' + path_row

		# search for the scenes with the least cloud coverage
		s = search.Search()

		result = s.search(paths_rows=path_row,
						  lat=None,
						  lon=None,
						  limit=100,
						  start_date="2013-01-01", #YYYY-MM-DD
						  end_date="2015-12-19",
						  cloud_max=50)

		if result['status'] != u'SUCCESS':
			print 'cannot find an image for tile %s, skipping...' %(path_row)
			continue

		results = result['results']

		sceneIDs = []
		for r in results:
			if not r['sceneID'].startswith('LT'):
				sceneIDs.append(r['sceneID'])

		if sceneIDs is []:
			print 'cannot find an image for tile %s, skipping...' %(path_row)
			continue

		# Download
		for sceneID in sceneIDs:

			path = os.path.join(download_dest, str(sceneID))
			path_tile = os.path.join(download_dest, str(sceneID)[0:9])
			if os.path.isdir(path):
				print '%s already exists, skipping...' %(sceneID)
				continue

			bands = [3, 6]
			d = downloader.Downloader(download_dir=download_dest)
			downloaded = d.download([str(sceneID)], bands)
			src = downloaded.iteritems().next()[1]

			# if the source is google then unzip
			if src == 'google':
				tar = tarfile.open(path+'.tar.bz')
				tar.extractall(path=path)
				tar.close()
				os.remove(path+'.tar.bz')

			# copy selected bands to the corresponding tile folder
			bands = [3, 6]
			for band in bands:
				sel_band_path = os.path.join(path, str(sceneID) + '_B' + str(band) + '.TIF')
				des_band_path = os.path.join(path_tile, str(sceneID) + '_B' + str(band) + '.TIF')
				if not os.path.exists(path_tile):
					os.mkdir(path_tile)
				shutil.move(sel_band_path, des_band_path)

			shutil.rmtree(path)

		# Compute the median images for the tiles
		os.chdir(path_tile)
		landsat_images = glob.glob("*_B6.TIF")

		image_stack = np.zeros((7600, 7600, len(landsat_images)))
		cnt = 0
		for landsat_image in os.listdir(path_tile):
			if landsat_image.endswith("_B3.TIF"):
				im = cv2.imread(os.path.join(path_tile,landsat_image), 0)
				image_stack[:,:,cnt] = im[0:7600, 0:7600]
				cnt = cnt+1

		#TODO: don't forget to cleanup variables and folders, center crop tiles, and copy geodata
		median_image = np.mean(image_stack, axis=2)
		cv2.imwrite("median.png", cv2.normalize(median_image, None, 0, 255, cv2.NORM_MINMAX))


