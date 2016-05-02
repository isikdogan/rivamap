# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 12:59:51 2015

@author: Leo Isikdogan
Homepage: www.isikdogan.com
Project Homepage: http://live.ece.utexas.edu/research/cne/
"""

import numpy as np

def mndwi(green, mir):
    """ Computes the modified normalized difference water index
    
    Inputs:
    green -- green band (e.g. Landsat 8 band 3)
    mir -- middle infrared band (e.g. Landsat 8 band 6)
    
    Returns:
    mndwi -- mndwi response
    """
    
    green = im2double(green)
    mir = im2double(mir)
        
    numerator = green-mir
    denominator = green+mir
    numerator[denominator==0] = 0
    denominator[denominator==0] = 1
    
    mndwi = numerator / denominator
        
    return mndwi

def contrastStretch(I):
    """ Applies contrast stretch to an input image """
    return (I - np.min(I)) / (np.max(I) - np.min(I))


def im2double(I):
    """ Converts image datatype to float """
    if I.dtype == 'uint8':
        I = I.astype('float')/255
        
    if I.dtype == 'uint16':
        I = I.astype('float')/65535
    
    return I

def double2im(I, datatype):
    """ Converts double data array to image """

    if datatype == 'uint8':
        I = I * 255
        
    if datatype == 'uint16':
        I = I * 65535

    return I.astype(datatype)
