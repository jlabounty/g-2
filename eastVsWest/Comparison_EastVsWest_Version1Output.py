
# coding: utf-8

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

import uproot #https://indico.cern.ch/event/686641/contributions/2894906/attachments/1606247/2548596/pivarski-uproot.pdf
from awkward import JaggedArray
from root_pandas import read_root # https://github.com/scikit-hep/root_pandas


# In[2]:


f = r.TFile("./data/gm2offline_ana_version1.root")
twest = f.Get("farline").Get("eventTree")
teast = f.Get("farline").Get("eastTree")


# In[3]:


twest.Print()


# In[4]:


teast.Print()


# In[5]:


#These are magic numbers which were stolen from https://cdcvs.fnal.gov/redmine/projects/gm2reconeast/repository/revisions/develop/entry/analyses/ReconstructionComparison_module.cc
#Will need to figure out where they come from
reconEastCaloTimeCorrection = [-2.052, -2.352, -2.255, -2.244, -0.117, 0.707,  0.312,  0.064,
                                -0.542, -0.365, -0.641, -0.779,  0.158, 0.052, -0.370, -0.181,
                                -0.705, -0.945, -0.861, -0.851, -0.154, 0.000, -0.417,  0.218]
#recon east energy fudge factor
energyFudgeFactor = 1.10


# In[37]:


matchingClusterCounts = []
positionsVec = []
timesVec = []
energyVec = []
caloNumVec = []
errorVec = []

for i,entry in enumerate(teast):
    if (i % 500 == 0):
        print("Beginning entry:",i)
    if i > 1: 
        break
#    print("Beginning entry", i)
#    print("     Time, Energy:", entry.time,entry.energy)
#    print("     Positions: ", entry.position.first,entry.position.second)
#    print("     CaloNum:", entry.calorimeterIndex)
    c = r.TCanvas("c","c",1200,600)
    c.Divide(2)
    c.cd(1)
    
    timecorrection = reconEastCaloTimeCorrection[entry.calorimeterIndex - 1]
    cut = "eventNum == "+str(entry.fillIndex) +" && caloNum == "+str(entry.calorimeterIndex)+" && time < "+str(entry.time - timecorrection + 0.5 ) + " && time > " + str(entry.time - timecorrection - 0.5)
    #curring on fill number, run/subrun number (implicitly by file), and time only
    
    h = r.TH1D("h","Time Shift Between Recon East and West Clusters (After Time Correction); Time [c.t.]; Counts",
               1000,entry.time-2,entry.time+2)
    
    twest.Draw("time + "+str(timecorrection)+">>h", cut ,"goff")
    h.Draw()
#    print("    ",h.GetEntries(),"Clusters within this time range")
    if(h.GetEntries() != 1):
        print("ERROR: MORE/LESS THAN ONE MATCHING CLUSTER (", h.GetEntries()," found )")
        errorVec.append((h.GetEntries(), i, entry.calorimeterIndex))
        continue
    matchingClusterCounts.append( h.GetEntries() )
    
    eastmarker = r.TLine((entry.time),0,(entry.time),1)
    eastmarker.SetLineColor(2)
    eastmarker.Draw()
    

    leg = r.TLegend(0.1,0.8,0.3,0.9)
    leg.AddEntry(h ,"Recon West Cluster(s)", "l")
    leg.AddEntry(eastmarker ,"Recon East Cluster", "l")
    leg.Draw()
    
    c.cd(2)
    hpos = r.TH2D("hpos","Positions of Recon East vs. West Clusters; x [xtals]; y [xtals]",90,0,9,60,0,6)
    twest.Draw("y:x>>hpos",cut,"goff")    
    r.gPad.SetGridx()
    r.gPad.SetGridy()
    hpos.Draw("COLZ")
    
    poseast = r.TMarker(entry.position.first,entry.position.second,29)
    poseast.SetMarkerColor(2)
    poseast.Draw("SAME")
    
    positionsVec.append( ( entry.position.first , entry.position.second , (twest.GetV1())[0] , (twest.GetV2())[0] ) )
    
    c.Draw()
    
    twest.Draw("time:energy",cut,"goff")
    
    timesVec.append( ( entry.time , twest.GetV1()[0] ) )
    energyVec.append( ( entry.energy , twest.GetV2()[0] ) )
    caloNumVec.append( entry.calorimeterIndex )
    


