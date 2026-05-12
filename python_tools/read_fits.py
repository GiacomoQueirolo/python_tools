import os
import numpy as np
from astropy.io import fits     
from python_tools.tools import get_dir_basename 

def get_header_entry(header,entry):
    try:
        return float(header[entry])
    except ValueError:
        return str(header[entry])


def load_fits(image_path,HDU=0):
    #load the image and read it as numpy array
    with fits.open(image_path,ignore_missing_end=True) as hdulist:
        image   = hdulist[HDU].data
    return image

def load_fitshead(image_path,HDU=0):
    #load the image header
    with fits.open(image_path,ignore_missing_end=True) as hdulist:
        head   = hdulist[HDU].header
    return head

def fits_with_copied_hdr(data,fits_parent_path,data_object="",data_history="",fits_res_namepath=None,overwrite=True,verbose=True):
    scihdr = load_fitshead(fits_parent_path,HDU=0)
    hdu    = fits.PrimaryHDU(data=data,header=scihdr)
    
    if data_object!="":
        hdu.header["OBJECT"]=str(data_object)
    
    if data_history!="":
        hdu.header["HISTORY"]=str(data_history)
    
    if fits_res_namepath is None:
        return hdu
    else:
        if verbose:
            print("saving file "+fits_res_namepath)
        hdu.writeto(fits_res_namepath, overwrite=overwrite)
        return 0
        
def fits_with_hdr(data,header,fits_res_namepath=None,overwrite=True,verbose=True):
    hdu    = fits.PrimaryHDU(data=data,header=header)
    
    if fits_res_namepath is None:
        return hdu
    else:
        if verbose:
            print("Saving file "+fits_res_namepath)
        hdu.writeto(fits_res_namepath, overwrite=overwrite)
        return 0

def fits_with_hdr_list(data,header_list,fits_res_namepath=None,overwrite=True,verbose=True):
    # data can be a list - in this case, have to have align it with the header 
    if type(data) is list:
        if len(data)==len(header_list)-1:
            if verbose:
                print("We assume to have a general header and individual headers for the data slices")
            data = [None,*data]
        elif len(data)== len(header_list):
            if verbose:
                print("We assume to have 1 header for each data - need to create an empty one for the PrimaryHDU")
            header_list= [fits.Header(),*header_list]
        else:
            raise ValueError(f"Input data can be a list, but have to be either same lenght of the header list, or 1 less than that")
            
    # by default the first is the primary one - must have no data
    primary_hdu = fits.PrimaryHDU(header=header_list[0])
     
    hdu_list    = [primary_hdu]
    for i,hd in enumerate(header_list[1:]):        
        if type(data) is list:
                di = data[i]
        else:
            if i==0:
                di = data
            else:
                di = None    
        hdu_i = fits.ImageHDU(data=di,header=hd)
        hdu_list.append(hdu_i)
    hdul = fits.HDUList(hdu_list)
    if fits_res_namepath is None:
        return hdul
    else:
        if verbose:
            print("Saving file "+fits_res_namepath)
        hdul.writeto(fits_res_namepath, overwrite=overwrite)
        return 0
        
def update_fits_hdr(file_path,new_header):
    data = load_fits(file_path)
    hdu  = fits.PrimaryHDU(data=data,header=new_header)
    print("Updating header of file "+file_path)
    hdu.writeto(file_path, overwrite=True)

def get_surrounding_pixels(matrix, rows, cols):
    surrounding_pixels = []
    for row, col in zip(rows,cols):
        srpxls  = []
        # Define the range of rows and columns to consider
        min_row = max(0, row - 1)
        max_row = min(len(matrix) - 1, row + 1)
        min_col = max(0, col - 1)
        max_col = min(len(matrix[0]) - 1, col + 1)

        # Iterate over the surrounding pixels
        for i in range(min_row, max_row + 1):
            for j in range(min_col, max_col + 1):
                # Exclude the center pixel
                if i != row or j != col:
                    srpxls.append([i, j])
        surrounding_pixels.append(srpxls)
    return surrounding_pixels



def get_transf_matrix(image_path,header=None,index=0,in_arcsec=True,verbose=True):
    if not header:
        header = load_fitshead(image_path,index)
    cd11,cd12,cd21,cd22 = "CD1_1","CD1_2","CD2_1","CD2_2"
    """
    already_in_arcsec   = False
    if "TELESCOP" in hdr.keys():
        if "JWST" in hdr["TELESCOP"]:
            hdr = load_fitshead(image_path,1)
            cd11,cd12,cd21,cd22 = "PC1_1","PC1_2","PC2_1","PC2_2"
            # these however are already in arcsec
            if not in_arcsec:
                already_in_arcsec = True
            else:
                in_arcsec=False    
    
    """ 
    try:
        CD1_1,CD1_2,CD2_1,CD2_2 = header[cd11],header[cd12],header[cd21],header[cd22]
        transform_pix2angle     = np.array([[CD1_1, CD1_2], [CD2_1, CD2_2]])
    except KeyError:
        if verbose:
            print("CDij not present, trying PCij and CDeltai")
        transform_pix2angle = get_transfM_from_PCij(header,in_arcsec=in_arcsec)
    #if already_in_arcsec and not in_arcsec:
    # transform_pix2angle /= 3600
    #elif
    if in_arcsec:
        transform_pix2angle *= 3600.
    return transform_pix2angle


def get_transfM_from_PCij(header,in_arcsec=True):
    # check https://www.aanda.org/articles/aa/full/2002/45/aah3859/aah3859.right.html#s:matrixspec
    # first 1-3 eqn
    PC1_1 = header["PC1_1"]
    PC1_2 = header["PC1_2"]
    PC2_1 = header["PC2_1"]
    PC2_2 = header["PC2_2"]
    CD1   = header["CDELT1"]
    CD2   = header["CDELT2"]
    transform_pix2angle = np.array([[PC1_1*CD1,PC1_2*CD1],[PC2_1*CD2,PC2_2*CD2]])
    if in_arcsec:
        transform_pix2angle *= 3600.
    return transform_pix2angle
    
def extract_layer(FILE,layer=None,ret_nm=False,name_fits=None):
    with fits.open(FILE) as f:
        for i,fi in enumerate(f):
            if layer==i or layer is None:
                image = fi.data
                hdr   = fi.header
                hdu = fits.PrimaryHDU(data=image,header=hdr)
                if name_fits is None:
                    name_fits = FILE.replace(".fits","_"+str(i)+".fits")
                print("Saving "+name_fits)    
                hdu.writeto(name_fits,overwrite=True)
    if ret_nm:
        return name_fits

def fits_name_w_pref(fits_path,pref,resp_err=True):
    # standardised way to get name of file with a give prefix
    dir,file = get_dir_basename(fits_path)
    if not resp_err or not "e." == file.replace(".fits","")[:2]:
        return dir+pref+file
    else:
        # if the file is the error of another file AND we respect the error prefix:
        # new_name = e.+pref+old_name(without e. pref)
        return dir+"e."+pref+file[2:]
        
def fits_err_name(fits_path):
    # standardised way to get name of error fits file
    return fits_name_w_pref(fits_path,pref="e.")
