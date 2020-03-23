from pileup_correction import *
from fit_util import *
import ROOT as r 

print("Starting pileup correction")

f = r.TFile("../truncationTest/data/results_1MissingFile_FullVsTrunc.root")
f.ls()

clusters = f.Get("clustersAndCoincidences").Get("clusters").Clone("clusters")

Ninitial = clusters.Project3D("yx").Clone()
Ninitial.Rebin2D(10,1)

corrector = PileupCorrector(Ninitial, "Test", 0 , 3)
corrector.verbosity = 100
corrector.fitOptions = "REMB"
corrector.ComputeRhoDouble()

corrector.ComputeDoubleCorrection()
corrector.FitDoublePileupAndApplyCorrection()

secondRound = True
if(secondRound):
    c2 = PileupCorrector(corrector.h_doublePileupCorrected, "Test2", 0 , 3)
    c2.verbosity = 100
    c2.fitOptions = "REMB"
    c2.ComputeRhoDouble()

    c2.ComputeDoubleCorrection()
    c2.FitDoublePileupAndApplyCorrection()

    c = r.TCanvas()
    c2.h_y.Draw()
    c.Draw()

print("All done!")