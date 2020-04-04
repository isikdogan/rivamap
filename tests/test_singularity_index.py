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

def test_filters():
    '''
    Test for the filters that are created
    '''
    psi = singularity_index.SingularityIndexFilters()
    assert psi.G1[0][7] == 0.

def test_filter_creation():
    psi = singularity_index.SingularityIndexFilters()
    assert psi.isCreated == True
