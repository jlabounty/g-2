
# coding: utf-8

# In[1]:


#from standardInclude import *
import ROOT as r
import numpy as np
import matplotlib.pyplot as plt

# In[2]:


f = r.TFile("./data/gm2offline_ana_18398265_1544564276.1650.root")
t = f.Get("SimuTreeMaker").Get("gm2ringsimTree")
t.Print()


# In[3]:


c = r.TCanvas()
nMu = t.Draw("muDecayR:muDecayY:muDecayTheta","","")
print(nMu)
c.Draw()


# In[4]:


rawMuons = [[],[],[]]
for i in range(nMu):
    rawMuons[0].append(t.GetV1()[i])
    rawMuons[1].append(t.GetV2()[i])
    rawMuons[2].append(t.GetV3()[i])


# In[5]:


#plt.plot(rawMuons[0],rawMuons[1],",")
#plt.show()

#rawMuonArr = np.asarray(rawMuons, dtype=np.float32)
# In[ ]:


#import numpy as np
from scipy import stats
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D

kde = stats.gaussian_kde(rawMuons)
density = kde(values)

#fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
#x, y, z = values
#ax.scatter(x, y, z, c=density)
#plt.show()

