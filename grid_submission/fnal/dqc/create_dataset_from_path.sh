path=$1
name=$2

echo "Creating dataset from .root files in :" $path

tmpfile="./tmp_sam_list_file"
echo $tmpfile
echo " " > ${tmpfile}
touch ${tmpfile}

for pathi in $path;
do
	echo "Starting:" $pathi
	files=$( ls -l $pathi*root )
	for file in $files;
	do
		if [[ "${file}" == *"root"* ]]; then  
			echo ${file} >> $tmpfile
		fi

		#if [[ "${file}" == *"root"* ]]; then  
		#	fullfile=$( ls ${pathi}${file} )
		#	echo ${fullfile} >> $tmpfile
		#fi
	done
done
echo "sam_add_dataset -e gm2 --no-rename  -f $tmpfile -n $name "


