
path="/data/g2/data/40M_MuonSimulation/"

cat errFiles.txt | while read p
do
	file=${p}
	echo "Submitting file:" $file
	#source test.sh $file
	qsub test.sh $file
done 
