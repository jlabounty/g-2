#general imports
import ROOT as r
import math
from BlindersPy3 import Blinders
from BlindersPy3 import FitType
r.gStyle.SetOptStat(0)
r.gStyle.SetOptFit(1111)
import matplotlib.pyplot as plt
plt.rcParams['figure.facecolor'] = 'white'
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
from PIL import Image


import uproot # https://indico.cern.ch/event/686641/contributions/2894906/attachments/1606247/2548596/pivarski-uproot.pdf
from awkward import JaggedArray
from root_pandas import read_root # https://github.com/scikit-hep/root_pandas



#construct unique ID's given an entry in a root tree. Slightly different variable names mean we need a few different versions.
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
def constructUniqueIDnon( entry ):
    uniqueID = int(str(entry.runNum).zfill(5) + str(entry.subRunNum).zfill(5) + str(entry.fill).zfill(5) +
                            str(entry.caloNum).zfill(5) + str(entry.island).zfill(5)) 
    return uniqueID



#conversly, we also sometimes need to construct the conditions necessary to isolate an island given a uniqueID
def constructConditionFromUniqueIDWest( uniqueID ):
    uniqueID = str(uniqueID)
    condition = (" runNum == "+str(int(uniqueID[0:5]))+
                 " && subRunNum == "+str(int(uniqueID[5:10]))+
                 " && eventNum == "+str(int(uniqueID[10:15]))+
                 " && caloNum == "+str(int(uniqueID[15:20]))+
                 " && islandWest == "+str(int(uniqueID[20:25]))
                )
    
    return condition

def constructConditionFromUniqueIDWave( uniqueID ):
    uniqueID = str(uniqueID)
    condition = (" runNum == "+str(int(uniqueID[0:5]))+
                 " && subRunNum == "+str(int(uniqueID[5:10]))+
                 " && fillNum == "+str(int(uniqueID[10:15]))+
                 " && caloNum == "+str(int(uniqueID[15:20]))+
                 " && islandNum == "+str(int(uniqueID[20:25]))
                )
    
    return condition

def constructConditionFromUniqueIDEast( uniqueID ):
    uniqueID = str(uniqueID)
    condition = (" runNum == "+str(int(uniqueID[0:5]))+
                 " && subRunNum == "+str(int(uniqueID[5:10]))+
                 " && fillIndex == "+str(int(uniqueID[10:15]))+
                 " && calorimeterIndex == "+str(int(uniqueID[15:20]))+
                 " && islandIndex == "+str(int(uniqueID[20:25]))
                )
    
    return condition

def constructConditionFromUniqueIDComp( uniqueID ):
    uniqueID = str(uniqueID)
    condition = (" runNum == "+str(int(uniqueID[0:5]))+
                 " && subRunNum == "+str(int(uniqueID[5:10]))+
                 " && fill == "+str(int(uniqueID[10:15]))+
                 " && caloNum == "+str(int(uniqueID[15:20]))+
                 " && islandWest == "+str(int(uniqueID[20:25]))
                )
    
    return condition

#returns the neighboring crystals in a grid in the form of an iterator
def ReturnNeighbors_4(x, y):
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if (((i, j) != (x, y)) and i < 9 and j < 6 and i > -1 and j > -1):
                yield (int(i), int(j))
			

#turns a vector of length 54, with xtals going from 0 -> 53 into a proper caloMap compatable with imshow()
import copy
def arrangeXtals( input ):
    vec1 = input.copy() #prevents us from changing original
    vec1.reverse() #imshow starts in upper left corner, so need to reverse the ordering of the xtals.
    list1 = []
    list2 = []
    for crystal in range(54):
        list2.append(vec1[crystal]) 
        if (crystal+1) % 9 == 0: #split into 9 column blocks
            list1.append(list2)
            list2 = []
            list2xtal = []
    return(list1)


#turns a list of crystals in a cluster into a proper map			
def toMap( crystalsInCluster ):
    xtalMapEast = []
    for i in range(54):
        if(i in crystalsInCluster):
            xtalMapEast.append(1)
        else:
            xtalMapEast.append(0)

    list1 = arrangeXtals( xtalMapEast )
    return( list1 )


def toFlatMap( crystalsInCluster ):
    xtalMapEast = []
    for i in range(54):
        if(i in crystalsInCluster):
            xtalMapEast.append(1)
        else:
            xtalMapEast.append(0)

    return( xtalMapEast )


#takes two maps and overlays them with imshow
def imshowCompare(vec1, vec2, showPlot = True, savePlot = True, titleString = ''):
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
        
    if(savePlot):
        plt.savefig("./images/CrystalHits_"+str(titleString)+".png",bbox_inches='tight')
        
    if(showPlot):
        plt.show()
    else:
        plt.close()
    
    return(vec3)

