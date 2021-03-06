
Description
===========

``jwst.assign_wcs`` is run in the beginning of the level 2B JWST pipeline.
It associates a WCS object with each science exposure. The WCS object transforms
positions in the detector frame to positions in a world coordinate frame - ICRS and wavelength.
In general there may be intermediate coordinate frames depending on the instrument.
The WCS is saved in the ASDF extension of the FITS file. It can be accessed as an attribute of
the meta object when the fits file is opened as a data model.

The forward direction of the transforms is from detector to world coordinates
and the input positions are 0-based.

``jwst.assign_wcs`` expects to find the basic WCS keywords in the 
SCI header. Distortion and spectral models are stored in reference files in the
`ASDF <http://asdf-standard.readthedocs.org/en/latest/>`__  format.

For each observing mode, determined by the value of ``EXP_TYPE`` in the science header,
assign_wcs retrieves reference files from CRDS and creates a pipeline of transforms from
input frame ``detector`` to a frame ``v2v3``. This part of the WCS pipeline may include
intermediate coordinate frames. The basic WCS keywords are used to create
the transform from frame ``v2v3`` to frame ``world``.



Basic WCS keywords and the transform from ``v2v3`` to ``world``
---------------------------------------------------------------

All JWST instruments use the following FITS header keywords to
define the transform from ``v2v3`` to ``world``:

``RA_REF``, ``DEC_REF`` - a fiducial point on the sky, ICRS, [deg]

``V2_REF``, ``V3_REF`` - a point in the V2V3 system which maps to ``RA_REF``, ``DEC_REF``, [arcsec]

``ROLL_REF`` - local roll angle associated with each aperture, [deg]

``RADESYS`` - standard coordinate system [ICRS]

These quantities are used to create a 3D Euler angle rotation between the V2V3 spherical system,
associated with the telescope, and a standard celestial system.


Using the WCS interactively
---------------------------

Once a FITS file is opened as a `DataModel` the WCS can be accessed as an attribute of the meta object.
Calling it as a function with detector positions as inputs returns the
corresponding world coordinates. Using MIRI LRS fixed slit as an example:

>>> from jwst.datamodels import ImageModel
>>> exp = ImageModel('miri_fixedslit_assign_wcs.fits')
>>> ra, dec, lam = exp.meta.wcs(x, y)
>>> print(ra, dec, lam)
    (329.97260532549336, 372.0242999250267, 5.4176100046836675)

The GRISM modes for NIRCAM and NIRISS have a slightly different calling structure,
in addition to the (x, y) coordinate, they need to know other information about the
spectrum or source object. In the JWST backward direction (going from the sky to
the detector) the WCS model also looks for the wavelength and order and returns
the (x,y) location of that wavelength+order on the dispersed image and the original
source pixel location, as entered, along with the order that was specified:

>>> form jwst.datamodels import ImageModel
>>> exp = ImageModel('nircam_grism_assign_wcs.fits')
>>> x, y, x0, y0, order = exp.meta.wcs(x0, y0, wavelength, order)
>>> print(x0, y0, wavelength, order)
    (365.523884327, 11.6539963919, 2.557881113, 2)
>>> print(x, y, x0, y0, order)
    (1539.5898464615102, 11.6539963919, 365.523884327, 11.6539963919, 2)


The WCS provides access to intermediate coordinate frames
and transforms between any two frames in the WCS pipeline in forward or
backward direction. For example, for a NIRSPEC fixed slits exposure,
which has been through the extract_2d step:

>>> exp = models.MultiSlitModel('nrs1_fixed_assign_wcs_extract_2d.fits')
>>> exp.slits[0].meta.wcs.available_frames
    ['detector', 'sca', 'bgwa', 'slit_frame', 'msa_frame', 'ote', 'v2v3', 'world']
>>> msa2detector = exp.slits[0].meta.wcs.get_transform('msa_frame', 'detector')
>>> msa2detector(0, 0, 2*10**-6)
    (5042.064255529629, 1119.8937888372516)

For each exposure, assign_wcs uses reference files and WCS header keywords
to create the WCS object. What reference files are retrieved
from CRDS is determined based on EXP_TYPE and other keywords in the science file header.


The assign_wcs step can accept any type of DataModel as input. In particular, for
multiple-integration datasets the step will accept either of these data products:
the slope results for each integration in the exposure, or the single slope image
that is the result of averaging over all integrations.

``jwst.assign_wcs`` is based on gwcs and uses the modeling, units and coordinates subpackages in astropy.

Software dependencies:

- `gwcs <https://github.com/spacetelescope/gwcs>`__ 0.7

- `numpy <http://www.numpy.org/>`__ 1.9 or later

- `astropy <http://www.astropy.org/>`__ 1.2.1 or later

- `asdf <http://asdf.readthedocs.io/en/latest/>`__ 1.1.1 or later
