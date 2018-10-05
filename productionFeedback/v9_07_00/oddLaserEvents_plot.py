import ROOT as r
import math
r.gStyle.SetOptStat(0)
r.gStyle.SetOptFit(1111)
import matplotlib.pyplot as plt
import csv
import pandas

import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
matplotlib.rc('xtick', labelsize=20) 
matplotlib.rc('ytick', labelsize=20) 
import os

print("Starting...")

f = r.TFile("./data/02cfd09d-7c49-4727-9698-49d6331424f3-gm2offline_full_11569852_16355.00162.root") #processed output of hadd.sh
t = f.Get("Events")
f.ls()


histvec = []
for i in range(1,25):
	t.Draw("energy:runNum*1000+subRunNum","energy > 40000 && time < 0 && caloNum == "+str(i),"")