#similar to the function above, but also plots the unpacked island data alongside the 
def islandPlot(uniqueIDref, teast, twest, twave, saveImage = True, globalThreshold = None):
    if(globalThreshold == None):
        globalThreshold = 60 #default value 60
    counter = 0
    
    fout = r.TFile("temp_tree_storage.root","recreate")
    teast_partial = teast.CopyTree( constructConditionFromUniqueIDEast(uniqueIDref) )
    
    crystalsEast = []
    for k, entry3 in enumerate(teast_partial):
        dong = constructUniqueIDeast(entry3)
        if uniqueIDref == dong:
            crystalsEast += [x for x in entry3.crystalsEast]
                
    mapEast = toMap(crystalsEast)
    #print("East: ", mapEast)
    
    crystalsWest = []
    
    twest_partial = twest.CopyTree( constructConditionFromUniqueIDWest(uniqueIDref) )
    for j, entry2 in enumerate(twest_partial):
        dong = constructUniqueIDwest(entry2)
        if (uniqueIDref == dong):
            crystalsWest += [x for x in entry2.crystalsWest]

    mapWest = toMap(crystalsWest)
    #print("West: ", mapWest)


    twave_partial = twave.CopyTree( constructConditionFromUniqueIDWave(uniqueIDref) )
    for i,entry in enumerate(twave_partial):
        if( constructUniqueIDwave(entry) == uniqueIDref ):
            if counter > 3:
                break
            counter = counter + 1

            fig, axarr = plt.subplots(6,9, sharey=True, sharex=True,figsize=(15, 10))
            #print("Entry #", i+1)
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
                    elif(np.abs( np.mean((list1[j][ding])[0:6]) - np.max(list1[j][ding]) ) > globalThreshold): #global threshold = 60
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
                plt.savefig("./images/UnpackedIslands_calo"+str(twave.caloNum).zfill(2)+"_run"+str(twave.runNum)+"_subRun"
                            +str(twave.subRunNum).zfill(5)+"_uniqueID_"+str(uniqueIDref)+".png",bbox_inches='tight')
            plt.show()

            break
			
#similar to the function above, but also plots the unpacked island data alongside the 
def islandPlotCompOnly(uniqueIDref, tcomp, twave, saveImage = True, globalThreshold = None):
    if(globalThreshold == None):
        globalThreshold = 60 #default value 60
    counter = 0
    
    fout = r.TFile("temp_tree_storage.root","recreate")
    teast_partial = tcomp.CopyTree( constructConditionFromUniqueIDComp(uniqueIDref) )
    
    crystalsEast = []
    for k, entry3 in enumerate(teast_partial):
        dong = constructUniqueID(entry3)
        if uniqueIDref == dong:
            print("Energy east:", entry3.energyEast)
            crystalsEast += [x for x in entry3.crystalsEast]
                
    mapEast = toMap(crystalsEast)
    #print("East: ", mapEast)
    
    crystalsWest = []
    
    twest_partial = tcomp.CopyTree( constructConditionFromUniqueIDComp(uniqueIDref) )
    for j, entry2 in enumerate(twest_partial):
        dong = constructUniqueID(entry2)
        if (uniqueIDref == dong):
            print("Energy west:", entry2.energyWest)
            crystalsWest += [x for x in entry2.crystalsWest]

    mapWest = toMap(crystalsWest)
    #print("West: ", mapWest)
    
    #print(twest_partial.GetEntries())


    twave_partial = twave.CopyTree( constructConditionFromUniqueIDWave(uniqueIDref) )
    for i,entry in enumerate(twave_partial):
        if( constructUniqueIDwave(entry) == uniqueIDref ):
            if counter > 3:
                break
            counter = counter + 1

            fig, axarr = plt.subplots(6,9, sharey=True, sharex=True,figsize=(15, 10))
            #print("Entry #", i+1)
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
                    elif(np.abs( np.mean((list1[j][ding])[0:6]) - np.max(list1[j][ding]) ) > globalThreshold): #global threshold = 60
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
                plt.savefig("./images/UnpackedIslands_calo"+str(twave.caloNum).zfill(2)+"_run"+str(twave.runNum)+"_subRun"
                            +str(twave.subRunNum).zfill(5)+"_uniqueID_"+str(uniqueIDref)+".png",bbox_inches='tight')
            plt.show()

            break
			
#similar to the function above, but also plots the unpacked island data alongside the 
def islandPlotWaveOnly(uniqueIDref, twave, saveImage = True, globalThreshold = None):
    if(globalThreshold == None):
        globalThreshold = 60 #default value 60
    counter = 0
    
    fout = r.TFile("temp_tree_storage.root","recreate")
    twave_partial = twave.CopyTree( constructConditionFromUniqueIDWave(uniqueIDref) )
    for i,entry in enumerate(twave_partial):
        if( constructUniqueIDwave(entry) == uniqueIDref ):
            if counter > 3:
                break
            counter = counter + 1

            fig, axarr = plt.subplots(6,9, sharey=True, sharex=True,figsize=(15, 10))
            #print("Entry #", i+1)
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
                    elif(np.abs( np.mean((list1[j][ding])[0:6]) - np.max(list1[j][ding]) ) > globalThreshold): #global threshold = 60
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
            

            if(saveImage):
                plt.savefig("./images/UnpackedIslands_calo"+str(twave.caloNum).zfill(2)+"_run"+str(twave.runNum)+"_subRun"
                            +str(twave.subRunNum).zfill(5)+"_uniqueID_"+str(uniqueIDref)+".png",bbox_inches='tight')
            plt.show()

            break
