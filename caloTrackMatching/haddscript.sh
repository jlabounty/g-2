cd ./data/

# Run 2C
runstart=25894
runend=26024
name="run2c"
rm -f ../tracks_${name}.root 
hadd -f -T ../tracks_${name}.root ./tracksOnly*_gm2tracker_ana*_${runstart..runend}*root 

rm -f ../clusters_${name}.root 
hadd -f -T ../clusters_${name}.root ./old/clustersOnly*_gm2tracker_ana*_${runstart..runend}*root  

rm -f ../matchedTracks_${name}.root 
hadd -f -T ../matchedTracks_${name}.root ./matchedTracks*_gm2tracker*_${runstart..runend}*root

#EndGame
runstart=16908
runend=17528
name="eg"

rm -f ../tracks_${name}.root 
hadd -f -T ../tracks_${name}.root ./tracksOnly*_gm2tracker_ana*_{${runstart}..${runend}}*root 

rm -f ../clusters_${name}.root 
hadd -f -T ../clusters_.root ./old/clustersOnly*_gm2tracker_ana*_${runstart..runend}*root  

rm -f ../matchedTracks_${name}.root 
hadd -f -T ../matchedTracks_${name}.root ./matchedTracksSam*_${runstart..runend}*root

#9-day
runstart=16355
runend=16539
name="9day"

rm -f ../tracks_${name}.root 
hadd -f -T ../tracks_${name}.root ./tracksOnly*_gm2tracker_ana*_{${runstart}..${runend}}*root 

rm -f ../clusters_${name}.root 
hadd -f -T ../clusters_.root ./old/clustersOnly*_gm2tracker_ana*_${runstart..runend}*root  

rm -f ../matchedTracks_${name}.root 
hadd -f -T ../matchedTracks_${name}.root ./matchedTracks*_${runstart..runend}*root
cd ..
