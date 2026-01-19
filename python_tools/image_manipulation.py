import numpy as np


def mask_old(image,coord_x,coord_y,rad,inout="in"):
    mask = np.ones_like(image)    
    for i in range(len(mask)):
        for j in range(len(mask[0])):
            R = np.sqrt((j-coord_x)**2 +(i-coord_y)**2)
            if inout=="in":
                if R<=rad:
                    mask[i][j]=0
            elif inout=="out":
                if R>rad:
                    mask[i][j]=0
            else:
                raise RuntimeError("Parameter inout can be 'in' or 'out', not "+str(inout))
    return mask
    
def mask_in(coord_x,coord_y,rad,mask):
    ny,nx = mask.shape
    y,x = np.ogrid[:ny,:nx]
    R = np.hypot(x-coord_x,y-coord_y)
    mask  *= R>=rad
    return mask
    
def mask_out(coord_x,coord_y,rad,mask):
    ny,nx = mask.shape
    y,x = np.ogrid[:ny,:nx]
    R = np.hypot(x-coord_x,y-coord_y)
    mask  *= R<rad
    return mask



# chatgpt is always much better -> unecessary, but def. cooler and more efficient
def mask(image, coord_x, coord_y, rad, inout="in"):
    """
    Create a circular mask with radius `rad` centered at (coord_x, coord_y).
    
    Parameters
    ----------
    image : ndarray
        The reference image (only its shape is used).
    coord_x, coord_y : float
        Circle center coordinates (in pixel units).
    rad : float
        Radius of the circle.
    inout : {'in', 'out'}, optional
        If 'in', mask inside the circle. If 'out', mask outside the circle.
    
    Returns
    -------
    mask : ndarray
        Binary mask with ones for unmasked pixels and zeros for masked pixels.
    """
    y, x = np.ogrid[:image.shape[0], :image.shape[1]]
    dist = np.sqrt((x - coord_x) ** 2 + (y - coord_y) ** 2)

    if inout == "in":
        mask = (dist > rad).astype(image.dtype)
    elif inout == "out":
        mask = (dist <= rad).astype(image.dtype)
    else:
        raise RuntimeError(f"Parameter inout can be 'in' or 'out', not {inout!r}")

    return mask


def get_fwhm(profile_1D,x_projdata=None):
    if x_projdata is None:
        x_projdata=np.arange(len(profile_1D))
    x0 = 0
    x1 = len(profile_1D)
    half_max = np.max(profile_1D)/2.
    max_projdata_i = np.where(profile_1D[x0:x1]==np.max(profile_1D[x0:x1]))[0][0]
    arr_lft = abs(profile_1D[x0:x1][:max_projdata_i]-half_max)
    res_lft_i = np.where(arr_lft==np.min(arr_lft))[0][0]
    dlft = abs(res_lft_i-max_projdata_i)
    arr_rgt = abs(profile_1D[x0:x1][max_projdata_i:]-half_max)
    res_rgt_i = np.where(arr_rgt==np.min(arr_rgt))[0][0]+max_projdata_i
    drght = res_rgt_i-max_projdata_i
    #sig_i = (dlft+drght)/2. # this is the sigma lenght in indeces
    fwhm_i = (dlft+drght) # this is the FWHM in indexes
    fwhm_pix = (x_projdata[x0:x1][int(fwhm_i)]-x_projdata[x0:x1][0])
    return fwhm_pix
    