
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

import uproot # https://indico.cern.ch/event/686641/contributions/2894906/attachments/1606247/2548596/pivarski-uproot.pdf
from awkward import JaggedArray
from root_pandas import read_root # https://github.com/scikit-hep/root_pandas

import warnings
warnings.filterwarnings('once')

# This file is meant to loop over all of the files in a given list and draw the crystal arrangements of the outliers / any other specified plots

# In[2]:


def constructUniqueID( entry ):
    uniqueID = int(str(entry.runNum).zfill(5) + str(entry.subRunNum).zfill(5) + str(entry.fill).zfill(5) +
                            str(entry.caloNum).zfill(5) + str(entry.islandEast).zfill(5)) 
    return uniqueID
def constructUniqueIDwest( entry ):
    uniqueID = int(str(entry.runNum).zfill(5) + str(entry.subRunNum).zfill(5) + str(entry.eventNum).zfill(5) +
                            str(entry.caloNum).zfill(5) + str(entry.islandWest).zfill(5)) 
    return uniqueID
def constructUniqueIDeast( entry ):
    uniqueID = int(str(entry.runNum).zfill(5) + str(entry.subRunNum).zfill(5) + str(entry.fillIndex).zfill(5) +
                            str(entry.calorimeterIndex).zfill(5) + str(entry.islandIndex).zfill(5)) 
    return uniqueID
def constructUniqueIDwave( entry ):
    uniqueID = int(str(entry.runNum).zfill(5) + str(entry.subRunNum).zfill(5) + str(entry.fillNum).zfill(5) +
                            str(entry.caloNum).zfill(5) + str(entry.islandNum).zfill(5)) 
    return uniqueID


# In[3]:


def ReturnNeighbors_4(x, y):
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if (((i, j) != (x, y)) and i < 9 and j < 6 and i > -1 and j > -1):
                yield (int(i), int(j))


# In[9]:


def toMap( crystalsInCluster ):
    xtalMapEast = []
    for i in range(54):
        if(i in crystalsInCluster):
            xtalMapEast.append(1)
        else:
            xtalMapEast.append(0)

    xtalMapEast.reverse()
    list1 = []
    list2 = []
    xtal = []
    list2xtal = []
    for crystal in range(54):
        list2.append(xtalMapEast[crystal]) 
        list2xtal.append(crystal)
        if (crystal+1) % 9 == 0: #split into 9 column blocks
            list1.append(list2)
            list2 = []
            list2xtal.reverse()
            xtal.append(list2xtal)
            list2xtal = []
    xtal.reverse()
    
    return( list1 )

def arrangeXtals( vec1 ):
    vec1.reverse()
    list1 = []
    list2 = []
    for crystal in range(54):
        list2.append(vec1[crystal]) 
        if (crystal+1) % 9 == 0: #split into 9 column blocks
            list1.append(list2)
            list2 = []
            list2xtal = []
    return(list1)

def imshowCompare(vec1, vec2, showPlot = True, printPlot = True, titleString = ''):
    vec3 = []
    for i in range(len(vec1)):
        vec3i = []
        for j in range(len(vec1[0])):
            if(vec1[i][j] > 0.1 and vec2[i][j] > 0.1):
                vec3i.append(2) #both recons include this xtal
            elif (vec1[i][j] > 0.1):
                vec3i.append(1) #only recon east includes this crystal
            elif (vec2[i][j] > 0.1):
                vec3i.append(3) #only recon west
            else:
                vec3i.append(5) #not inluded in either recon's cluster.
        vec3.append(vec3i)
        
    fig, ax = plt.subplots()

    cmap = matplotlib.colors.ListedColormap(['blue', 'xkcd:teal green', 'xkcd:forest green', 'xkcd:light grey'])
    cmap.set_over('xkcd:light grey')
    cmap.set_under('xkcd:light grey')
    
    bounds = [1, 2, 3, 4]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    cax = ax.imshow(vec3, interpolation='nearest', cmap=cmap, vmin=1,vmax=5)
    ax.set_title('Crystals Identified as Part of Cluster(s) in \n Island '+str(titleString))
    cbar = fig.colorbar(cax,
                        cmap=cmap,
                        boundaries = [0] + bounds + [5],
                        extend='both',
                        extendfrac='auto',
                        spacing='uniform',
                        ticks=[x + 0.5 for x in bounds],
                        orientation='vertical')
    cbar.ax.set_xticklabels(['Low', 'Medium', 'High'])  # horizontal colorbar
    cbar.ax.set_yticklabels(['East Only', 'Both', 'West Only'])
        
    if(printPlot):
        plt.savefig("./images/CrystalHits_"+str(titleString)+".png",bbox_inches='tight')
        
    if(showPlot):
        plt.show()
    else:
        plt.close()
    
    return(vec3)


