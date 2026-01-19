
#give a catalogue obtained from sextractor + ldactoasc, obtain a ds9 region file
from argparse import ArgumentParser 
import sys


import numpy as np
from python_tools.tools import extract_xy_from_file

def regfile(x,y,rad=40,outname="ouput.reg",radec=False,verbose=True):
    if type(rad) is list or type(rad) is np.ndarray:
        r = rad  
    else:
        if radec and rad==40:
            rad = 1 # arcsec
        r = np.ones_like(x)*rad
    endline = ")\n"
    if radec:
        endline = '"'+endline
    with open(outname,"w") as f:
        f.write("# Region file format: DS9 version 4.1\n")
        f.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n')
        if not radec:
            f.write("image\n")
        else:
            f.write("fk5\n")
        
        for xx,yy,rr in zip(x,y,r):
            f.write("circle("+str(xx)+","+str(yy)+","+str(rr)+endline)
    if verbose:
        print("Saved "+outname)
    return 0

def cat2reg(cat_file,rad=40,outname="ouput.reg",radec=False,verbose=True,index_x=1,index_y=2):
    if ".reg"!=outname[-4:]:
        outname += ".reg"
    x,y = extract_xy_from_file(cat_file,index_x=index_x,index_y=index_y)
    regfile(x=x,y=y,rad=rad,outname=outname,radec=radec,verbose=verbose)
    
if __name__=="__main__":
    parser = ArgumentParser(description="Convert catalogue to .reg file for DS9")
    parser.add_argument("-cf","--cat_file",dest="cat_file",help="Catalogue file (structure: 2 columns w. XY, commented lines starting with #)")
    parser.add_argument("-on","--out_name",dest="outname",help="Output name of .reg file",default="output.reg")
    parser.add_argument("-r","--radius",dest="rad",help="Radius of region",default=40)
    parser.add_argument("-radec",dest="radec",action="store_true",default=False,help="Input is given in Ra-Dec")
    parser.add_argument("-s","--silent",dest="silent",action="store_true",default=False,help="Silent (not verbose)")
    parser.add_argument("-ix","--index_x",dest="index_x",help="x-Index",default=1,type=int)
    parser.add_argument("-iy","--index_y",dest="index_y",help="y-Index", default=2,type=int)

    args     = parser.parse_args()
    cat_file = args.cat_file
    ix       = args.index_x
    iy       = args.index_y
    rad      = args.rad
    radec    = args.radec
    outname  = args.outname
    verbose  = not args.silent 
    cat2reg(cat_file=cat_file,rad=rad,outname=outname,radec=radec,verbose=verbose,index_x=ix,index_y=iy)