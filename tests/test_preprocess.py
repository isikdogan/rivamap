import pytest

import sys, os
import numpy as np
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

from rivamap import preprocess

def test_mndwi():
    '''
    Unit test for function mndwi
    '''
    # define dummy green and nir band arrays
    green = np.array([10,20,30], dtype='uint8')
    nir = np.array([10,10,10], dtype='uint8')
    # apply the function
    result = preprocess.mndwi(green, nir)
    # make assertion
    assert np.all(result) == np.all([0, 10./30., 40./20.])

def test_contrastStretch():
    '''
    Unit test for contrastStretch function
    '''
    # make dummy image
    I = np.array([10,50,100])
    # apply function
    result = preprocess.contrastStretch(I)
    # make assertion
    assert np.all(result) == np.all([0, 40./90., 1.])

def test_im2double():
    '''
    Unit test for im2double function
    '''
    # create dummy image
    I = np.array([10,50,100], dtype='uint8')
    # apply function
    result = preprocess.im2double(I)
    # make assertion
    assert np.all(result) == np.all([10./255, 50./255, 100./255])

def test_double2im():
    '''
    Unit test for double2im function
    '''
    # create dummy image
    I = np.array([10./255, 50./255, 100./255])
    # apply function
    result = preprocess.double2im(I,'uint8')
    # make assertion
    assert np.all(result) == np.all(np.array([10,50,100], dtype='uint8'))
