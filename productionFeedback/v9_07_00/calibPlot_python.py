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

f162 = r.TFile("./data/02cfd09d-7c49-4727-9698-49d6331424f3-gm2offline_full_11569852_16355.00162.root") #processed output of hadd.sh
#f162 = r.TFile("./data/c912e49f-a504-4949-9468-cf7729561deb-gm2offline_full_11569142_16355.00161.root")
t162 = f162.Get("Events")
f162.ls()


histvec = []
for i in range(1,25):
    hist = r.TH1D("hist","calo"+str(i),100,0,2)
    cut = r.TCut("gm2calo::CaloCalibrationConstants_longTermGainCorrectionDAQ_corrector_fullwithDQC.obj.caloNum=="+str(i))
    t162.Draw("gm2calo::CaloCalibrationConstants_longTermGainCorrectionDAQ_corrector_fullwithDQC.obj.constants>>hist",cut)

    hist.SetLineColor(i)
    histvec.append(hist.Clone("h"+str(i)))
        
print(histvec)

c2 = r.TCanvas("c2","c2",1200,1200)
c2.Divide(5,5)
for i,hi in enumerate(histvec):
    c2.cd(i+1)
    hi.SetLineColor(2)
    hi.Draw()
    histvec[23].SetLineColor(3)
    histvec[23].Draw("SAME")
c2.Draw()

c2.Print("c2.png")
c2.Print("c2.root")


files = ["02775539-c3f3-4117-bf03-96dd3145e669-gm2offline_full_11569154_16355.00165.root",
	"02cfd09d-7c49-4727-9698-49d6331424f3-gm2offline_full_11569852_16355.00162.root",
	"086c4c6f-d138-422a-9248-ca33a0b58bcf-gm2offline_full_11570444_16355.00168.root",
	"0f969540-98e4-4b35-821e-68375a68e5ce-gm2offline_full_11578773_16355.00166.root",
	"40522a0b-f75b-4250-921b-95b53fa6c486-gm2offline_full_11569168_16355.00160.root",
	"7e8951a2-b59e-4dad-8183-c1d27875d265-gm2offline_full_11590171_16355.00167.root",
	"89f73e7c-5f9e-4711-b7d9-4aa518dae6dc-gm2offline_full_11589378_16355.00169.root",
	"92f7a49c-396d-4d98-99fb-3f591230fbbf-gm2offline_full_11569847_16355.00164.root",
	"bbf53244-a5b3-41b8-af08-d8cf534b4c94-gm2offline_full_11590342_16355.00163.root",
	"c912e49f-a504-4949-9468-cf7729561deb-gm2offline_full_11569142_16355.00161.root"]
print(files)

filevec = []
subruns = []
for i, file in enumerate(files):
	fi = r.TFile("./data/"+file)
	ti = fi.Get("Events")
	subRunNum = file[70:73]
	subruns.append(subRunNum)
	print(subRunNum)

	hist = r.TH1D("hist","SubRun"+str(subRunNum),100,0,2)
	cut = r.TCut("gm2calo::CaloCalibrationConstants_longTermGainCorrectionDAQ_corrector_fullwithDQC.obj.caloNum=="+str(24))
	ti.Draw("gm2calo::CaloCalibrationConstants_longTermGainCorrectionDAQ_corrector_fullwithDQC.obj.constants>>hist",cut)

	hist.SetLineColor(i)
	hist.SetDirectory(0)

	filevec.append(hist.Clone("h"+str(subRunNum)))
	filevec[i].SetDirectory(0)
	
	fi.Close()

print(filevec)


c = r.TCanvas()
#c.Divide(5,5)
leg = r.TLegend(0.1,0.8,0.4,0.9)
leg.SetNColumns(2)
for i, hi in enumerate(filevec):
#	c.cd(i+1)
	hi.SetLineColor(i+1)
	hi.SetTitle("Run "+files[i][62:67])
	if i > 8:
		hi.SetLineColor(i+2)
	if i < 0.5:
		hi.Draw()
	else:
		hi.Draw("SAME")
	leg.AddEntry(hi,"Sub Run: "+subruns[i],"l")

leg.Draw("SAME")
c.Draw()

c.Update()
c.Print("./c.root")
