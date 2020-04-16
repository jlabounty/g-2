#source /grid/fermiapp/products/common/etc/setups.sh  
source /cvmfs/gm2.opensciencegrid.org/prod/g-2/setup
#setup gm2 v9_41_00 -q prof   
#setup ifdh_art v2_05_05 -q e15:prof:s65   
#setup python
#setup jobsub_client
#setup fife_utils
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


data=$CONDOR_DIR_A/
echo "Data dir:" $data
ls -ltrh ${data}

input=$CONDOR_DIR_INPUT/
echo "Input dir:" $input
ls -ltrh ${input}
ding=$(ls ${input}/* | grep 'tar.gz')  
tar -zxvf $ding
ls -ltrh ${input}
cp ./gm2/app/users/labounty/github/g-2/fitting/*py ${input}
cp ./gm2/app/users/labounty/github/g-2/fitting/*py .
ls -ltrh ${input}

echo "Hello grid!" | tee ${data}output_file.txt

ls -ltrh .

echo ${data}${pythonArgs}     

pythonDir="./python/"
set -x
${pythonDir}/install/bin/python ${input}${pythonFile} ${data}${pythonArgs}
set +x

ls -ltrh ${data}

echo "All done"

date
