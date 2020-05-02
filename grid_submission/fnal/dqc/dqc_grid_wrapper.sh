#source /grid/fermiapp/products/common/etc/setups.sh  
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups.sh
source /cvmfs/gm2.opensciencegrid.org/prod/g-2/setup
setup gm2 v9_41_00 -q prof   
setup jobsub_client
setup fife_utils
setup ifdhc -z /cvmfs/fermilab.opensciencegrid.org/products/common/db
date

#voms-proxy-init -noregen -rfc -voms fermilab:/fermilab/gm2/Role=Analysis 

ls -ltrh

nArgs=$(echo $#)
echo $nArgs "arguments"
echo $@
pythonFile=$1
pythonArgs=${@:2}
echo $pythonFile
echo $pythonArgs

tar=$INPUT_TAR_FILE
echo "Tar file"
echo $tar
ls -ltrh $tar

cluster=$CLUSTER
process=$PROCESS
echo $cluster "/" $process

export data=$CONDOR_DIR_A/
echo "Data dir:" $data
ls -ltrh ${data}

export input=$CONDOR_DIR_INPUT/
echo "Input dir:" $input
ls -ltrh ${input}
# ding=$(ls ${input}/* | grep 'tar.gz')  
# tar -zxvf $ding
# ls -ltrh ${input}
# cp ./gm2/app/users/labounty/github/g-2/fitting/*py ${input}
# cp ./gm2/app/users/labounty/github/g-2/fitting/*py .
# cp ./gm2/app/users/labounty/github/g-2/fitting/*so .
# ls -ltrh ${input}

echo "Hello grid!" | tee ${data}hello_file_${process}.txt

ls -ltrh .

echo ${data}${pythonArgs}     

pythonDir="./python/"
set -x

cp ${input}* .
#cd ${input}

directory="/pnfs/GM2/scratch/users/gm2pro/DQCAna/5112B/ProductionCRecovery/2020-04-30-20-20-17/data/"
filelist=$( ifdh ll ${directory} )
echo "${filelist}"

outfile="${data}dqc_processing_${cluster}_${3}_${process}.sql"
touch ${outfile}

njobs=${3}
thisjob=${process}

modulo=$njobs  
counter=0


for file in $filelist;
do
	if [[ "${file}" == *"root"* ]]; then
		thisfilenum=$( expr $counter % $modulo )  
		if [[ "$thisfilenum" == "$thisjob" ]]; then 
			echo $counter / $thisfilenum
			echo ${directory}$file
			xrdfilei=$( echo `bash ${input}pnfsToXRootD ${directory}${file}` |tr '\r' ' ' ) 
			echo "${xrdfilei}"
			xrdfile=`echo "x"${xrdfilei}` #change root to xroot
			echo "${xrdfile}"
			echo "|" `echo ${xrdfile}` ";"

			#xrootd version
			root -b -l extractNearline_init.C\(\"${xrdfile}\",\"intermediate.sql\",1,2\)

			#ifdh cp version
			#ifdh cp -D ${directory}${file} .
			#root -b -l extractNearline_init.C\(\"./${file}\",\"intermediate.sql\",1,2\)
			#rm -f ./${file}

			cat intermediate.sql >> ${outfile}
			echo " " >> ${outfile}
		fi
		counter=$(expr ${counter} + 1 ) 
	fi

done

rm -f intermediate.sql

ls -ltrh .

set +x

cp ./*sql ${data}
cp ${input}*sql ${data}

ls -ltrh ${data}

echo "All done"

date







