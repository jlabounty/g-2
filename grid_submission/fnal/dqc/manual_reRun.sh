infile=`cat ./Missing_Run2F`

for file in $infile;
do
    thisfile="${file%?}"
    echo "This file:" $thisfile 
    eval `samweb -e gm2  locate-file ${thisfile} -v > temp.txt`
    locations=`cat temp.txt`
    echo $locations
    # echo "Location: "$fileLocation
    y=${locations%$'\n'*}
    y=${y:7}
    echo "Location: " $y
    thisfilewithpath="${y}/${thisfile}"
    echo "This file full: ${thisfilewithpath}"
    root -b -l -q extractNearline_init.C\(\"${thisfilewithpath}\",\"intermediate.sql\",1,2\)
    cat intermediate.sql >> output.sql
    # break
done