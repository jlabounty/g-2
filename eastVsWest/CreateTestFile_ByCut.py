
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

fileNamesPartial = ["gm2offline_ana_12653990_16369.00449.root",
            "gm2offline_ana_12653991_16369.00045.root",
            "gm2offline_ana_12653992_16367.00444.root",
            "gm2offline_ana_12653993_16358.00045.root",
            "gm2offline_ana_12653994_16355.00098.root",
            "gm2offline_ana_12653995_16369.00495.root",
            "gm2offline_ana_12653996_16369.00129.root",
            "gm2offline_ana_12653997_16356.00472.root",
            "gm2offline_ana_12653998_16370.00100.root",
            "gm2offline_ana_12653999_16368.00142.root",
            "gm2offline_ana_12654000_16358.00108.root",
            "gm2offline_ana_12654001_16362.00028.root",
            "gm2offline_ana_12654002_16370.00193.root",
            "gm2offline_ana_12654003_16364.00096.root",
            "gm2offline_ana_12654004_16367.00414.root",
            "gm2offline_ana_12654005_16367.00137.root",
            "gm2offline_ana_12654006_16357.00150.root",
            "gm2offline_ana_12654007_16357.00046.root",
            "gm2offline_ana_12654008_16370.00438.root",
            "gm2offline_ana_12654009_16364.00339.root",
            "gm2offline_ana_12654010_16358.00008.root",
            "gm2offline_ana_12654011_16368.00282.root",
            "gm2offline_ana_12654012_16363.00212.root",
            "gm2offline_ana_12654013_16369.00099.root",
            "gm2offline_ana_12654014_16367.00496.root",
            "gm2offline_ana_12654015_16362.00160.root",
            "gm2offline_ana_12654016_16363.00311.root",
            "gm2offline_ana_12654017_16368.00107.root",
            "gm2offline_ana_12654018_16356.00104.root",
            "gm2offline_ana_12654019_16370.00040.root",
            "gm2offline_ana_12654020_16363.00374.root",
            "gm2offline_ana_12654021_16370.00393.root",
            "gm2offline_ana_12654022_16359.00111.root",
            "gm2offline_ana_12654023_16369.00492.root",
            "gm2offline_ana_12654024_16359.00065.root",
            "gm2offline_ana_12654025_16358.00375.root",
            "gm2offline_ana_12654026_16363.00094.root",
            "gm2offline_ana_12654027_16367.00093.root",
            "gm2offline_ana_12654028_16370.00218.root",
            "gm2offline_ana_12654029_16368.00396.root",
            "gm2offline_ana_12654030_16365.00141.root",
            "gm2offline_ana_12654031_16356.00210.root",
            "gm2offline_ana_12654032_16367.00251.root",
            "gm2offline_ana_12654034_16364.00077.root",
            "gm2offline_ana_12654035_16363.00257.root",
            "gm2offline_ana_12654036_16367.00005.root",
            "gm2offline_ana_12654037_16367.00128.root",
            "gm2offline_ana_12654038_16365.00367.root",
            "gm2offline_ana_12654039_16358.00025.root",
            "gm2offline_ana_12654040_16363.00479.root",
            "gm2offline_ana_12654041_16369.00155.root",
            "gm2offline_ana_12654042_16368.00421.root",
            "gm2offline_ana_12654043_16356.00252.root",
            "gm2offline_ana_12654044_16358.00237.root",
            "gm2offline_ana_12654045_16355.00136.root",
            "gm2offline_ana_12654046_16358.00053.root"]

#and their paths.
fileNames = ["./data/dataExternal/Oct23DataSet/" + x for x in fileNamesPartial]

#uncomment this to just loop over the local file for which we also have the island data
#fileNames = ["./data/gm2offline_ana.root"]


# In[4]:


#this will be the cut that will determine whether or not something is printed. Written in root format, not pyroot.
condition = "TMath::Sqrt(TMath::Abs(deltaX)**2 + TMath::Abs(deltaY)**2) > 6 && timeEast > 30*1000/1.25" 

#name of the output file. Should reflect the cut, and the intputs.
outFileName = "./data/dataExternal/TestEvents_deltaR_gt_5_timeCut_30_Oct23.root"


# In[ ]:

nEventsMatching = 0

for i, file in enumerate(fileNames):
    print("Starting file",i,":", file)
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
        nEventsMatching += tfinal.GetEvents()
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
        nEventsMatching += ti.GetEvents()
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


    fout.Write()
    fout.Close()

print("Found", mEventsMatching, "clusters")
print("All done. Output file: ", outFileName)
