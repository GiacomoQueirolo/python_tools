import numpy as np

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
    
    
    

