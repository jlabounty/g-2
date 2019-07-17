
# coding: utf-8

# This file will take a set of input files as strings and then loop over them to create an output file containing only the events which have passed the cut

# In[1]:


#General imports.
import ROOT as r
import math
from BlindersPy3 import Blinders
from BlindersPy3 import FitType
r.gStyle.SetOptStat(0)
r.gStyle.SetOptFit(1111)
import matplotlib.pyplot as plt
import csv
import pandas

import seaborn as sns
sns.set(style="ticks", color_codes=True)
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
matplotlib.rc('xtick', labelsize=20) 
matplotlib.rc('ytick', labelsize=20) 
import os
import scipy

import uproot # https://indico.cern.ch/event/686641/contributions/2894906/attachments/1606247/2548596/pivarski-uproot.pdf
from awkward import JaggedArray
from root_pandas import read_root # https://github.com/scikit-hep/root_pandas

import warnings
warnings.filterwarnings('once')


from evwTools import *


# In[3]:


#Names of the files to loop over

'''
fileNamesPartial = ["gm2offline_ana_12769487_15932.00176.root",
                    "gm2offline_ana_12769488_15929.00040.root",
                    "gm2offline_ana_12769489_15928.00148.root",
                    "gm2offline_ana_12769490_15926.00236.root",
                    "gm2offline_ana_12769491_15925.00138.root",
                    "gm2offline_ana_12769502_15932.00136.root",
                    "gm2offline_ana_12769503_15925.00302.root",
                    "gm2offline_ana_12769504_15932.00404.root",
                    "gm2offline_ana_12769505_15924.00114.root",
                    "gm2offline_ana_12769506_15926.00463.root",
                    "gm2offline_ana_12769517_15925.00347.root",
                    "gm2offline_ana_12769518_15925.00416.root",
                    "gm2offline_ana_12769519_15923.00286.root",
                    "gm2offline_ana_12769520_15929.00068.root",
                    "gm2offline_ana_12769521_15927.00098.root",
                    "gm2offline_ana_12769532_15926.00341.root",
                    "gm2offline_ana_12769533_15930.00326.root",
                    "gm2offline_ana_12769534_15932.00270.root",
                    "gm2offline_ana_12769535_15926.00098.root",
                    "gm2offline_ana_12769536_15922.00104.root",
                    "gm2offline_ana_12769547_15927.00076.root",
                    "gm2offline_ana_12769548_15931.00241.root",
                    "gm2offline_ana_12769549_15926.00137.root",
                    "gm2offline_ana_12769550_15926.00289.root",
                    "gm2offline_ana_12769551_15925.00292.root",
                    "gm2offline_ana_12769563_15933.00156.root",
                    "gm2offline_ana_12769564_15921.00059.root",
                    "gm2offline_ana_12769565_15930.00026.root",
                    "gm2offline_ana_12769567_15928.00147.root",
                    "gm2offline_ana_12769568_15926.00188.root",
                    "gm2offline_ana_12769579_15932.00352.root",
                    "gm2offline_ana_12769580_15922.00429.root",
                    "gm2offline_ana_12769581_15933.00346.root",
                    "gm2offline_ana_12769582_15930.00193.root",
                    "gm2offline_ana_12769583_15929.00109.root",
                    "gm2offline_ana_12769594_15925.00436.root",
                    "gm2offline_ana_12769595_15926.00212.root",
                    "gm2offline_ana_12769596_15926.00271.root",
                    "gm2offline_ana_12769597_15925.00479.root",
                    "gm2offline_ana_12769598_15931.00313.root",
                    "gm2offline_ana_12769610_15922.00054.root",
                    "gm2offline_ana_12769611_15922.00291.root",
                    "gm2offline_ana_12769612_15922.00098.root",
                    "gm2offline_ana_12769613_15921.00360.root",
                    "gm2offline_ana_12769614_15922.00021.root",
                    "gm2offline_ana_12769627_15926.00409.root",
                    "gm2offline_ana_12769628_15932.00428.root",
                    "gm2offline_ana_12769629_15926.00443.root",
                    "gm2offline_ana_12769630_15926.00345.root",
                    "gm2offline_ana_12769631_15924.00247.root",
                    "gm2offline_ana_12769642_15931.00001.root",
                    "gm2offline_ana_12769643_15922.00156.root",
                    "gm2offline_ana_12769644_15927.00012.root",
                    "gm2offline_ana_12769645_15925.00478.root",
                    "gm2offline_ana_12769646_15927.00436.root",
                    "gm2offline_ana_12769657_15928.00123.root",
                    "gm2offline_ana_12769658_15924.00077.root",
                    "gm2offline_ana_12769659_15933.00299.root",
                    "gm2offline_ana_12769660_15929.00372.root",
                    "gm2offline_ana_12769661_15925.00189.root",
                    "gm2offline_ana_12769672_15928.00105.root",
                    "gm2offline_ana_12769673_15930.00328.root"]

#and their paths.
fileNames = ["./data/dataExternal/Oct29_v10_DataSet/" + x for x in fileNamesPartial]
'''