# In[10]:


def islandPlot(uniqueIDref, saveImage = True):
    counter = 0
    
    crystalsEast = []
    for k, entry3 in enumerate(teast):
        dong = constructUniqueIDeast(entry3)
        if uniqueIDref == dong:
            crystalsEast += [x for x in entry3.crystalsEast]
                
    mapEast = toMap(crystalsEast)
    print("East: ", mapEast)
    
    crystalsWest = []
    for j, entry2 in enumerate(twest):
        dong = constructUniqueIDwest(entry2)
        if (uniqueIDref == dong):
            crystalsWest += [x for x in entry2.crystalsWest]

    mapWest = toMap(crystalsWest)
    print("West: ", mapWest)


    for i,entry in enumerate(twave):
        if( constructUniqueIDwave(entry) == uniqueIDref ):
            if counter > 3:
                break
            counter = counter + 1

            fig, axarr = plt.subplots(6,9, sharey=True, sharex=True,figsize=(15, 10))
            print("Entry #", i+1)
            plotVec = []
            for crystal in range(0,54):
                branchString = "twave.xtal"+str(crystal)
                entryVeci = []
                rootVec = eval(branchString)# t.xtal53
                length = rootVec.size()
                for ding in range(length):
                    entryVeci.append( rootVec[ding] )
                plotVec.append(entryVeci)

            plotVec.reverse()
            list1 = []
            list2 = []
            xtal = []
            list2xtal = []
            for crystal in range(54):
                list2.append(plotVec[crystal]) 
                list2xtal.append(crystal)
                if (crystal+1) % 9 == 0: #split into 9 column blocks
                    list1.append(list2)
                    list2 = []
                    list2xtal.reverse()
                    xtal.append(list2xtal)
                    list2xtal = []
            xtal.reverse()


            aboveThresholdVec = []
            for ding in range(9):
                for j in range(6):
                    if(len(list1[j][ding]) < 1):
                        axarr[j,ding].plot(list1[j][ding],color='g') 
                    elif(np.abs( np.mean((list1[j][ding])[0:6]) - np.max(list1[j][ding]) ) > 60): #global threshold = 60
                        axarr[j,ding].plot(list1[j][ding],color='r') 
                        aboveThresholdVec.append( (j, ding) )
                    else:
                        axarr[j,ding].plot(list1[j][ding],color='black') 
                    axarr[j,ding].set_title(str(xtal[j][ding]),y = 0.95)


            #grey out all of the +3x3 grid
            xtalsVec = []
            for xtal in aboveThresholdVec:
                for nxtals in ReturnNeighbors_4(xtal[1],xtal[0]):
                    axarr[nxtals[1],nxtals[0]].set_facecolor('xkcd:light grey')
                    xtalsVec.append(nxtals)
                xtalsVec.append((xtal[1],xtal[0]))

            plt.suptitle("Unpacked Islands from Calo "+str(twave.caloNum)
                         +" [run "+str(twave.runNum)+", subRun "+str(twave.subRunNum)
                         +", fill "+str(twave.fillNum)+", island "+str(twave.islandNum)+"]"
                         ,y = 0.93, fontsize=20)
            

            #now lets color them ala the plots above
            for ding in range(9):
                for j in range(6):
                    in3x3check = False
                    if((mapWest[j][ding] == 1) and (mapEast[j][ding] == 1)):
                        axarr[j,ding].set_facecolor('xkcd:teal green')
                        in3x3check = True
                    elif(mapWest[j][ding] == 1):
                        axarr[j,ding].set_facecolor('xkcd:forest green')
                        in3x3check = True
                    elif(mapEast[j][ding] == 1):
                        axarr[j,ding].set_facecolor('xkcd:cerulean')
                        in3x3check = True
                      
                    #make the borders red if this xtal is not within the 3x3 grid that would be saved
                    if( (ding,j) not in xtalsVec and in3x3check):
                        #axarr[j,ding].set_facecolor('xkcd:lilac')
                        axarr[j,ding].spines['right'].set_color('xkcd:neon purple')
                        axarr[j,ding].spines['left'].set_color('xkcd:neon purple')
                        axarr[j,ding].spines['top'].set_color('xkcd:neon purple')
                        axarr[j,ding].spines['bottom'].set_color('xkcd:neon purple')
                        axarr[j,ding].title.set_color('xkcd:neon purple')
                        axarr[j,ding].spines['right'].set_linewidth(3)
                        axarr[j,ding].spines['left'].set_linewidth(3)
                        axarr[j,ding].spines['top'].set_linewidth(3)
                        axarr[j,ding].spines['bottom'].set_linewidth(3)
                        
            #create custom lines for the legend with the same colors as above
            from matplotlib.lines import Line2D
            custom_lines = [Line2D([0], [0], color='xkcd:forest green', lw=4),
                            Line2D([0], [0], color='xkcd:teal green', lw=4),
                            Line2D([0], [0], color='xkcd:cerulean', lw=4),
                            Line2D([0], [0], color='xkcd:light grey', lw=4),
                            Line2D([0], [0], color='r', lw=4),
                            Line2D([0], [0], color='xkcd:neon purple', lw=4)]

            fig.legend(custom_lines,
                       ('Recon West Only', 'Shared', 'Recon East Only', 
                        'in 3x3 Grid', 'Above Threshold', 'In a Cluster, but\n not in 3x3 Grid'),
                       'upper right')

            if(saveImage):
                plt.savefig("./images/UnpackedIslands_CT_calo"+str(twave.caloNum).zfill(2)+"_run"+str(twave.runNum)+"_subRun"
                            +str(twave.subRunNum).zfill(5)+"_entry"+str(i)+".png",bbox_inches='tight')
            plt.show()

            break


