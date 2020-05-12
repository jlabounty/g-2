import pandas
import math
import ROOT as r
import numpy as np
import os
import matplotlib.pyplot as plt

'''basepath="/data/g2/users/labounty/gm2ringsim/"

paths = [
	1589041125,
	1589041122,
	1589041120,
	1589041118,
	1589041116,
	1589041114,
	1589041112,
	1589041109
]'''

basepath="/home/labounty/sim/100points/"
files = os.listdir(basepath)

tempvec = []
efficiencies = []

hithist = r.TH2I("hithist","Collimator + Calo Hits in the Ring; z [mm]; x [mm]", 
                 700, -8000,8000, 700, -8000, 8000 )
hithist.SetDirectory(0)

nHits_vs_FirstCalo = r.TH3I("nhitsvscalo", "Number of Calo Entries vs. First Calo Hit vs. Collimator; N calo hits; First Calo Number; First Coll Number",
                            20,0,20,
                            26,0,26,
                            10,0,10)
nHits_vs_FirstCalo.SetDirectory(0)

drifttimehist = r.TH2I("drifttime", "Drift Time vs. First Calo Hit; calo number; drift time [ns]", 
                    26,0,26,
                    10000,0,1000)
drifttimehist.SetDirectory(0)

ypos_vs_corner = r.TH3I("yposvscorner", "y-Position of Calo Hit vs. Corner of Collimator; y_calo [mm]; corner num; calo entry num",
                        100,-100,100,
                        100,0,100,
                        20,0,20)

rpos_vs_corner = r.TH3I("rposvscorner", "R-Position of Calo Hit vs. Corner of Collimator; R_calo [mm]; corner num; calo entry num",
                        400, 6800, 7200,
                        100,0,100,
                        20,0,20)

deltat = r.TH2I("deltat", "Time difference of first and second hit; delta t [ns]; calo num",
                1000,0,10,
                26,0,26)


histsToSave = [hithist, nHits_vs_FirstCalo, drifttimehist, ypos_vs_corner, deltat, rpos_vs_corner]

doTree = True
if(doTree):
    #for k, file in enumerate(paths):
    for k, file in enumerate(files):
        print("Starting files in:", basepath+str(file))
        if(".root" not in file):
            print("Skipping...")
            continue

        f = r.TFile(basepath+file)
        t = f.Get("trajectoryAnalyzer/t")

        #t = r.TChain("trajectoryAnalyzer/t")
        #t.Add(basepath+str(file)+"/*root")
        
        
        name = file.split('.root')[0] 

        #allfiles = os.listdir(basepath+str(file))
        #print(allfiles)

        '''
        for ding in allfiles:
            if("root" in ding):
                name = ding.split("col")[1].split('.root')[0] 
                break
        
        collimator = int(name.split("_")[0])
        corner = name.split("_")[1:]
        corner_num = 0
        if("inner" in name):
            corner_num += 10
        if("bottom" in name):
            corner_num += 1
        if(collimator == 8):
            corner_num += 5
        print(collimator, corner)
        '''

        collimator = int(name.split("_col")[1].split("_")[0])
        corner_num = int(name.split("_")[3].split(".root")[0])
        corner = [None, None]
        
        counter = 0
        
        n1 = t.Draw("caloNum[0]","@collNum.size() > 0")
        n2 = t.Draw("caloNum[0]","@caloNum.size() >= 5 && @collNum.size() > 0")
        
        efficiency = (n2*1.0/n1)
        efficiencies.append(efficiency)
        
        for i,e in enumerate(t):
            #if(counter > 1000):
            #    break
            if( e.caloNum.size() > 0 and e.collNum.size() > 0 ):
                nHits_vs_FirstCalo.Fill(e.caloNum.size(), e.caloNum[0]+1, e.collNum[0])
            if(e.caloNum.size() < 5 or e.collNum.size() < 1 or (e.collNum[0] != collimator)):
                continue
            counter += 1
            #print([x for x in e.caloNum])
            drifttime = e.caloT[0] - e.collT[0]
            drifttimehist.Fill(e.caloNum[0]+1, drifttime)
            calosize=e.caloNum.size()

            deltat.Fill( e.caloT[2] - e.caloT[0] , e.caloNum[0])

            for ii, (x,z) in enumerate(zip(e.caloX, e.caloZ)):
                hithist.Fill(z, x)
                ypos_vs_corner.Fill(math.sqrt(x**2 + z**2), corner_num, ii)
            hithist.Fill(e.collZ[0], e.collX[0])
            for ii, y in enumerate(e.caloY):
                ypos_vs_corner.Fill(y, corner_num, ii)
            
            tempvec.append([ k, name, collimator, corner[0], corner[1], e.collNum[0] ,e.caloNum[0], math.sqrt(e.collX[0]**2 + e.collZ[0]**2), 
                            e.collY[0], math.sqrt(e.caloX[0]**2 + e.caloZ[0]**2), e.caloY[0], n2, efficiency, drifttime, corner_num, calosize ])
        
        print("Good Triples:", counter)
        print("Good Collimator Hits: ", n1)
        print("*******************************************************************")

    df = pandas.DataFrame(tempvec, columns=['filenum','name','collimator_set', 'in-out', 'top-bot', 'coll', 'calo', 'collR', 'collY', 'caloR', 
                                        'caloY', 'goodtriples', 'efficiency', 'drifttime', 'corner_num', 'ncaloentries'])
    df.head()

    df.to_csv("./python_output_may12.csv")

    
    outfile = "./histograms_collimator_may12.root"
    print("Writing histograms to", outfile)
    fout = r.TFile(outfile,"recreate")
    for h in histsToSave:
        h.Write()
    fout.Write()
    fout.Close()

