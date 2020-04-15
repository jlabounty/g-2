import os
import sys

import argparse
import datetime
import time


def main():
    jobstring = "jobsub_submit "

    parser = argparse.ArgumentParser(description='Process grid submission options')
    parser.add_argument('--foo', help='foo help', default='henlo', type=str)
    parser.add_argument('--OS', help='foo help', default='SL6', type=str)
    parser.add_argument('--group', default='fermilab')
    parser.add_argument('--condor-req', default=['\'(TARGET.HAS_CVMFS_gm2_opensciencegrid_org==true)\'', 
                                                 '\'(TARGET.HAS_SINGULARITY=?=true||TARGET.IFOS_Installed=?="SL6")\' '],
                                                  nargs='+')
    parser.add_argument('--submission-file', default='/gm2/app/users/labounty/submission/test4/grid_test.sh')
    parser.add_argument('--other-files', default=None, nargs="+", help='Other files to copy over (i.e. input root or config files perhaps)')
    parser.add_argument('-f', default=['/gm2/app/users/labounty/submission/test4/python_test.py'], nargs='+', help='Main python script')
    parser.add_argument('-d', default=None, type=str)
    parser.add_argument('--memory', default="2GB")
    parser.add_argument("--python-args", default=None, nargs='+')
    
    '''
    --resource-provides=usage_model=OPPORTUNISTIC 
    --OS=SL5,SL6 
    --group=fermilab 
    --append_condor_requirements='(TARGET.HAS_CVMFS_gm2_opensciencegrid_org==true)' 
    --append_condor_requirements='(TARGET.HAS_SINGULARITY=?=true||TARGET.IFOS_Installed=?="SL6")' 
    -f /gm2/app/users/labounty/submission/test4/python_test.py 
    file:///gm2/app/users/labounty/submission/test4/grid_test.sh
    '''

    ding = parser.parse_args(sys.argv[1:])
    #print(ding)
    #print(ding.foo)

    jobstring += " --OS="+ding.OS 
    jobstring += ' --group='+ding.group
    jobstring += ' --memory='+ding.memory

    for x in ding.condor_req:
        jobstring += ' --append_condor_requirements='+x

    if(ding.f is not None):
        for f in ding.f:
            jobstring += ' -f '+f 
    if(ding.other_files is not None):
        for f in ding.other_files:
            jobstring += ' -f '+f 

    if(ding.d is None):
        defaultPath = "/pnfs/GM2/scratch/users/labounty/newscript/"
        newfolder = int(time.time())
        path = defaultPath+str(newfolder)
        #os.system("mkdir -p "+path)
        ding.d = path 
    jobstring += ' -d A '+ding.d

    jobstring += " file://"+ding.submission_file
    for f in ding.f:
        file_split = f.split("/")
        jobstring += " "+file_split[len(file_split) - 1]
    if(ding.python_args is not None):
        for x in ding.python_args:
            jobstring += " "+x
    print(jobstring)
    return jobstring

if __name__ == "__main__":
    main()