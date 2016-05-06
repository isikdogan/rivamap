# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 12:59:51 2015

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/
"""

import csv
import warnings
import numpy as np
from osgeo import osr, gdal

class GeoMetadata:
    def __init__(self):
        self.projection = None
        self.geotransform = None
        self.rasterXY = None
    
        
def loadGeoMetadata(filepath):
    """ Reads metadata from a geotiff file
    
    Inputs:
    filepath -- path to the file
    
    Returns:
    gm -- metadata
    """
    ds = gdal.Open(filepath)
    
    if ds is None:
        raise ValueError('Cannot read file')
    
    gm = GeoMetadata()
    gm.projection   = ds.GetProjection()
    gm.geotransform = ds.GetGeoTransform()
    gm.rasterXY = (ds.RasterXSize, ds.RasterYSize)
    
    if gm.projection is None:
        warnings.warn('No projection found in the metadata')
    
    if gm.geotransform is None:
        warnings.warn('No geotransform found in the metadata')
    
    # Close file
    ds = None
    
    return gm
    
    
def saveAsGeoTiff(gm, I, filepath):
    """ Saves a raster image as a geotiff file
    
    Inputs:
    gm -- georeferencing metadata
    I -- raster image
    filepath -- path to the file    
    """
    
    if (I.shape[1] != gm.rasterXY[0]) and (I.shape[0] != gm.rasterXY[1]):
        raise ValueError('Image size does not match the metadata')
    
    DATA_TYPE = {
      "uint8": gdal.GDT_Byte,
      "int8": gdal.GDT_Byte,
      "uint16": gdal.GDT_UInt16,
      "int16": gdal.GDT_Int16,
      "uint32": gdal.GDT_UInt32,
      "int32": gdal.GDT_Int32,
      "float32": gdal.GDT_Float32,
      "float64": gdal.GDT_Float64
    }

    driver = gdal.GetDriverByName('GTiff')
     
    ds = driver.Create(filepath, I.shape[1], I.shape[0], 1, DATA_TYPE[I.dtype.name])
    
    ds.SetGeoTransform(gm.geotransform)
    ds.SetProjection(gm.projection)
    ds.GetRasterBand(1).WriteArray(I)
    ds.FlushCache()
    
    ds = None
    

def pix2lonlat(gm, x, y):
    """ Convers pixel coordinates into longitude and latitude
    
    Inputs:
    gm -- georeferencing metadata
    x, y -- pixel coordinates
    
    Returns:
    lon, lat -- longitude and latitude
    """
    
    sr = osr.SpatialReference()
    sr.ImportFromWkt(gm.projection)
    ct = osr.CoordinateTransformation(sr,sr.CloneGeogCS())

    lon_p = x*gm.geotransform[1]+gm.geotransform[0]
    lat_p = y*gm.geotransform[5]+gm.geotransform[3]

    lon, lat, _ = ct.TransformPoint(lon_p, lat_p)
    
    return lon, lat


def lonlat2pix(gm, lon, lat):
    """ Convers longitude and latitude into pixel coordinates
    
    Inputs:
    gm -- georeferencing metadata
    lon, lat -- longitude and latitude
    
    Returns:
    x, y -- pixel coordinates
    """
    
    sr = osr.SpatialReference()
    sr.ImportFromWkt(gm.projection)
    ct = osr.CoordinateTransformation(sr.CloneGeogCS(),sr)

    lon_p, lat_p, _ = ct.TransformPoint(lon, lat)
    x = (lon_p - gm.geotransform[0]) / gm.geotransform[1]
    y = (lat_p - gm.geotransform[3]) / gm.geotransform[5]

    return int(x), int(y)


def exportCSVfile(centerlines, widthMap, gm, filepath):
    """ Exports (coordinate, width) pairs to a comma separated text file
    
    Inputs:
    centerlines -- a binary matrix that indicates centerline locations
    widthMap -- estimated width at each spatial location (x,y)
    gm -- georeferencing metadata
    filepath -- path to the file
    
    """
    
    centerlineWidth = widthMap[centerlines]
    [row,col] = np.where(centerlines)
    
    with open(filepath, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["width","lat","lon"])
        
        for i in range(0, len(centerlineWidth)):
            lon, lat = pix2lonlat(gm, col[i], row[i])
            writer.writerow([centerlineWidth[i], lat, lon])
