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
    parser.add_argument('--submission-file', default='/gm2/app/users/labounty/submission/test4/grid_submission_wrapper.sh')
    parser.add_argument('--other-files', default=None, nargs="+", help='Other files to copy over (i.e. input root or config files perhaps)')
    parser.add_argument('-f', default=['/gm2/app/users/labounty/submission/test4/python_test.py'], nargs='+', help='Main python script')
    parser.add_argument('-d', default=None, type=str)
    parser.add_argument('--memory', default="2GB")
    parser.add_argument('--disk', default=None)
    parser.add_argument('--lifetime', default=None)
    parser.add_argument("--python-args", default=None, nargs='+')
    parser.add_argument("--test", default=False, type=bool)
    parser.add_argument("--tar", default="/pnfs/GM2/scratch/users/labounty/python.tar.gz")
    parser.add_argument('--python-custom', default='/gm2/app/users/labounty/github/g-2/fitting/',help='The custom python files which will be tarred up and sent to the grid node along with the existing python tarball')
    
    ding = parser.parse_args(sys.argv[1:])
    #print(ding)
    #print(ding.foo)

    jobstring += " --OS="+ding.OS 
    jobstring += ' --group='+ding.group
    jobstring += ' --memory='+ding.memory
    if(ding.disk is not None):
    	jobstring += ' --disk='+ding.disk
    if(ding.lifetime is not None):
    	jobstring += ' --expected-lifetime='+ding.lifetime

    if("pnfs" in ding.tar):
    	jobstring += ' --tar_file_name='+ding.tar
    else:
    	jobstring += ' --tar_file_name=dropbox://'+ding.tar

    python_lib_dir = "/pnfs/GM2/scratch/users/labounty/ding.tar.gz"
    to_tar = "tar -hzcvf "+python_lib_dir+" "+ding.python_custom+"*py"
    print(to_tar)
    if(not ding.test):
        os.system("rm -f "+python_lib_dir)
        os.system(to_tar)


    for x in ding.condor_req:
        jobstring += ' --append_condor_requirements='+x

    if(ding.d is None):
        defaultPath = "/pnfs/GM2/scratch/users/labounty/newscript/"
        newfolder = int(time.time())
        path = defaultPath+str(newfolder)
        if(not ding.test):
        	os.system("mkdir -p "+path)
        ding.d = path 

    if(ding.f is not None):
	#lets copy our script over to our output directory in scratch, for easier copying to grid nodes
        for f in ding.f:
            if(not ding.test):
            	os.system("cp "+f+" "+ding.d)
            fileName = f.split("/")[len(f.split("/")) -1]
            jobstring += ' -f '+ding.d+"/"+fileName

    if("pnfs" in python_lib_dir):
    	jobstring += ' -f '+python_lib_dir
    else:
    	jobstring += ' -f dropbox://'+python_lib_dir

    if(ding.other_files is not None):
        for f in ding.other_files:
            jobstring += ' -f '+f 

    jobstring += ' -d A '+ding.d+"/output"

    if(not ding.test):
    	os.system("cp "+ding.submission_file+" "+ding.d)
    new_sub_file = ding.submission_file.split("/")[len(ding.submission_file.split("/")) -1] 
    jobstring += " file://"+ding.d+"/"+new_sub_file
    for f in ding.f:
        file_split = f.split("/")
        jobstring += " "+file_split[len(file_split) - 1]
    if(ding.python_args is not None):
        for x in ding.python_args:
            jobstring += " "+x
    print(jobstring)
    if(not ding.test):
        print("Executing...")
    	os.system(jobstring+" | tee ./submission_output.log")
    with open("./submission.log","w") as file:
    	file.write(jobstring)
    if(not ding.test):
        os.system("cp ./submission*log "+ding.d)
    return jobstring

if __name__ == "__main__":
    main()