fileNamesPartial = ["results_full_partial_v9_11_Nov14.root"]
fileNames = ["./data/dataExternal/Nov14_v11_60hr_PartialSet_WrongTimeConstants/" + x for x in fileNamesPartial]

#uncomment this to just loop over the local file for which we also have the island data
#fileNames = ["./data/gm2offline_ana.root"]


# In[4]:


#this will be the cut that will determine whether or not something is printed. Written in root format, not pyroot.
#condition = "((TMath::Abs(deltaX)**2)/(3**2) + (TMath::Abs(deltaY)**2)/(2**2)) > 1 && timeEast > 100*1000/1.25" 
#condition = "TMath::Abs(deltaE) > 1700 && timeEast > 100*1000/1.25" 
condition = "TMath::Abs(deltaT - timeCorr) > 3 && timeEast > 100*1000/1.25" 
#condition = "TMath::Sqrt(TMath::Abs(deltaX)**2 + TMath::Abs(deltaY)**2) < 0.25 && TMath::Abs(deltaE) < 250 && energyWest > 1500 && TMath::Abs(deltaT-timeCorr) < 2 && timeEast > 100*1000/1.25" 
#condition = "TMath::Abs(deltaE) < 500 && TMath::Abs(KS) > 0.95 && energyWest > 1000 && timeEast > 100*1000/1.25" 
#condition = "condition = "energyEast > 1500 && energyEast < 2500 && energyWest > 3200 && energyWest < 5000"
#condition = "deltaX > 4.5 && delta Y > 2.25 && deltaX < 5.5 && deltaY < 3.75"
#condition = "deltaX > 2 && delta Y > -3 && deltaX < 4 && deltaY < -1 && TMath::Abs(deltaT - timeCorr) > 3"
#condition = "energyWest > 2700 && energyWest < 3500 && energyEast > 1500 && energyEast < 2100"

print("Cutting on:", condition)
#name of the output file. Should reflect the cut, and the intputs.
outFileName = "./data/dataExternal/TestEvents_deltaT_abs_gt_3_Nov14_v9_11.root"


# In[ ]:

nEventsMatching = 0
cutoffPoint = 3000000

for i, file in enumerate(fileNames):
    print("Starting file",i+1,"/",len(fileNames),":", file)
    #if i > 2:
    #    break

    #open up the input file
    try:
        f = r.TFile(file,"read")
    except:
        print("ERROR: File not found", file)
        continue

    tcomp = f.Get("farline").Get("evwTree")

    if(i == 0):
        #create file
        fout = r.TFile(outFileName,"recreate")
        #create a tree to store the output, and fill it based on the condition.
        tfinal = tcomp.CopyTree( condition )
        nEventsMatchingi = tfinal.GetEntries()
        nEventsMatching += nEventsMatchingi
        #write the tree to the file
        tfinal.Write()
    else:
        #open existing file so that we can append to it
        fout = r.TFile(outFileName,"update")
        
        #get the final tree
        tbefore = fout.Get("evwTree")
        tbefore.SetName("tbefore")
        #create a temporary tree to store the output
        ti = tcomp.CopyTree( condition )
        nEventsMatchingi = ti.GetEntries()
        nEventsMatching += nEventsMatchingi
        #add the temp tree to tfinal using TList
        listoftrees = r.TList()
        listoftrees.Add(tbefore)
        listoftrees.Add(ti)
        
        tfinal = r.TTree.MergeTrees(listoftrees)
        tfinal.SetName("evwTree")
        
        #write the output
        tfinal.Write("evwTree",r.TObject.kWriteDelete)

        #tbefore.Delete()
        #ti.Delete()

    print("     Found", nEventsMatchingi, "clusters")

    fout.Write()
    fout.Close()

    if(nEventsMatching > cutoffPoint):
        print("Exceeded maximum number of clusters. Stopping here.")
        break

print("Found", nEventsMatching, "clusters")
print("All done. Output file: ", outFileName)
