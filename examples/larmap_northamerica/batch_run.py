# -*- coding: utf-8 -*-
"""
Created on Thu April 28, 2016

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/

Runs the algorithms in batch on a set of images
"""

import os
import glob
import cv2
import numpy as np
from cne import singularity_index, delineate, preprocess, georef
from multiprocessing import Process
import time
import zipfile
import ntpath

# Reads images from base_dir and saves the results to save_dir
base_dir = "/home/leo/landsat_1x1_new/"
save_dir = "/home/leo/cne_output/"
landsat_images = glob.glob(base_dir + '*.zip')

def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def batch_compute(landsat_images):

    print len(landsat_images)

    filters = singularity_index.SingularityIndexFilters(minScale=1.2, nrScales=14)

    for landsat_image in landsat_images:

        temp_dir = os.path.join(save_dir, 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        with zipfile.ZipFile(landsat_image) as zf:
            for zippedname in zf.namelist():
                if zippedname.endswith('.tif'):
                    zf.extract(zippedname, path = temp_dir)
                    temp_im_dir = os.path.join(temp_dir, zippedname)

        I1 = cv2.imread(temp_im_dir, cv2.IMREAD_UNCHANGED)
        gm = georef.loadGeoMetadata(temp_im_dir)

        #delete the temp file
        os.remove(temp_im_dir)

        psi, widthMap, orient = singularity_index.applyMMSI(I1, filters)

        nms = delineate.extractCenterlines(orient, psi)
        centerlines = delineate.thresholdCenterlines(nms, tLow=0.012, tHigh=0.11)

        # remove the overlapping response
        numRow, numCol = centerlines.shape
        padRow = numRow/10
        padCol = numCol/10
        centerlines[0:padRow, :] = 0
        centerlines[:, 0:padCol] = 0
        centerlines[-padRow:, :] = 0
        centerlines[:, -padCol:] = 0

        #save results
        wrsname = ntpath.basename(landsat_image)
        georef.exportCSVfile(orient, psi, centerlines, widthMap, gm, os.path.join(save_dir, wrsname[:-4] + '.csv'))


if __name__ == '__main__':
    nrCores = 7
    print len(landsat_images)
    filelist_parts = chunks(landsat_images, (len(landsat_images)+nrCores)/nrCores)

    p0 = Process(target=batch_compute, args=([filelist_parts[0]]))
    p0.start()

    time.sleep(20)

    p1 = Process(target=batch_compute, args=([filelist_parts[1]]))
    p1.start()

    time.sleep(20)

    p2 = Process(target=batch_compute, args=([filelist_parts[2]]))
    p2.start()

    time.sleep(20)

    p3 = Process(target=batch_compute, args=([filelist_parts[3]]))
    p3.start()

    time.sleep(20)

    p4 = Process(target=batch_compute, args=([filelist_parts[4]]))
    p4.start()

    time.sleep(20)

    p5 = Process(target=batch_compute, args=([filelist_parts[5]]))
    p5.start()

    time.sleep(20)

    p6 = Process(target=batch_compute, args=([filelist_parts[6]]))
    p6.start()