#takes the unique id for a crystal and parses it into its components.
def parseUniqueID(uniqueID, printKey = None):
	uniqueID = str(uniqueID)
	runNum = int(uniqueID[0:5])
	subRunNum = int(uniqueID[5:10])
	fillNum = int(uniqueID[10:15])
	caloNum = int(uniqueID[15:20])
	islandNum = int(uniqueID[20:25])
	
	if(printKey is True):
		print("From UniqueID: ", uniqueID)
		print("                runNum:", runNum)
		print("                subRunNum:", subRunNum)
		print("                fillNum:", fillNum)
		print("                caloNum:", caloNum)
		print("                islandNum:", islandNum)
	return( (runNum, subRunNum, fillNum, caloNum, islandNum ) )



def plotNonUnique(uniqueID, teast, twest, tnon, saveImage = False):
    
    xtalsEast = []
    xtalsWest = []
    
    energiesWest = []
    energiesEast = []
    timesWest = []
    timesEast = []
    
    conditionEast = constructConditionFromUniqueIDEast(uniqueID)
    conditionWest = constructConditionFromUniqueIDWest(uniqueID)
    
    fout = r.TFile("temp_tree_storage.root","recreate")
    teast_partial = teast.CopyTree(conditionEast)
    twest_partial = twest.CopyTree(conditionWest)
    #print("     Matching entries in this file:", teast_partial.GetEntries())
    #print("                                   ", twest_partial.GetEntries())
    
    for j, ding in enumerate(twest_partial):
        xtalsWest.append( toFlatMap(ding.crystalsWest) )
        energiesWest.append(ding.energy)
        timesWest.append(ding.time)
    for ding in teast_partial:
        xtalsEast.append( toFlatMap(ding.crystalsEast) )
        energiesEast.append(ding.energy)
        timesEast.append(ding.time)


        
    print("West (Red):  ", len(xtalsWest))
    print("East (Green):", len(xtalsEast))

    newimg1 = Image.new('RGBA', size=(9, 6), color=(255,255,255,255))
    imvec = []

    for i, cluster in enumerate(xtalsWest):
        clusternew = []
        for clusterentry in cluster:
            if clusterentry == 0:
                clusternew.append((255,255,255))
            else:
                #clusternew.append((clusterentry*(i+1)*100,0,0))
                clusternew.append((0,clusterentry*(i+1)*100,0))

        clusternew.reverse()
        img1 = Image.new('RGBA', size=(9, 6), color=(255, 0, 0, 0))
        img1.putdata(clusternew)

		
        imvec.append(img1.copy())

    for i, cluster in enumerate(xtalsEast):
        clusternew = []
        for clusterentry in cluster:
            if clusterentry == 0:
                clusternew.append((255,255,255))
            else:
                #clusternew.append((0,clusterentry*(i+1)*100,0))
                clusternew.append((0,0,clusterentry*(i+1)*100))

        clusternew.reverse()
        img1 = Image.new('RGBA', size=(9, 6), color=(255, 0, 0, 0))
        img1.putdata(clusternew)

        imvec.append(img1.copy())

        
    nClusters = len(xtalsEast) + len(xtalsWest)
    fig,ax = plt.subplots(1,nClusters,figsize=(16,3))
    
    
    print("Total West Energy: ", sum(energiesWest))
    print("Total East Energy: ", sum(energiesEast))
    print("deltaE = ", sum(energiesEast) - sum(energiesWest))
    
    energies = energiesWest + energiesEast
    times = timesWest + timesEast
    for k, imi in enumerate(imvec):
        ax[k].imshow(np.asarray(imi))
        ax[k].set_title("Energy: "+str(energies[k])+"\n Time: "+str(times[k]) )
        newimg1 = Image.blend(newimg1, imi,alpha=0.3)
    for axi in ax:
        axi.set_xticks(np.arange(-.5, 9, 1))
        axi.set_yticks(np.arange(-.5, 6, 1))
        axi.set_xticklabels([])
        axi.set_yticklabels([])
        axi.tick_params(length=0)
        axi.grid(color='lightgrey', linestyle='-', linewidth=2)
    if(saveImage):
        plt.savefig("./images/Images_NonUnique_"+str(uniqueID)+"_Individual.png",bbox_inches='tight')
        
    plt.show()

    plt.imshow(np.asarray(newimg1))
    axi = plt.gca()
    axi.set_xticks(np.arange(-.5, 9, 1))
    axi.set_yticks(np.arange(-.5, 6, 1))
    axi.set_xticklabels([])
    axi.set_yticklabels([])
    axi.tick_params(length=0)
    axi.grid(color='lightgrey', linestyle='-', linewidth=2)
    plt.title(uniqueID)
    if(saveImage):
        plt.savefig("./images/Images_NonUnique_"+str(uniqueID)+"_Overlap.png",bbox_inches='tight')
    plt.show()