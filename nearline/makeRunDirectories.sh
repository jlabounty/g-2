
outDir="/home/jlab/g-2/nearline/data/"
runStart=24000
runEnd=24020

for run in $(seq $runStart $runEnd);
do
	mainFolder="runs_"${run:0:2}"000"
	wholeFolder=$outDir$mainFolder/$run
	
	echo $wholeFolder
	mkdir -p $wholeFolder
done
