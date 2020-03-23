for run in {28000..40000};
do
	echo $run
	firstTwoNumbers=${run:0:2}
	mkdir -p runs_${firstTwoNumbers}000/${run}
done
