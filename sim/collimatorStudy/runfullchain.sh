cd /home/labounty/sim/trajectoryAnalysis/100points/
source hadd.sh
cd ..
python run_analysis.py -b
tar -zcvf allcsv.tar.gz ./100points/*/csv   
