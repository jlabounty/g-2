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

#fileNamesPartial = ["results_full_partial_v9_11_Nov14.root"]
#fileNames = ["./data/dataExternal/Nov14_v11_60hr_PartialSet_WrongTimeConstants/" + x for x in fileNamesPartial]

#uncomment this to just loop over the local file for which we also have the island data
fileNames = ["./data/gm2offline_ana_16536938_15925.00356.root"]


# In[4]:


#this will be the cut that will determine whether or not something is printed. Written in root format, not pyroot.
#condition = "((TMath::Abs(deltaX)**2)/(3**2) + (TMath::Abs(deltaY)**2)/(2**2)) > 1 && timeEast > 100*1000/1.25" 
#condition = "TMath::Abs(deltaE) > 1700 && timeEast > 100*1000/1.25" 
#condition = "TMath::Abs(deltaT - timeCorr) > 3 && timeEast > 100*1000/1.25" 
#condition = "TMath::Sqrt(TMath::Abs(deltaX)**2 + TMath::Abs(deltaY)**2) < 0.25 && TMath::Abs(deltaE) < 250 && energyWest > 1500 && TMath::Abs(deltaT-timeCorr) < 2 && timeEast > 100*1000/1.25" 
#condition = "TMath::Abs(deltaE) < 500 && TMath::Abs(KS) > 0.95 && energyWest > 1000 && timeEast > 100*1000/1.25" 
#condition = "condition = "energyEast > 1500 && energyEast < 2500 && energyWest > 3200 && energyWest < 5000"
#condition = "deltaX > 4.5 && delta Y > 2.25 && deltaX < 5.5 && deltaY < 3.75"
#condition = "deltaX > 2 && delta Y > -3 && deltaX < 4 && deltaY < -1 && TMath::Abs(deltaT - timeCorr) > 3"
#condition = "energyWest > 2700 && energyWest < 3500 && energyEast > 1500 && energyEast < 2100"
condition = "energyWest > 700 && energyEast < 210"

print("Cutting on:", condition)
#name of the output file. Should reflect the cut, and the intputs.
outFileName = "./data/TestEvents_Ewest_gt_700_Eeast_lt_200_60hUnblinding.root"


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
