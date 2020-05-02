voms-proxy-init -noregen -rfc -voms fermilab:/fermilab/gm2/Role=Analysis 
export XrdSecDEBUG=0  

directory="/pnfs/GM2/scratch/users/gm2pro/DQCAna/5112B/ProductionCRecovery/2020-04-30-20-20-17/data/"
filelist=$( ifdh ll ${directory} )
#echo "${filelist}"

#outfile="${data}test_${3}_${4}.sql"
#touch ${outfile}

njobs=100
thisjob=3

nfiles=`echo "${filelist}" | wc -l` 
echo "Number of files: " $nfiles

filesperjob=$( expr $nfiles / $njobs)
echo "Files per job: " $filesperjob

counter=0
#modulo=$(expr $njobs + $thisjob)
modulo=$njobs

for file in $filelist;
do
	if [[ "${file}" == *"root"* ]]; then
		thisfilenum=$( expr $counter % $modulo )
		if [[ "$thisfilenum" == "$thisjob" ]]; then
			echo $thisfilenum / $counter
			echo ${directory}$file
			xrdfilei=$( echo `bash ./pnfsToXRootD ${directory}${file}` |tr '\r' ' ' ) 
			echo "${xrdfilei}"
			xrdfile=`echo "x"${xrdfilei}`
			echo "${xrdfile}"
#			root -b -l extractNearline_init.C\(\"${xrdfile}\",\"intermediate.sql\",1,2\)
#			cat intermediate.sql >> ${outfile}
#			echo " " >> ${outfile}
#			break
		fi
		counter=$(expr ${counter} + 1 )
	fi

done
