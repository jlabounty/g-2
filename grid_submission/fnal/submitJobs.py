import os
import sys

import argparse
import datetime
import time

import ifdh


def main():
    jobstring = "jobsub_submit "

    parser = argparse.ArgumentParser(description='Process grid submission options')
    parser.add_argument('--foo', help='foo help', default='henlo', type=str)
    parser.add_argument('--OS', help='foo help', default='SL6', type=str)
    parser.add_argument('--group', default='fermilab', type=str)
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
    parser.add_argument('--dataset', default=None)
    parser.add_argument('--user', default="labounty", type=str)
    parser.add_argument("--python-args", default=None, nargs='+')
    parser.add_argument("--test", default=False, type=bool)
    parser.add_argument("-N", default=None)
    parser.add_argument("--tar", default="/pnfs/GM2/scratch/users/labounty/python.tar.gz")
    parser.add_argument("--schemas", default='xroot', choices=['xroot', 'None'])
    parser.add_argument("--python-lib-dir", default="/pnfs/GM2/scratch/users/labounty/ding.tar.gz")
    parser.add_argument('--python-custom', default='/gm2/app/users/labounty/github/g-2/fitting/',help='The custom python files which will be tarred up and sent to the grid node along with the existing python tarball')
    
    os.system("kx509")
    os.system("voms-proxy-init -noregen -rfc -voms fermilab:/fermilab/gm2/Role=Analysis")

    ding = parser.parse_args(sys.argv[1:])
    #print(ding)
    #print(ding.foo)

    # https://cdcvs.fnal.gov/redmine/projects/ifdhc/repository/revisions/master/entry/demo.py
    if(ding.dataset is not None):
        print("Using SAM dataset:", ding.dataset)
        if not os.environ.has_key("EXPERIMENT"):
            os.environ["EXPERIMENT"] = ding.group
        #establish the sam process
        i = ifdh.ifdh()
        projname=time.strftime("DQC_Labounty_test_%Y%m%d%H_%%d")%os.getpid()
        dataset=ding.dataset

        cpurl=i.startProject(str(projname), ding.group, str(dataset), ding.user, ding.group)
        time.sleep(2)
        cpurl=i.findProject(projname,ding.group)

#        consumer_id=i.establishProcess( cpurl, "demo","1", "bel-kwinith.fnal.gov","mengel" )
        print "got cpurl, consumer_id: ", cpurl 

        jobstring += " -e SAM_PROJECT_NAME="+projname+" -e GRID_USER="+ding.user+" -e EXPERIMENT="+ding.group
        ding.python_args.append(" sam-dataset-True")
        if( 'xroot' not in ding.schemas):
            ding.python_args.append(" schemas-None")

        os.system('echo "ifdh endProject '+cpurl+' ; \n ifdh cleanup" > endscript.sh')


    jobstring += " --OS="+ding.OS 
    jobstring += ' --group='+ding.group
    if("B" not in ding.memory):
        ding.memory = ding.memory+"GB"
    jobstring += ' --memory='+ding.memory
    if(ding.N is not None):
        jobstring += ' -N '+ding.N
    if(ding.disk is not None):
    	jobstring += ' --disk='+ding.disk
    if(ding.lifetime is not None):
    	jobstring += ' --expected-lifetime='+ding.lifetime

    if(ding.tar == "None"):
        print("Warning: Submitting with no tar file")
    elif("pnfs" in ding.tar):
    	jobstring += ' --tar_file_name='+ding.tar
    else:
    	jobstring += ' --tar_file_name=dropbox://'+ding.tar

    #python_lib_dir = "/pnfs/GM2/scratch/users/labounty/ding.tar.gz"
    python_lib_dir = ding.python_lib_dir 
    to_tar = "tar -hzcvf "+python_lib_dir+" "+ding.python_custom+"*{py,so}"
    print(to_tar)
    if((not ding.test) and ("None" not in python_lib_dir)):
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


    if("None" in python_lib_dir):
    	jobstring += ' '
    elif("pnfs" in python_lib_dir):
    	jobstring += ' -f '+python_lib_dir
    else:
    	jobstring += ' -f dropbox://'+python_lib_dir

    if(ding.other_files is not None):
        for f in ding.other_files:
            jobstring += ' -f '+f 

    jobstring += ' -d A '+ding.d+"/output"

    if(not ding.test):
    	os.system("cp "+ding.submission_file+" "+ding.d)
    	os.system("cp endscript.sh "+ding.d)
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
