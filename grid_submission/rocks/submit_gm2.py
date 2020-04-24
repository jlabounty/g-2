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
    parser.add_argument("--njobs", default=1, type=int)
    parser.add_argument("--nmuons", default=0, type=int)
    parser.add_argument("-t", default="gm2ringsim_output_", type=str)


    ding = parser.parse_args(sys.argv[1:])

    for required in [ding.inpath, ding.infile, ding.tarpath, ding.tarfile, ding.outpath]:
        if( required is None):
            raise ValueError("ERROR: required variable not set.")
        jobstring += " "+str(required).rstrip("/")

    if(ding.nmuons < 1):
        raise ValueError("ERROR: You must have 1+ muon per job")

    if(ding.gm2_args is not None):
        for x in ding.gm2_args:
            jobstring += " "+str(x)

    for jobi in range(ding.njobs):
        jobstring += " -T "+ding.t.rstrip("_")+"_"+str(jobi).zfill(5)+".root"
        print(jobstring)



if __name__ == "__main__":
    main()