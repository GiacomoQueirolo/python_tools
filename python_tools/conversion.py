import numpy as np
import warnings
from astropy import units as u
from python_tools.read_fits import get_transf_matrix,get_header_entry,load_fitshead

def get_pixscale(file,trnsf_matrix=None,index=0):
    # note: trnsf_matrix must be in arcsec
    if trnsf_matrix is None:
        trnsf_matrix = get_transf_matrix(file,index=index,in_arcsec=True)
    pix_scale = ((trnsf_matrix[0][0]**2 + trnsf_matrix[0][1]**2)**.5) # "/pix
    return pix_scale

def radec2xy(file,ra,dec,trnsf_matrix=None,scihdr=None,index=0):
    # note trnsf_matrix not in arcsec!
    if trnsf_matrix is None:
        trnsf_matrix = get_transf_matrix(file,index=index,in_arcsec=False)
    if scihdr is None:
        scihdr = load_fitshead(file,HDU=index)
    CV1 = get_header_entry(scihdr,"CRVAL1")
    CV2 = get_header_entry(scihdr,"CRVAL2")
    CP1 = get_header_entry(scihdr,"CRPIX1")
    CP2 = get_header_entry(scihdr,"CRPIX2")
    #print("DEBUG ")
    #print(CV1,CV2,CP1,CP2)
    return _radec2xy(ra=ra,dec=dec,CV1=CV1,CV2=CV2,CP1=CP1,CP2=CP2,trnsf_matrix=trnsf_matrix)
    
def _radec2xy(ra,dec,CV1,CV2,CP1,CP2,trnsf_matrix):
    ra0,dec0      = ra-CV1,dec-CV2
    inv_trans_mat = np.linalg.inv(trnsf_matrix)
    x0,y0         = inv_trans_mat.dot([ra0,dec0])
    x             = x0 + CP1
    y             = y0 + CP2
    return x,y


def xy2radec(file,x,y,trnsf_matrix=None,scihdr=None,index=0):
    # remember: if this is given by sextractor/DS9, we need to subtract 1
    # note trnsf_matrix not in arcsec!
    if trnsf_matrix is None:
        trnsf_matrix = get_transf_matrix(file,index=index,in_arcsec=False)
    if scihdr is None:
        scihdr = load_fitshead(file,HDU=index)
    CV1 = get_header_entry(scihdr,"CRVAL1")
    CV2 = get_header_entry(scihdr,"CRVAL2")
    CP1 = get_header_entry(scihdr,"CRPIX1")
    CP2 = get_header_entry(scihdr,"CRPIX2") 
    return _xy2radec(x=x,y=y,CV1=CV1,CV2=CV2,CP1=CP1,CP2=CP2,trnsf_matrix=trnsf_matrix)

def _xy2radec(x,y,CV1,CV2,CP1,CP2,trnsf_matrix):
    x0,y0    = x-CP1,y-CP2
    ra0,dec0 = np.array(trnsf_matrix).dot([x0,y0])
    ra       = ra0  + CV1
    dec      = dec0 + CV2
    return ra,dec
    
def pixscale2transfmat(pixscale):
    # we create a transformation matrix encoding only the pixel scale (no rotation)
    # pixscale must be in ''/pix
    CD11 = pixscale
    CD12 = 0
    CD21 = CD12
    CD22 = CD11
    return np.array([[CD11,CD12],
                     [CD21,CD22]])
    
# copied from lenstronomy_SDSSJ1433 project
def e1e2_from_qphi(q,phi,deg=True):
    """
    transforms orientation angle and axis ratio into complex ellipticity moduli e1, e2

    :param phi: angle of orientation (in radian)
    :param q: axis ratio minor axis / major axis
    :return: eccentricities e1 and e2 in complex ellipticity moduli
    """
    if deg:
        warnings.warn("NOTE: assumed phi given in degree!")
        phi = np.array(phi)*u.deg.to("rad")

    c  = (1. - q) / (1. + q) 
    e1 = np.cos(2 * phi)*c
    e2 = np.sin(2 * phi)*c
    return e1, e2

def find_index(x,arr):
    """
    Find linear interpolation of the index given a value x 
    with respect to a grid defined by the array arr
    """
    arr = np.array(arr)
    #ind0 = np.where((arr-x)<0)[0][-1] #works but only for x being float
    # Find insertion index
    i = np.searchsorted(arr, x) - 1
    # Clip to valid range
    ind0 = np.clip(i, 0, len(arr) - 2)
    return ind0 + (x-arr[ind0])/(arr[ind0+1] -arr[ind0])

### test: verified
import copy
def test_conversion():
    # real transf matrix
    trnsf_matrix = np.array([[2.466090978207752e-06, 8.315533503603797e-06],
                             [8.315533503603797e-06, -2.466090978207752e-06]])
    # random values
    CV1,CV2 = 10,20
    CP1,CP2 = 30,240
    kw_gen = {"CV1":CV1,"CV2":CV2,"CP1":CP1,"CP2":CP2,"trnsf_matrix":trnsf_matrix}
    x_true,y_true = 40,-130

    x,y = copy.copy(x_true),copy.copy(y_true)
    for i in range(100):
        ra,dec = _xy2radec(x=x,y=y,**kw_gen)
        x,y    = _radec2xy(ra=ra,dec=dec,**kw_gen)
    np.testing.assert_almost_equal(x,x_true)
    np.testing.assert_almost_equal(y,y_true)
    return 0
    
def test_pixscale2transfmat():
    pxsc  = .6
    _pxsc = copy.copy(pxsc)
    for i in range(100):
        trsfM = pixscale2transfmat(_pxsc)
        _pxsc = get_pixscale(None,trnsf_matrix=trsfM)
    np.testing.assert_almost_equal(pxsc,_pxsc)
    return 0
