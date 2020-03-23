from omega_a_fitting import *
#from pileup_correction import *
from ding import *
import pickle

#f = r.TFile("./data/results_10MissingOutputFiles_9day_histOnly.root")
f = r.TFile("../truncationTest/data/results_1MissingFile_FullVsTrunc.root")
f.ls()

clusters = f.Get("clustersAndCoincidences").Get("clusters").Clone("clusters")

Ninitial = clusters.Project3D("yx").Clone()
#Ninitial.Rebin2D(10,10)

corrector = PileupCorrector(Ninitial, "Test", 0, 2)
corrector.verbosity = 100
corrector.fitOptions = "REMB"
corrector.ComputeRhoDouble()
#corrector.FullChain()

pickle.dump(corrector, open("corrector.pickle","wb"))