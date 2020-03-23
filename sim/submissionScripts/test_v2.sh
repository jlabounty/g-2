#!/bin/bash

#$ -j y
#$ -S /bin/bash						#use bash shell
#S -V							#inherit environment veriables
#-S -m ea 
#-S M jjlab@uw.edu					#email completion messages here
#$ -N g2PDF 						#job name
#$ -e /data/g2/users/labounty/logFiles/ 		#output error messages to here 
#$ -o /data/g2/users/labounty/logFiles/			#output stdout to here

script="CreatePDF_Hists.py"
scriptPath="/home/labounty/data/users/labounty/4D_PDF/"

file="${1##*/}" 

outdir=$2

date
echo $PATH

echo "Running python script on file: " $file / $1

cd $TMPDIR
cp $1 $TMPDIR/
cp ${scriptPath}${script} $TMPDIR/
 
pwd
ls -ltrh

#python script inputFile outputPath -b
python ${TMPDIR}/${script} ${TMPDIR}/${file} ${TMPDIR}/ -b 

ls -ltrh

echo "All done."
date

rm -f ${TMPDIR}/${script}
rm -f ${TMPDIR}/${file}

cp $TMPDIR/* $outdir

send_to_slack "Script processing file $1 has completed"
