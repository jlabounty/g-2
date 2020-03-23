for run in {30000..31000};
do
	echo $run
	nSubruns=$( ls -ltrh ./*run_${run}* | wc -l )
	echo $nSubruns
	firstTwoNumbers=${run:0:2}
	fileLimit=-1
	if [ $nSubruns \> $fileLimit ];
	then 
		echo "Doing syncronization for ${run}";
		echo "rsync -av --progress ./gm*run_${run}*root gm2pro@gm2gpvm03.fnal.gov:/pnfs/GM2/daq/run3/nearline/nearlineHists/runs_${firstTwoNumbers}000/${run}/"
	else
		echo "No subruns, skipping.";
	fi;
done
