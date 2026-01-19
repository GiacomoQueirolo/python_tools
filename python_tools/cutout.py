# coordinates
import os,glob,sys
import numpy as np
from argparse import ArgumentParser 
from python_tools.tools import get_dir_basename
from python_tools.conversion import radec2xy,get_pixscale
from python_tools.read_fits import load_fits,load_fitshead,get_transf_matrix,get_transfM_from_PCij,fits_with_hdr,get_header_entry,fits_err_name, fits_name_w_pref

Radius = 3 # arcsecs

def cutout_HST(FILE,ra,dec,Radius=Radius,pref="e",outname=None):
    # Define output name and load data
    if not outname:
        scioutname   = fits_name_w_pref(FILE,pref)
    else:
        scioutname   = outname
    scihdr       = load_fitshead(FILE)
    trnsf_matrix = get_transf_matrix(FILE,in_arcsec=False)
    scidata      = load_fits(FILE)

    # look for error frame
    err_name   = fits_err_name(FILE)
    erroutname = fits_err_name(scioutname)
    errdata    = None
    errhdr     = None
    if glob.glob(err_name)!=[]:
        print("Error image found")
        errdata = load_fits(err_name)
        errhdr  = load_fitshead(err_name)
        
    # use subfunct
    _cutout(ra,dec,trnsf_matrix,Radius,scidata,scihdr,scioutname,\
            errdata=errdata,errhdr=errhdr,erroutname=erroutname)
    return 0

def cutout_JWST(FILE,ra,dec,Radius=Radius,pref="e"):
    scioutname = fits_name_w_pref(FILE,pref)
    erroutname = fits_err_name(scioutname)
    # load data name
    try:
        scidata  = load_fits(FILE,1)
        scihdr   = load_fitshead(FILE,1)
        errdata  = load_fits(FILE,2)
        errhdr   = load_fitshead(FILE,2)
    except IndexError:
        # already extracted
        scidata  = load_fits(FILE,0)
        scihdr   = load_fitshead(FILE,0)
        ERR_FILE = fits_err_name(FILE)        
        errdata  = load_fits(ERR_FILE,0)
        errhdr   = load_fitshead(FILE,0)
    # get transf.Matrix from PCij
    trnsf_matrix = get_transfM_from_PCij(scihdr,in_arcsec=False) # in deg
    # update header with tranf. Matrix
    warning = "CDij terms obtained following Greisen et Calabretta (2002) , see "+str(sys.argv[0])
    scihdr["warning"] = warning
    errhdr["warning"] = warning
    for val_cdij,cdij in zip(trnsf_matrix.flatten(),["CD1_1","CD1_2","CD2_1","CD2_2"]):
        scihdr[cdij] = val_cdij
        errhdr[cdij] = val_cdij
    for CRP in "CRPIX1","CRPIX2":
        errhdr[CRP] = scihdr[CRP]
    # use subfunct
    _cutout(ra,dec,trnsf_matrix,Radius,scidata,scihdr,scioutname,\
            errdata=errdata,errhdr=errhdr,erroutname=erroutname)
    return 0
    
    
def _cutout(ra,dec,trnsf_matrix,Radius,scidata,scihdr,scioutname,errdata=None,errhdr=None,erroutname=None):
    if np.abs(np.diag(trnsf_matrix)).mean()>1e-4:
        # Very likely, it's in arcsec, while we expect it in degree
        raise RuntimeError("Warning: trnsf_matrix must be given in degree, not arcsec")

    # get pix coords:
    x,y  = radec2xy(None,ra,dec,trnsf_matrix=trnsf_matrix,scihdr=scihdr)
    pxsc = get_pixscale(None,trnsf_matrix=trnsf_matrix*3600) #the matrix is in degree
    rad  = Radius/pxsc
    
    # extract data (adapted from extractfits.py)
    outdata = scidata[int(y-rad)-1:int(y+rad),int(x-rad)-1:int(x+rad)]

    # record cutout 
    hdrs = [scihdr]
    if errdata is not None:
        hdrs = scihdr,errhdr
    for hdr in hdrs :
        hdr['history'] = 'extracted '+str(ra)+' '+str(dec)+' w. rad '+str(Radius)+'" with '+sys.argv[0]
        hdr['CRPIX1']  = hdr['CRPIX1'] - int(x-rad) + 1
        hdr['CRPIX2']  = hdr['CRPIX2'] - int(y-rad) + 1 
    # save science image
    fits_with_hdr(outdata,scihdr,fits_res_namepath=scioutname)
    # if present, repeat for error image
    if errdata is not None:
        outerrdata = errdata[int(y-rad)-1:int(y+rad),int(x-rad)-1:int(x+rad)]
        fits_with_hdr(outerrdata,errhdr,fits_res_namepath=erroutname)
    return 0

if __name__=="__main__":
    parser = ArgumentParser(description="Extract using Ra-Dec coordinates")
    parser.add_argument("-ra",dest="ra",type=float, help="Ra Center")
    parser.add_argument("-dec",dest="dec",type=float, help="Dec Center")
    parser.add_argument("-rad",dest="Radius",type=float, help="Radius extraction",default=Radius)
    parser.add_argument("-p", "--prefix", dest="prefix", default="e",
                  help="prefix of the output file, default=e")
    parser.add_argument("-tel", "--telescope", dest="telescope", default="HST",
                  help="Which telescope is this file from: HST (default) or JWST")

    parser.add_argument('FILE',help="FILE NAME")
    args = parser.parse_args()
    ra     = args.ra
    dec    = args.dec
    Radius = args.Radius
    FILE   = args.FILE
    pref   = args.prefix
    telescope = args.telescope
    if telescope == "HST":
        cutout_HST(FILE,ra,dec,Radius=Radius,pref=pref)
    elif telescope=="JWST":
        cutout_JWST(FILE,ra,dec,Radius=Radius,pref=pref)
    else:
        raise RuntimeError("Input either HST or JWST files, not "+telescope)
