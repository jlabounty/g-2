cp CMakeLists_beam.txt ./beamTemplatesByCalo/CMakeLists.txt 
cp CMakeLists_standard.txt ./standardLaserTemplatesByCalo/CMakeLists.txt 
cp CMakeLists_crossed.txt ./crossedLaserTemplatesByCalo/CMakeLists.txt 

rm -f outputTemplates.tar.gz
tar -zcvf outputTemplates.tar.gz ./*ByCalo* 
