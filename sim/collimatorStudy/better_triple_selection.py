import pandas
import math
import ROOT as r
import numpy as np
import os
import matplotlib.pyplot as plt

#directories in which each of the files are stored. The file name is used to determine which momentum is which.
basepaths= [    
    "/home/labounty/sim/100points/plus/",
    "/home/labounty/sim/100points/minus/",
    "/home/labounty/sim/100points/nominal/",
    "/home/labounty/sim/100points/nominal2/",
]

for basepath in basepaths:
    
    files = os.listdir(basepath)

    tempvec = []
    efficiencies = []

    #for k, file in enumerate(paths):
    for k, file in enumerate(files):
        print("Starting files in:", basepath+str(file))

        #determine if the file is a root file and whether or not the required tree is present
        if(".root" not in file):
            print("Skipping...")
            continue
        f = r.TFile(basepath+file)
        t = f.Get("trajectoryAnalyzer/t")
        if("Tree" not in str(type(t))):
            print("ERROR: Tree not found. Skipping...")
            continue            
        
        #from the file name, get the corner + collimator this was set to
        name = file.split('.root')[0] 
        collimator = int(name.split("_col")[1].split("_")[0])
        #corner_num = int(name.split("_")[3].split(".root")[0])
        try:
            corner_num = int(name.split("_")[4].split(".root")[0])
        except:
            corner_num = int(name.split("_")[3].split(".root")[0])
        corner = [None, None]
        
        counter = 0

        tripleCondition = "@caloNum.size() >= 5"
        newTripCon = (" && "+tripleCondition+" && TMath::ATan2(caloX[0], caloZ[0]) - TMath::ATan2(caloX[1], caloZ[1]) > 0.019"
                    +" && TMath::ATan2(caloX[2], caloZ[2]) - TMath::ATan2(caloX[3], caloZ[3]) > 0.019"
                    +" && TMath::ATan2(caloX[4], caloZ[4]) - TMath::ATan2(caloX[5], caloZ[5]) > 0.019"
                    )
        
        #hack to remove some bad files (wrong fcl file used)
        if("inus" in basepath):
            n1 = t.Draw("caloNum[0]","@collNum.size() > 0 && collE[0] < 3093 ")
            n2 = t.Draw("caloNum[0]","@caloNum.size() >= 5 && @collNum.size() > 0 && collE[0] < 3093"+newTripCon)
        elif("lus" in basepath):
            n1 = t.Draw("caloNum[0]","@collNum.size() > 0 && collE[0] > 3098")
            n2 = t.Draw("caloNum[0]","@caloNum.size() >= 5 && @collNum.size() > 0 && collE[0] > 3098"+newTripCon)
        else:
            n1 = t.Draw("caloNum[0]","@collNum.size() > 0")
            n2 = t.Draw("caloNum[0]","@caloNum.size() >= 5 && @collNum.size() > 0"+newTripCon)

        #only loop over the tree if there is something interesting
        if(n1 < 1):
            print("ERROR: No collimator hits in this file")
            continue
        
        efficiency = (n2*1.0/n1)
        efficiencies.append(efficiency)

        
        for i,e in enumerate(t):
            #if(counter > 1000):
            #    break

            if(e.caloNum.size() < 5 or e.collNum.size() < 1 or (e.collNum[0] != collimator)):
                continue
            counter += 1
            #print([x for x in e.caloNum])
            drifttime = e.caloT[0] - e.collT[0]

            calosize=e.caloNum.size()
            collimatorEnergyLoss = e.collE[0] - e.collE[1]
            caloEnergyLoss = e.caloE[0] - e.caloE[1]
            
            tempvec.append([ k, name, collimator, corner[0], corner[1], e.collNum[0], 
                            e.caloNum[0], e.caloNum[2], e.caloNum[4], e.caloNum,
                            math.sqrt(e.collX[0]**2 + e.collZ[0]**2), 
                            e.collY[0], 
                            math.sqrt(e.caloX[0]**2 + e.caloZ[0]**2), math.sqrt(e.caloX[2]**2 + e.caloZ[2]**2), 
                            math.sqrt(e.caloX[4]**2 + e.caloZ[4]**2),# [math.sqrt(x**2 + z**2) for (x,z) in zip(e.caloX, e.caloZ)],
                            e.caloY[0], e.caloY[2], e.caloY[4], e.caloY, 
                            n2, efficiency, drifttime, corner_num, 
                            calosize, collimatorEnergyLoss, caloEnergyLoss,
                            e.collE[0], e.caloE[0] ])
        
        print("Good Triples:", counter)
        print("Good Collimator Hits:", n1)
        print("   -> Efficiency:", efficiency)
        print("*******************************************************************")


        #write the data + histograms to an output file
        df = pandas.DataFrame(tempvec, columns=['filenum','name','collimator_set', 'in-out', 'top-bot', 'coll', 
                                                'calo', 'calo2', 'calo3', 'allcalos',
                                                'collR', 
                                                'collY', 
                                                'caloR', 'calo2R', 
                                                'calo3R', #'allcaloR', 
                                                'caloY', 'calo2Y', 'calo3Y', 'allcaloY',
                                                'goodtriples', 'efficiency', 'drifttime', 'corner_num', 
                                                'ncaloentries', 'collimatorEnergyLoss', 'caloEnergyLoss',
                                                'initialCollimatorEnergy', 'initialCaloEnergy'])
        df.head()

        df.to_csv(basepath+"python_output_may20.csv")


    print("Finished path", basepath)


print("All done!")