# In[38]:


c.Draw()
c.Print("out_c.root")


# In[7]:


plt.hist(matchingClusterCounts)
plt.yscale("log")
plt.show()
plt.plot(matchingClusterCounts)
plt.ylim(0,5)
plt.show()


# In[25]:

if(len(errorVec) > 0):
	errorCounts, errorI, errorCalo = zip(*errorVec)

	plt.hist(errorCounts)
	plt.show()
	plt.plot(errorCounts)
	plt.show()
	plt.hist(errorCalo,bins=24)
	plt.show()


# In[9]:


vecXeast, vecYeast, vecYwest, vecXwest = zip(*positionsVec)


# In[10]:


plt.scatter(vecXeast,vecYeast,label='east')
plt.scatter(vecXwest,vecYwest,label='west')
plt.legend()
plt.show()


# In[31]:


deltaX = []
deltaY = []
for xeast, yeast, ywest, xwest in positionsVec:
    deltaX.append( xeast - xwest )
    deltaY.append( yeast - ywest )
    
plt.hist(deltaX,bins=100)
plt.title("$\Delta x$")
plt.xlabel("Crystal Widths")
plt.yscale("log")
plt.show()

plt.hist(deltaY,bins=100)
plt.title("$\Delta y$")
plt.xlabel("Crystal Widths")
plt.yscale("log")
plt.show()

'''
cmap = plt.get_cmap("viridis")
cmap.set_bad("white")
cmap.set_under("white")

plt.hist2d(deltaX,deltaY,bins=20,cmap=cmap,vmin=0.1)
plt.xlabel("$\Delta x$")
plt.ylabel("$\Delta y$")
plt.colorbar()
plt.show()
'''
c2 = r.TCanvas()
hdeltaxy = r.TH2D("hdeltaxy","$\Delta x ~vs.~ \Delta y$; $\Delta x$ [xtals]; $\Delta y$ [xtals]"
                  ,100,-10,10,50,-5,5)
for i,x in enumerate(deltaX):
    hdeltaxy.Fill(x,deltaY[i])
hdeltaxy.Draw("COLZ")
c2.SetLogz()
c2.Draw()
c2.Print("out_c2.root")


# In[29]:


deltaT = [x[0] - x[1] for x in timesVec]
plt.plot(deltaT)
plt.title("$t_{east} - t_{west}$")
plt.ylabel("Time [c.t.]")
plt.show()

plt.hist(deltaT,bins=100)
plt.xlabel("$t_{east} - t_{west}$")
plt.show()

plt.plot(caloNumVec,deltaT,'.')
plt.xlabel("Calo Number")
plt.ylabel("$t_{east} - t_{west}$")
plt.show()


# In[13]:


deltaE = [x[0] - x[1] for x in energyVec]
eeast, ewest = zip(*energyVec)
plt.hist(deltaE,bins=20)
plt.title("$E_{east} - E_{west}$")
plt.show()

plt.hist(ewest, alpha=0.5,bins=20,label='west')
plt.hist(eeast, alpha=0.5,bins=20,label='east')
plt.title("Energy Distribution in Recon East + West")
plt.yscale("log")
plt.legend()
plt.show()


# In[18]:


plt.hist(ewest, alpha=0.5,bins=20,label='west')
plt.hist([eeasti*energyFudgeFactor for eeasti in eeast], alpha=0.5,bins=20,label='east')
plt.title("Energy Distribution in Recon East + West")
plt.yscale("log")
plt.legend()
plt.show()

