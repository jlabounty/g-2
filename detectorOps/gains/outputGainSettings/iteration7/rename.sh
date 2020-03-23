set -x

for calo in {1..24};
do

	mv gainSettings_Iteration6_calo${calo}.json gainSettings_Iteration7_calo${calo}.json

done

set +x
