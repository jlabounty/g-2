#!/usr/bin/env python
# coding: utf-8

# In[1]:


from fit_util import *
from omega_a_fitting import *
from pileup_correction import *
from lost_muon_calculation import *


# In[2]:


f = r.TFile("../truncationTest/data/results_1MissingFile_FullVsTrunc.root")
f.cd("clustersAndCoincidences")
f.ls()


# In[3]:


clusters = f.Get("clustersAndCoincidences").Get("clusters")
print(clusters)


# In[4]:


e1 = 1700
e2 = 3100
calo = 3

wiggle = MakeWiggleFromTH3(clusters, e1, e2, calo)


# In[5]:


DumpClass(wiggle)


# In[6]:



# ---
# 
# ### Now fit the wiggle plot

# In[7]:


fitFunc = WiggleFit(GetBlindingPhrase("./blinding.txt"), "5par")


# In[8]:


fitFunc([0],[2+x for x in range(18)])


# In[ ]:


fit = BuildTF1(fitFunc, 5, "5par", "five_parameter_fit", 30, 650)
fit.SetParameters([10000,64.4,0.33,0,0])
fit.SetParNames()


# In[ ]:


#fit.f.Draw()
#c.Draw()


# In[ ]:


fitter = WiggleFitter(wiggle.h, fit, "5par", "REMB", 1)


# In[ ]:


fitter.Fit(2)


# In[ ]:


DumpClass(fitter)


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:


fitter.f.GetParameter(0)


# In[ ]:


fitter.Draw()


# In[3]:

