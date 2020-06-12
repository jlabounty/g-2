source ./.bash_profile

source /cvmfs/gm2.opensciencegrid.org/prod/g-2/setup
export PRODUCTS=/cvmfs/gm2.opensciencegrid.org/specials/sl7/prod/g-2:/cvmfs/gm2.opensciencegrid.org/specials/sl7/prod/external:$PRODUCTS
setup gm2 v9_44_00 -q prof

cd ./nearline_sl7/
source localProducts_gm2_v9_44_00_prof/setup 
. mrb s 
