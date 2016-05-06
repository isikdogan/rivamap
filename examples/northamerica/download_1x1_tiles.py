# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 18:32:19 2015

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/

Downloads images from the EarthEngine
"""

import urllib2
import ee
import zipfile
import os
import csv
import time
from StringIO import StringIO
import logging

logging.basicConfig(filename='warnings.log',level=logging.DEBUG)

download_dest = "/home/leo/landsat8_1x1_grid/"
check_dest = "/home/leo/landsat_1x1_new/"

ee.Initialize()

# Select 1x1 degree tiles on North America
northamerica = ee.FeatureCollection('ft:1Ep6prwb941jMjmMxqD_BsISZj6JCiAE76mFcAiYl') \
	.filterMetadata('CONTINENT', 'equals', 'North America')
tiles = ee.FeatureCollection('ft:15P7IFF53wKVGefe_c6Cb2RBnsUql-wgMAX5OBcmq')
spatialFilter = ee.Filter.intersects('.geo', None, '.geo', None, 10)
saveAllJoin = ee.Join.saveAll('scenes')
intersectJoined = saveAllJoin.apply(northamerica, tiles, spatialFilter)
northamerica_tiles = ee.List(intersectJoined.first().get('scenes'))

time.sleep(15)

numTiles = 4366
for i in range(35, numTiles - 1):

	checkpath = os.path.join(check_dest, 'tile' + str(i) + '.zip')
	savepath = os.path.join(download_dest, 'tile' + str(i) + '.zip')

	#check if file exists
	if(os.path.isfile(checkpath)):
		logging.warning('tile:' + str(i) + ' exists, skipping...')
		continue

	if(os.path.isfile(savepath)):
		logging.warning('tile:' + str(i) + ' exists, skipping...')
		continue

	print 'downloading ' + 'tile:' + str(i)

	current_tile = northamerica_tiles.get(i)
	tile_geometry = ee.Feature(current_tile).geometry().bounds()
	collection = ee.ImageCollection('LC8').filterBounds(tile_geometry)
	composite = ee.Algorithms.Landsat.simpleComposite(collection)
	ndwi = composite.normalizedDifference(['B3', 'B6'])
	ndwi = ndwi.clip(tile_geometry)

	try:
		zipurl = ndwi.getDownloadURL({'scale': 30})
	except Exception, e:
		logging.warning(e)
		continue

	try:
		response = urllib2.urlopen(zipurl, timeout=600)
		logging.info('downloaded tile' + str(i))
	except Exception, e:
		logging.warning(e)
		print 'waiting'
		time.sleep(30)
		continue

	time.sleep(15)

	filedata= response.read()


	with open(savepath, 'w') as f:
		f.write(filedata)
