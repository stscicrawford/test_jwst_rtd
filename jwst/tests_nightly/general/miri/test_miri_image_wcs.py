import os
import pytest
import numpy as np

from numpy.testing import utils

from jwst.assign_wcs import AssignWcsStep
from jwst.datamodels import ImageModel

from ..helpers import add_suffix

pytestmark = [
    pytest.mark.usefixtures('_jail'),
    pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
]

def test_miri_image_wcs(_bigdata):
    """
    Regression test of creating a WCS object and doing pixel to sky transformation.
    """
    suffix = 'assignwcsstep'
    output_file_base, output_file = add_suffix('miri_image_wcs_output.fits', suffix)

    input_file = os.path.join(_bigdata, 'miri', 'test_wcs', 'image', 'jw00001001001_01101_00001_MIRIMAGE_ramp_fit.fits')
    ref_file = os.path.join(_bigdata, 'miri', 'test_wcs', 'image', 'jw00001001001_01101_00001_MIRIMAGE_assign_wcs.fits')

    AssignWcsStep.call(input_file,
                       output_file=output_file_base, suffix=suffix
                       )
    im = ImageModel(output_file)
    imref = ImageModel(ref_file)
    x, y = np.mgrid[:1031, :1024]
    ra, dec = im.meta.wcs(x, y)
    raref, decref = imref.meta.wcs(x, y)
    utils.assert_allclose(ra, raref)
    utils.assert_allclose(dec, decref)
