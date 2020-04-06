import pytest

import sys, os
import numpy as np
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

from rivamap import delineate




def test_extractCenterlines():
    '''
    Unit test for extractCenterlines function
    '''
    psi = np.zeros((5,5))
    orient = np.zeros((5,5))
    # put some values in dummy psi
    psi[:,2] = 1
    # expect max values in interior to be held
    nms = delineate.extractCenterlines(orient,psi)
    # make assertion
    assert np.all(nms[1:4,2]) == np.all(psi[1:4,2])



def test_thresholdCenterlines():
    '''
    Unit test for thresholdCenterlines function
    '''
    # setup dummy case
    nms = np.zeros((5,5))
    nms[1:4,1] = 0.5
    nms[1:4,3] = 0.5
    nms[1:4,2] = 1
    c = delineate.thresholdCenterlines(nms,bimodal=False)
    # make assertion
    assert np.all(c[2,0:2]) == np.all([False,True])
