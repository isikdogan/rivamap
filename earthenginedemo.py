# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 18:32:19 2015

@author: leo
"""
import urllib2
import ee
import zipfile
import os
import csv
from StringIO import StringIO

download_dest = "/home/leo/landsat8_median/"

ee.Initialize()

#wrs_path = 44
#wrs_row = 34

with open('/home/leo/Documents/git/NARWidth_scene_list.csv', 'rb') as csvfile:
	reader = csv.DictReader(csvfile)
	for line in reader:
		wrs_path = int(line['PATH'])
		wrs_row = int(line['ROW'])

		print 'downloading ' + 'path:' + str(wrs_path) + ', row:' + str(wrs_row)

		collection = ee.ImageCollection('LC8') \
			.filterMetadata('WRS_PATH', 'equals', wrs_path) \
			.filterMetadata('WRS_ROW', 'equals', wrs_row)
		wrs = ee.FeatureCollection('ft:1_RZgjlcqixp-L9hyS6NYGqLaKOlnhSC35AB5M5Ll') \
			.filterMetadata('PATH', 'equals', wrs_path) \
			.filterMetadata('ROW', 'equals', wrs_row)

		composite = ee.Algorithms.Landsat.simpleComposite(collection)
		ndwi = composite.normalizedDifference(['B3', 'B6'])
		ndwi = ndwi.clip(wrs.geometry())

		try:
			zipurl = ndwi.getDownloadURL({'scale': 30})
		except Exception, e:
			print e
			continue

		response = urllib2.urlopen(zipurl)
		filedata= response.read()
		zipfile = zipfile.ZipFile(StringIO(filedata))

		savepath = os.path.join(download_dest, 'p' + str(wrs_path) + 'r' + str(wrs_row))

		zipfile.extractall(savepath)
		zipfile.close()







