#!/bin/bash

#$ -j y
#$ -S /bin/bash                                         #use bash shell
#S -V                                                   #inherit environment veriables
#-S -m ea
#-S M jjlab@uw.edu                                      #email completion messages here
#$ -N gm2ringsim                                        #job name
#$ -e /data/g2/users/labounty/logFiles/                 #output error messages to here
#$ -o /data/g2/users/labounty/logFiles/                 #output stdout to here
#$ -l scratch=25G

ROOTSTORAGE="/state/partition1"

nArgs=$(echo $#)
echo "Number of arguments:" $nArgs
echo $@
gm2Args=${@:6} #the first 5 arguments are spoken for, the rest will be passed to the gm2 call directly
echo "Arguments to the gm2 call are:" $gm2Args

scriptPath=$1 #the path to the fcl file
script=$2     #the name of the fcl file
infilepath=$3 #the path of an input file, here the g-2 tarball
infile=$4     #the name of an input file, here the g-2 tarball
outdir=$5     #the name of the directory where we should direct output

queue_dir="/home/labounty/stupid_queue/"

datestring=$(date +%Y_%m_%d_%H_%M_%S_%N)
echo $datestring

echo $scriptPath $script $infilepath $infile $outdir

return 1

#make sure the output directory exists
mkdir -p $outdir

date
echo $PATH

echo "Running python script on file: " $infile


#copy over the fcl file and the g-2 tarball (if it doesn't exist already)
cd $TMPDIR
pwd -P

while :
do
	nfiles=$( ls -l ${queue_dir} | wc -l)
	echo "$nfiles in directory"

	if [ "$nfiles" -le "10" ]
	then
		echo Processing!
		touch ${queue_dir}${datestring}
        if [[ ! -f $ROOTSTORAGE/${infile} ]]
        then
            echo "${infile} does not exist on this filesystem. copying now."
            rsync -vz --progress  ${infilepath}/${infile} $ROOTSTORAGE/
        fi
		rsync -vz --progress  ${scriptPath}/${script}  $TMPDIR/
		rm -f ${queue_dir}${datestring}
		break
	fi
	echo "waiting..."
	sleep 10
done 

pwd
ls -ltrh
ls -ltrh ${ROOTSTORAGE}

#untar the root file
cd ${ROOTSTORAGE}
tar -zxvf ${ROOTSTORAGE}/${infile}
ls -ltrh 

#create a bash script to exececute in the singularity container

#FILE="${TMPDIR}/singularity_script.sh"
FILE="singularity_script.sh"
logfile="gm2_output.log"
cd ${TMPDIR}

/bin/cat <<EOM >$FILE
#!/bin/bash

#setup gm2

export ${ROOTSTORAGE}/sim/docker/cvmfs/gm2.opensciencegrid.org/prod/external/ups/v6_0_7/Linux64bit+2.6-2.12/bin:$PATH
export PRODUCTS=${ROOTSTORAGE}/sim/docker/cvmfs/gm2.opensciencegrid.org/prod/g-2
source ${ROOTSTORAGE}/sim/env_run1final.sh
source ${ROOTSTORAGE}/sim/docker/cvmfs/gm2.opensciencegrid.org/prod/g-2/setup
setup gm2 v9_21_06 -q prof

#run the code, pass along the g-2 arguments
cd ${TMPDIR}
pwd 
ls -ltrh

#gm2 -c ${TMPDIR}/${script} -s ${ROOTSTORAGE}/${infile} ${gm2Args}
#gm2 -c ${TMPDIR}/${script} ${gm2Args}
gm2 -c ${TMPDIR}/${script} ${gm2Args} | tee ${logfile}
#gm2 -c ${script} ${gm2Args}

pwd
ls -ltrh

echo "All done with singularity."

EOM

ls -ltrh $FILE

#now that we have that created, check that it exists
if [[  -f $FILE ]]
then
    singularity exec -B ${ROOTSTORAGE}/sim/docker/cvmfs:/cvmfs -B ${TMPDIR}:${TMPDIR} -B ${ROOTSTORAGE}:${ROOTSTORAGE} ${ROOTSTORAGE}/sim/container/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl6\:latest /bin/bash $FILE
fi

#copy the output file back to the correct directory

while :
do
	nfiles=$( ls -l ${queue_dir} | wc -l)
	echo "$nfiles in directory"

	if [ "$nfiles" -le "10" ]
	then
		echo Processing!
		touch ${queue_dir}${datestring}
		rsync -vz --progress  $TMPDIR/*root ${outdir}/
		rsync -vz --progress  $TMPDIR/*fcl ${outdir}/
		rsync -vz --progress  $FILE ${outdir}/
		rm -f ${queue_dir}${datestring}
		break
	fi
	echo "waiting..."
	sleep 10
done 

echo "All done."
send_to_slack "All done with gm2ringsim, check: ${outdir}"
