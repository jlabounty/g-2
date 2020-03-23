for run in {28..34};
do
	echo $run
	files=`ls ./*run${run}*root`
	echo $files
	for file in $files;
	do
		if [[ $file == *"root"* ]]; then
			echo $file
			run=$( echo $file | cut -d "_" -f 3 | cut -d "n" -f 2) 
			firstTwoNumbers=${run:0:2}
			echo $run
			echo "ifdh mv -D $file ./runs_${firstTwoNumbers}000/$run"
		fi
	done

done
