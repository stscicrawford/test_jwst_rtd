import pytest
from astropy.io import fits
from jwst.flatfield.flat_field_step import FlatFieldStep

from ..helpers import add_suffix

pytestmark = [
    pytest.mark.usefixtures('_jail'),
    pytest.mark.skipif(not pytest.config.getoption('bigdata'),
                       reason='requires --bigdata')
]

def test_flat_field_miri(_bigdata):
    """
    Regression test of flat_field step performed on MIRI data.
    """
    suffix = 'flat_field'
    output_file_base, output_file = add_suffix('flatfield1_output.fits', suffix)

    FlatFieldStep.call(_bigdata+'/miri/test_flat_field/jw00001001001_01101_00001_MIRIMAGE_assign_wcs.fits',
                       output_file=output_file_base, suffix=suffix
                       )
    h = fits.open(output_file)
    href = fits.open(_bigdata+'/miri/test_flat_field/jw00001001001_01101_00001_MIRIMAGE_flat_field.fits')
    newh = fits.HDUList([h['primary'],h['sci'],h['err'],h['dq']])
    newhref = fits.HDUList([href['primary'],href['sci'],href['err'],href['dq']])
    result = fits.diff.FITSDiff(newh,
                              newhref,
                              ignore_keywords = ['DATE','CAL_VER','CAL_VCS','CRDS_VER','CRDS_CTX'],
                              rtol = 0.00001
    )
    assert result.identical, result.report()
