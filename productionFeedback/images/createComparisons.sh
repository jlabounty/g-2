#Script to put the plots generated from the production fast feedback side by side. 
#	Joshua LaBounty
#	8/30/2018
#	Usage: bash createComparisons.sh
#	Requires: ./comparisons folder to have been created, baseline and comparison images
#		to exist already. To modify which baseline/comparison is used, alter the script
#		directly.

set -x

baseline='v9_05_00'
comparison='v9_06_00'

baselinelist=$( eval 'ls ./$baseline/*png')

comparisonlist= ''
basenames= ''
for file in $baselinelist
do
	filenew=${file:19}
	comparisonlist+=' '
	comparisonlist+='./'$comparison'/'$baseline
	comparisonlist+=$filenew

	basenames+=' '
	basenames+=$filenew
done

arrbase=($baselinelist)
arrcomp=($comparisonlist)
arrname=($basenames)

#create the comparison plots using imagemagic montage feature. each subplot should include a label which gives their name.
for ((i=0;i<${#arrbase[@]};++i)); do
	echo $i
	montage -mode concatenate -tile 1x -frame 5 -geometry +5+5 -label '%f'  ${arrbase[i]} ${arrcomp[i]} './comparisons/comparison_'$baseline'_'$comparison''${arrname[i]}
done

#create tarball of the images for easy sharing / archival purposes
tar -cvf './comparisons/comparison_'$baseline'_'$comparison'.tar' ./comparisons/*png
