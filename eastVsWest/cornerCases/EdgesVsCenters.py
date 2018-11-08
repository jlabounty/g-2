
# coding: utf-8

# In[1]:


from evwTools import *


# In[5]:


files = ["results_full.root"]
#files = ["gm2offline_ana_12396088_16357.00078.root"]
path = "/home/jlab/g-2/eastVsWest/data/dataExternal/Oct16DataSet/"
#this is only a subset, but I have it unpacked already.
prodString = 'v9_08_NewCalibration'

for file in files:
	print("Starting file:", file)
	f2 = r.TFile(path + file)
	tcomp = f2.Get("farline").Get("evwTree")
	tcomp.Print()


	# In[16]:


	caloEdgeVec = []
	for calo in range(1,25):
	    print("Starting Calo:" ,calo)
	    hi = r.TH2D("hi","Calo"+str(calo)+" Edges",600,0,6000,600,0,6000)
	    tcomp.Draw("energyWest:energyEast>>hi","caloNum == "+str(calo)+
		       " && (positionWest.first > 8.0 || positionWest.first < 1.0 || positionWest.second < 1.0 || positionWest.second > 5.0)","goff")
	    caloEdgeVec.append( hi.Clone( "h"+str(calo) ) )
	    
	print(caloEdgeVec)


	# In[13]:


	c = r.TCanvas("c","c",6300,4000)
	c.Divide(6,4)
	for i,hi in enumerate(caloEdgeVec):
	    c.cd(i+1)
	    hi.Draw("COLZ")
	    r.gPad.SetLogz()
	c.Draw()
	c.Print("./Edges"+prodString+:".root")
	c.Print("./Edges"+prodString+:".png")


	# In[18]:


	caloCenterVec = []
	for calo in range(1,25):
	    print("Starting Calo:" ,calo)
	    hi = r.TH2D("hi","Calo"+str(calo)+" Center",600,0,6000,600,0,6000)
	    tcomp.Draw("energyWest:energyEast>>hi","caloNum == "+str(calo)+
		       " && !(positionWest.first > 8.0 || positionWest.first < 1.0 || positionWest.second < 1.0 || positionWest.second > 5.0)","goff")
	    caloCenterVec.append( hi.Clone( "h"+str(calo) ) )
	    
	print(caloCenterVec)


	# In[19]:


	c = r.TCanvas("c","c",6300,4000)
	c.Divide(6,4)
	for i,hi in enumerate(caloCenterVec):
	    c.cd(i+1)
	    hi.Draw("COLZ")
	    r.gPad.SetLogz()
	c.Draw()

	c.Print("./Centers"+prodString+:".root")
	c.Print("./Centers"+prodString+:".png")