# In[19]:

#these are the unique ids that we want to plot
uniqueIDs = [1636800128001030001700149]

#these are the files we are searching for them in
filePath  = "./data/Oct23/"
fileNamesBare = ["gm2offline_ana_12653993_16358.00045.root",
		"gm2offline_ana_12653994_16355.00098.root",
		"gm2offline_ana_12654000_16358.00108.root",
		"gm2offline_ana_12654005_16367.00137.root",
		"gm2offline_ana_12654020_16363.00374.root",
		"gm2offline_ana_12654027_16367.00093.root",
		"gm2offline_ana_12654032_16367.00251.root",
		"gm2offline_ana_12654038_16365.00367.root",
		"gm2offline_ana_12654040_16363.00479.root",
		"gm2offline_ana_12654043_16356.00252.root"]
fileNames = [filePath + x for x in fileNamesBare]
condition = "r.TMath.Abs(entry.deltaX) > 50000"

print("Identifying based on: ", uniqueIDs)

# In[20]:


#Open the current file and find any matching islands. Print them if they exist
matchingUniqueIDs = []

for fileName in fileNames:
    if(len(matchingUniqueIDs) == len(uniqueIDs)):
        print("Found all unique ID's. Exiting.")
        break

    try:
        f = r.TFile(fileName)
        twest = f.Get("farline").Get("eventTree")
        teast = f.Get("farline").Get("eastTree")
        tcomp = f.Get("farline").Get("evwTree")
        terr = f.Get("farline").Get("evwNoPartnerTree")
        tcomp2 = f.Get("farline").Get("wveTree")
        terr2 = f.Get("farline").Get("wveNoPartnerTree")
    except:
        print("ERROR: File ", fileName, "not found")
        continue
        
    print("Starting file:", fileName)
    
    dingbefore = 0


    for i, entry in enumerate(tcomp):
        ding = constructUniqueID(entry)

        if(ding not in uniqueIDs):
            continue

        counter = 0
        matchingUniqueIDs.append((i, ding))
        if (dingbefore == ding):
            continue

        print("Unique island: ", ding)

        crystalsEast = []
        for k, entry3 in enumerate(teast):
            dong = constructUniqueIDeast(entry3)
            if ding == dong:
                print("     Found an island with this unique ID.")
                crystalsEast += [x for x in entry3.crystalsEast]
                print("          ",crystalsEast)

        crystalsWest = []
        for j, entry2 in enumerate(twest):
            dong = constructUniqueIDwest(entry2)
            if (ding == dong):
                counter = counter + 1
                print("     Found Match (", i, j, counter,")")
                print("         East: ", crystalsEast)
                print("         West: ", [x for x in entry2.crystalsWest])
                crystalsWest += [x for x in entry2.crystalsWest]

        imshowCompare( toMap(crystalsEast), toMap(crystalsWest), False, True, ding)
        dingbefore = ding

print("Matching Unique ID's: ", matchingUniqueIDs)

