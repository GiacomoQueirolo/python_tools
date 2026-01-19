import os
import numpy as np
from python_tools.read_fits import load_fits,load_fitshead,fits_with_hdr,get_transfM_from_PCij
from python_tools.conversion import xy2radec


import sys
from argparse import ArgumentParser 
from python_tools.tools import get_dir_basename,Read_Two_Column_File,Write_Two_Column_File 

if __name__=="__main__":
    parser = ArgumentParser(description="Convert the cat given from pixel values to Ra-Dec")
    parser.add_argument("-cf","--cat_file",dest="cat",help="Catalogue")
    parser.add_argument("-rf","--reference_file",dest="ref_file",help="Reference fits file")
    parser.add_argument("-ih","--index_header",dest="index_hdr",help="Index of header to read for conversion matrix",default=0)
    parser.add_argument("-not_ds9",dest="not_ds9",action="store_true",default=False,help="If activated, doesn't account for DS9/Sextractor starting from 1 (assuming you already corrected for it)")
    parser.add_argument("-on","--output_name",dest="output_name",help="Output name",default="out_radec.cat")

    args      = parser.parse_args()
    cat_file  = args.cat
    ref_file  = args.ref_file
    index_hdr = args.index_hdr
    out_file  = args.output_name
    not_ds9   = args.not_ds9
    # if the outfile is not the path for the outfile:
    if get_dir_basename(out_file)[0]=="":
        dir,_     = get_dir_basename(cat_file)
        out_file  = dir+out_file

    x,y = Read_Two_Column_File(cat_file)
    if not not_ds9:
        # MAPORCAVACCA correction
        x -=1
        y -=1
    # TODO: implement vectorisation
    #ra,dec = xy2radec(file=ref_file,x=x,y=y,index=index_hdr)
    ra,dec = [],[]
    for xi,yi in zip(x,y):
        rai,deci = xy2radec(file=ref_file,x=xi,y=yi,index=index_hdr)
        ra.append(float(rai))
        dec.append(float(deci))

    Write_Two_Column_File(ra,dec,out_file)
    