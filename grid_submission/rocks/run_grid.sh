#!/bin/bash

#$ -j y
#$ -S /bin/bash                                         #use bash shell
#S -V                                                   #inherit environment veriables
#-S -m ea
#-S M jjlab@uw.edu                                      #email completion messages here
#$ -N QueueTest                                         #job name
#$ -e /data/g2/users/labounty/logFiles/                 #output error messages to here
#$ -o /data/g2/users/labounty/logFiles/                 #output stdout to here
#$ -l scratch=25G

ROOTSTORAGE="/state/partition1"

nArgs=$(echo $#)
echo $nArgs "arguments"
echo $@
pythonArgs=${@:6}
echo $pythonArgs

#constant args, 1-5
#[scriptPath, script, infilePath, infile, outpath]:

scriptPath=$1
script=$2

infilepath=$3
infile=$4

queue_dir="/home/labounty/stupid_queue/"

datestring=$(date +%Y_%m_%d_%H_%M_%S_%N)
echo $datestring

outdir=$5

echo $scriptPath $script $infilepath $infile $outdir

#return 1

mkdir -p $outdir

date
echo $PATH

echo "Running python script on file: " $infile

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
		rsync -vz --progress  ${infilepath}/${infile} $ROOTSTORAGE/
		rsync -vz --progress  ${scriptPath}${script} $TMPDIR/
		rm -f ${queue_dir}${datestring}
		break
	fi
	echo "waiting..."
	sleep 10
done 

pwd
ls -ltrh
ls -ltrh ${ROOTSTORAGE}

set -x
python ${TMPDIR}/${script} ${ROOTSTORAGE}/${infile}  $pythonArgs
set +x

ls -ltrh

echo "All done."
date

#rm -f ${TMPDIR}/${script}
rm -f ${ROOTSTORAGE}/${infile}

while :
do
	nfiles=$( ls -l ${queue_dir} | wc -l)
	echo "$nfiles in directory"

	if [ "$nfiles" -le "10" ]
	then
		echo Processing!
		touch ${queue_dir}${datestring}
		set -x
		rsync -vz --progress  $TMPDIR/* $outdir
		set +x
		rm -f ${queue_dir}${datestring}
		break
	fi
	echo "waiting..."
	sleep 10
done 

rm -f ${queue_dir}${datestring}

echo "Output file copied."
send_to_slack "Script $script processing file $infile with parameters $pythonArgs has completed. See: $outdir "
