#!/bin/bash

#Josh LaBounty; Aug 9th, 2018
#	Version 1.0
#Script to start the experimental frontends which are located in /home/daq/labounty. This script will only work if the screens for each of the desired 
#	amc13XX exist and the frontends are stopped manually in the daq. This can be used in conjunction with the script changeCaloODB.sh to alter the ODB parameters
#	This will start the frontends with whatever their default parameters are, which as of writing this are (n,n,n). This isn't a good setting, so it may be necessary
#	to run the script twice (run this script -> change odb -> kill frontends -> run again)

#Example usage: bash frontend_test_start_script.sh 12345
#	This will start the frontends and will save the output of each of the frontends to files: frontend_output_caloXX_12345.txt 

#set -x #uncomment to display all commands on the stdout

#check if the run number is set. If not, use default.
if [ -z ${1+x} ]; then 
	runnum="00000"
	echo "WARNING: Run Number is unset. Seting to default ($runnum)"; 
else 
	runnum=$1
fi

#loop over all calorimeters
for num in `seq 1 24`; do
	echo "Starting frontend for calo $num"
	amc13=`printf amc13%02d $num`
	
	#check if the screens exist for caloXX
	screen -S $amc13 -X select . ; ding=$?
	dong=0
	if (( ding == dong )); then
		IFS= #necessary for the screen -X command to be passed successfully for some baffling reason
		txt_output=`printf frontend_output_calo%02d_%05d.txt $num $runnum`
		command=$"screen -S $amc13 -p 0 -X stuff 'cd /home/daq/labounty/gm2daq/frontends/CaloReadoutAMC13; ./frontend -e GM2 -h g2be1-data -i $num > $txt_output ;  "
		command+=$'\n'
		command+=$"'" 	#Building the command this way allows us to include the newline character
		#eval $command 	#uncomment this to actually evaluate the command. 
		#echo $command
		echo "     Frontend Started. Writing to file: $txt_output"
	else
		#If the frontends don't exist, dont do anything. Can later be modified to create the screens if we want.
		echo "     *************************Warning: Screen not found for $amc13"
	fi
	shift
done
