#!/usr/bin/env python
# coding: utf-8

# In[30]:


import ROOT as r
import os
import sys


# In[31]:


filePath = sys.argv[1] #"./data/"
fileName =  sys.argv[2] #"gm2skim_ana_16495.root"
station =  int(sys.argv[3]) #13

outfileName = fileName.split(".root")[0]+"station_"+str(station)+"_output.root"
f = r.TFile(filePath+fileName)

f.ls()


# # Plots to make
# * All Cluster y's vs. Time
# * All Tracks y's (calo face) vs. y-s (beam) vs. time 
# * All calo-matched tracks y's (cluster) vs. y's (calo face tracker) vs. time
# 
# ---

# ### Global Parameters
# 
# ---

# In[32]:


eMin = 1100
eMax = 2400
tMin = 0
tMax = 700
tBins = 700


histsToSave = []


# ### All cluster y's vs. time
# 
# ---

# In[33]:


cutString = "energy > "+str(eMin)+" && energy < "+str(eMax)+" && time/1000.*1.25 < "+str(tMax)+" && time/1000.*1.25 > "+str(tMin)+" && caloNum == "+str(station)
print(cutString)


# In[34]:


t = f.Get("clusterTree").Get("clusters")
t.Print()


# In[35]:


h1 = r.TH2I("allClusterY_vs_Time","Cluster y [mm] vs. Time; Time [#mus]; Relative y [mm]",
           tBins, tMin, tMax,
           600,-75,75)

t.Draw("y:time*1.25/1000.>>allClusterY_vs_Time",cutString, "goff")


# In[36]:


histsToSave.append(h1)


# ---
# 
# ### All Tracks y's (calo face) vs. y-s (beam) vs. time 
# 
# ---

# In[37]:


t = f.Get("trackerNTup").Get("tracker")
t.Print()


# In[38]:


cutString = "passVertexQuality && passTrackQuality && station == "+str(station-1)


# In[39]:


h2 = r.TH3I("allTracks_yCalo_vs_yBeam_vs_Time", 'Track y vs. Extrapolated Calo y vs. Time; Time [#mus]; Track y [mm]; Calo y [mm]',
           tBins, tMin, tMax,
            400, -50, 50,
            600, -100,100
           )

t.Draw("caloVertexPosY:decayVertexPosY:decayTime/1000.>>allTracks_yCalo_vs_yBeam_vs_Time", cutString, "goff")


# In[40]:


histsToSave.append(h2)


# ---
# 
# ### All calo-matched tracks y's (cluster) vs. y's (calo face tracker) vs. time
# 
# ---

# In[41]:


t = f.Get("allmuons").Get("tree")
t.Print()


# In[42]:


cutString = "trkPassCaloVertexQuality && trkPassTrackQuality && trkPassVertexQuality " 
cutString += " && cluEne > "+str(eMin)+" && cluEne < "+str(eMax)
cutString += " && cluTime/1000. < "+str(tMax)+" && cluTime/1000. > "+str(tMin)
cutString += " && cluCaloNum == "+str(station)

print(cutString)


# In[43]:


h3 = r.TH3I("matchedTracks_yCaloTracks_vs_yCaloTracker_vs_Time", 
            'Tracker Calo y vs. Cluster Calo y vs. Time; Time [#mus]; Track y [mm]; Calo y [mm]',
            tBins, tMin, tMax,
            400, -50, 50,
            600, -100,100
           )

t.Draw("(cluY-3)*25:vY:cluTime/1000.>>matchedTracks_yCaloTracks_vs_yCaloTracker_vs_Time", cutString, "goff")


# In[44]:


histsToSave.append(h3)


# In[ ]:





# ---
# 
# ### Save histograms to root file
# 
# ---

# In[45]:


fout = r.TFile(outfileName,"RECREATE")
for hi in histsToSave:
    hi.Write()
fout.Close()


# In[46]:


f = r.TFile(outfileName)
f.ls()
