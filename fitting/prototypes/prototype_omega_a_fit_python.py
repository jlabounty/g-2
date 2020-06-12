from python_fit import *
import ROOT as r 
import matplotlib.pyplot as plt

# hist = r.TH1D("h","h",100,0,10)
# fi = r.TF1("fi","pol1",0,10)
# fi.SetParameters(1,0.25)
# hist.FillRandom("fi", 10000)

f = r.TFile("/home/jlab/g-2/changingFitThreshold/data/results_truncation_changingFitThreshold_300_100_EndGame.root")
hist3 = f.Get("clustersAndCoincidences/clusters").Clone()
hist3.GetYaxis().SetRangeUser(1700,3000)
hist = hist3.Project3D("x").Clone("hist")
hist.Rebin(6)

c = r.TCanvas()
hist.Draw()
c.SetLogy()
c.Draw()

print("Woo")

test = omega_a_fit(hist, "test_fit_file.py",fitoptions="R")

print(test)

test.draw() 
plt.show()

print("All done!")