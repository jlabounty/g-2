
path="/data/g2/data/40M_MuonSimulation/"
outdir="/data/g2/users/labounty/4D_PDF/data/"

cat fileList.txt | while read p
do
	file=${path}${p}
	echo "Submitting file:" $file
	#source test.sh $file
	qsub test_v2.sh $file $outdir
done 
