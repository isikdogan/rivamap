import pytest

import sys, os
import numpy as np
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

from rivamap import singularity_index

def test_class_init():
    '''
    Test init of the SingularityIndexFilters class
    '''
    psi = singularity_index.SingularityIndexFilters()
    assert psi.minScale == 1.2

def test_class_nrScales():
    psi = singularity_index.SingularityIndexFilters()
    assert psi.nrScales == 15

def test_filters():
    '''
    Test for the filters that are created
    '''
    psi = singularity_index.SingularityIndexFilters()
    assert psi.G1[0][7] == 0.

def test_filter_creation():
    psi = singularity_index.SingularityIndexFilters()
    assert psi.isCreated == True

def test_applyMMSI():
    '''
    Test with just 1 scale
    '''
    t_input = np.array([[20,20,50,20,20],[20,20,55,20,20],[20,20,50,20,20]], dtype='uint8')
    filts = singularity_index.SingularityIndexFilters(nrScales=1)
    [psi, widthMap, orient] = singularity_index.applyMMSI(t_input,filts)
    # expect max response in the center
    psi_max = np.max(psi)
    psi_bool = psi==psi_max
    # make assertion
    assert psi_bool[1,2] == True

def test_applyMMSI_scales():
    '''
    Testing with more than just 1 scale size
    '''
    t_input = np.array([[20,20,50,20,20],[20,20,55,20,20],[20,20,50,20,20]], dtype='uint8')
    filts = singularity_index.SingularityIndexFilters(nrScales=2)
    [psi, widthMap, orient] = singularity_index.applyMMSI(t_input,filts)
    # expect max response in the center
    psi_max = np.max(psi)
    psi_bool = psi==psi_max
    # make assertion
    assert psi_bool[1,2] == True
