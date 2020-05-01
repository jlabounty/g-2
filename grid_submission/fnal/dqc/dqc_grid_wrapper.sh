source /grid/fermiapp/products/common/etc/setups.sh  
source /cvmfs/gm2.opensciencegrid.org/prod/g-2/setup
setup gm2 v9_41_00 -q prof   
setup jobsub_client
setup fife_utils
date

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
#${pythonDir}install/bin/python ${input}${pythonFile} ${pythonArgs} ${process}

# https://root-forum.cern.ch/t/compile-and-run-from-command-prompt/13799
root -b -l <<EOF 
.L extractNearline.C;
runall("/pnfs/GM2/scratch/users/gm2pro/DQCAna/5110A/ProductionC/2020-04-11-19-10-
06/data", "ProdC_test3.sql", $2, $3)
EOF

set +x

mv ./*sql ${data}

ls -ltrh ${data}

echo "All done"

date