else:
    print("Reading histogram from file")
    df_full = pandas.read_csv("./python_output_may12.csv")
    df = df_full.sample(10000)



print("Now making plots")


''' ***************************************************************************** '''

fig,ax = plt.subplots(1,3,figsize=(15,5), sharey=False)

axi = ax[0]
axi.plot(df['coll'], df['efficiency'],"o")
axi.set_title("Efficiency vs. Collimator")

axi = ax[1]
scatter = axi.scatter(df['corner_num'], df['efficiency'], c = df['coll'])
axi.set_xticks( [0,1,5,6,10,11,15,16] )
axi.set_xticklabels( ['col 6 outer top', 'col 6 outer bottom','col 8 outer top', 'col 8 outer bottom',
                      'col 6 inner top', 'col 6 inner bottom','col 8 inner top', 'col 8inner bottom'  ], 
                      rotation=90 
                    )
axi.set_title("Efficiency vs. Inner/Outer")

legend1 = axi.legend(*scatter.legend_elements(),
                    #loc="lower left", 
                    title="Collimator", 
                    ncol=2)
axi.add_artist(legend1)


axi = ax[2]
axi.scatter(df['top-bot'], df['efficiency'], c = df['coll'])
axi.set_title("Efficiency vs. Top/Bottom")

for axi in ax:
    axi.grid()
    
plt.tight_layout()
plt.savefig("./Efficiency_vs_Corners.png", bbox_inches="tight")
#plt.show()
plt.close()


plotnum = 1

print("Finished plot", plotnum); plotnum+=1
''' ***************************************************************************** '''

fig,ax = plt.subplots(figsize=(15,5))

if(True):
    splitcalo = 15
    dfi = df.loc[df['calo'] >= splitcalo]
    plt.scatter(dfi['calo']+1-24, dfi['drifttime'], c=dfi['coll'])
    plt.scatter(df['calo']+1+24, df['drifttime'], c=df['coll'])
    
    plt.xticks([x for x in range(splitcalo-24, 500,2)], labels=[x%24 for x in range(splitcalo-24, 500,2)],
              rotation=90)
scatter = plt.scatter((df['calo']+1), df['drifttime'],c=df['coll'])
plt.colorbar()
plt.yscale("log")
plt.title("Drift Time vs. Calo Number")
plt.ylabel("Drift Time [c.t. or ns?]")
plt.xlabel("Calo Number of First Hit in Triple")
plt.grid()

legend1 = ax.legend(*scatter.legend_elements(),
                    #loc="lower left", 
                    title="Collimator", 
                    ncol=2)
ax.add_artist(legend1)

'''handles, labels = scatter.legend_elements(prop="sizes", alpha=0.6)
legend2 = ax.legend(handles, labels, title="Efficiency", loc=4)'''

plt.xlim(-10,50)
plt.tight_layout()
plt.savefig("./DriftTime_vs_Collimator.png", bbox_inches="tight")
#plt.show()
plt.close()



print("Finished plot", plotnum); plotnum+=1
''' ***************************************************************************** '''



fig, ax = plt.subplots(figsize=(15,5))
for coll in [6,8]:
    dfi = df.loc[df['coll'] == coll]
    if coll == 6:
        offset = 0
    else:
        offset = 0
    plt.hist(((dfi['calo']+1+offset)%24)+1, range=(0,26), bins=26 ,
             label="collimator "+str(coll)+" [shifted right by "+str(offset)+"]", alpha=0.3, weights=1./dfi['goodtriples'])
plt.legend()
plt.title("calo of first triple hit")
plt.yscale("log")
plt.grid()
plt.savefig("ntriples_vs_calo_by_collimator.png", bbox_inches="tight")
plt.close()
#plt.show()

print("Finished plot", plotnum); plotnum+=1
''' ***************************************************************************** '''



fig, ax = plt.subplots(figsize=(15,5))
for coll in [6,8]:
    dfi = df.loc[df['coll'] == coll]
    if coll == 6:
        offset = 4
    else:
        offset = 0
    plt.hist(((dfi['calo']+1+offset)%24)+1, range=(0,26), bins=26 ,
             label="collimator "+str(coll)+" [shifted right by "+str(offset)+"]", alpha=0.3, weights=1./dfi['goodtriples'])
plt.legend()
plt.title("calo of first triple hit")
plt.yscale("log")
plt.grid()
plt.savefig("ntriples_vs_calo_by_collimator_offset.png", bbox_inches="tight")
plt.close()
#plt.show()

print("Finished plot", plotnum); plotnum+=1






print("All done!")


