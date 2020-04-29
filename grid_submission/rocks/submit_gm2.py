import numpy as np
import os
import sys

import argparse
import datetime
import time

def main():
    jobstring = "qsub run_gm2_grid.sh "

    parser = argparse.ArgumentParser(description='Process grid submission options')
    parser.add_argument("--gm2-args", default=None, nargs='+')
    parser.add_argument("--infile", default=None, type=str)
    parser.add_argument("--inpath", default=None, type=str)
    parser.add_argument("--outpath", default=None, type=str)
    parser.add_argument("--tarfile", default=None, type=str)
    parser.add_argument("--tarpath", default=None, type=str)
    parser.add_argument("--localfile", default=None, type=str)
    parser.add_argument("--localpath", default=None, type=str)
    parser.add_argument("--njobs", default=1, type=int)
    parser.add_argument("--nmuons", default=0, type=int)
    parser.add_argument("-t", default=None, type=str)
    parser.add_argument("-o", default=None, type=str)


    ding = parser.parse_args(sys.argv[1:])

    if(ding.outpath is not None): #append random path
        ding.outpath = ding.outpath.rstrip("/")+"/"+str(int(time.time()))
        os.system("mkdir -p "+str(ding.outpath))
    for required in [ding.inpath, ding.infile, ding.tarpath, ding.tarfile, ding.outpath]:
        if( required is None):
            raise ValueError("ERROR: required variable not set.")
        jobstring += " "+str(required).rstrip("/")
    #if(ding.localfile is not None):
    #    jobstring += " "+str(ding.localpath).rstrip("/")
    #    jobstring += " "+str(ding.localfile).rstrip("/")
    #else:
    #    jobstring += " None None "
        

    if(ding.nmuons < 1):
        raise ValueError("ERROR: You must have 1+ muon per job")

    jobstring+= " -n "+str(ding.nmuons)
    if(ding.gm2_args is not None):
        for x in ding.gm2_args:
            jobstring += " "+str(x)

    for jobi in range(ding.njobs):
        jobstring_i = jobstring
        if(ding.t is not None):
            jobstring_i += " -T "+ding.t.rstrip("_")+"_"+str(jobi).zfill(5)+".root"
        if(ding.o is not None):
            jobstring_i += " -o "+ding.o.rstrip("_")+"_"+str(jobi).zfill(5)+".root"
        print(jobstring_i)
        os.system(jobstring_i)




if __name__ == "__main__":
    main()
