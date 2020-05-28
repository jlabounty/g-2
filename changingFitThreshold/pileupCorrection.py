import ROOT as r 
import math
import numpy as np 
#g-2 Blinding Software
from BlindersPy3 import Blinders
from BlindersPy3 import FitType
from fit_util import *
#from standardInclude import *
import matplotlib.pyplot as plt

from py_th2 import *
from python_pileup import *
import time
from pickle_util import *


f = r.TFile("/home/jlab/g-2/changingFitThreshold/data/results_truncation_changingFitThreshold_300_100_EndGame.root")
f.cd("clustersAndCoincidencesTrunc")
f.ls()
clusters = f.Get("clustersAndCoincidencesTrunc").Get("clusters").Clone()
print(clusters)

caloNum = 0
Ninitial = clusters.Project3D("yx").Clone()
Ninitial.Rebin2D(1,1)


t1 = time.time()

print("Creating ding...")
ding = pyTH2()
print("Filling...")

fillPyTH2fromRoot(Ninitial, ding)

t2 = time.time()
print(t2 - t1, "seconds")
t1 = t2

print("Copying...")
ding2 = pyTH2(ding)

t2 = time.time()
print(t2 - t1, "seconds")
t1 = t2

ding = PythonPileup(ding2, "test")

t2 = time.time()
print(t2 - t1, "seconds")
t1 = t2

ding.computeRhoDouble()

t2 = time.time()
print(t2 - t1, "seconds")
t1 = t2

ding.ComputeDoubleCorrection()

t2 = time.time()
print(t2 - t1, "seconds")
t1 = t2

ding.ComputeTripleCorrection()

t2 = time.time()
print(t2 - t1, "seconds")
t1 = t2

#storeData("./pileup.pickle", ding)
pickle_dump(ding, "./pileup.pickle")


t2 = time.time()
print(t2 - t1, "seconds")
t1 = t2

print("All done.")
