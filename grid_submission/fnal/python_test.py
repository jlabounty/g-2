import sys
import os

import ROOT as r

import python_fit

print("Hello python")

with open(sys.argv[1],"w") as file:
	file.write("Hello python file! \n")
	for x in sys.argv:
		file.write(x+"\n")

print("All done. File is:", sys.argv[1])

c = r.TCanvas()
h =r.TH1D("h","Example",10,0,10)


fout = r.TFile(sys.argv[1]+".root","RECREATE")
h.Write()
fout.Close()

print("All done with root!")
