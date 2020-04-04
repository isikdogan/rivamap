import pytest

import sys, os
import numpy as np
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

from rivamap import georef

def test_metadata():
    '''
    Unit test for GeoMetadata class initiation
    '''
    gm = georef.GeoMetadata()
    # assertion
    assert gm.projection == None
