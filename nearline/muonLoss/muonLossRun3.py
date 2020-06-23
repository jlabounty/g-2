import ROOT as r
import os
import pandas
import numpy as np

path = "/datalocal/nearlineHists_merged/"
outpath = "/home/daq/labounty/run3_nearlineLMbump/"
files = os.listdir(path)

# path = "/home/jlab/g-2/nearline/data/"
# files = ['gm2nearline_hists_run34922.root']


ratios = []

for i, file in enumerate(files):
    f = r.TFile(path+file)
    # f.ls()

    run = int(file.split("run")[1].split(".root")[0])

    h1 = f.Get("CoincidenceFinderLM/clusterTimecaloNumsingle_").Clone("h1")
    h3 = f.Get("CoincidenceFinderLM/clusterTimecaloNumtriple_").Clone("h3")

    h1_x = h1.Project3D("y").Clone("h1_x")

    # h3.Divide(h1)
    scaleFactor = h1_x.Integral(h1_x.FindBin(30*1000/1.25), -1)
    print(scaleFactor)
    # print(h1,h3)

    # c = r.TCanvas()
    # h3.Project3D("y").Draw("hist")
    # c.Draw()
    # c.Update()

    h3y = r.TH1D()
    h3.Project3D("y").Copy(h3y)
    # h3y = h3.Project3D("y").Clone("h3y")
    if(scaleFactor > 0):
        h3y.Scale(1/scaleFactor)


        splash = h3y.Integral( h3y.FindBin(0*1000/1.25), h3y.FindBin(30*1000/1.25) )
        bump = h3y.Integral( h3y.FindBin(50*1000/1.25), h3y.FindBin(150*1000/1.25) )

        print(bump, splash)
    else:
        bump = np.nan
        splash = np.nan

    ratios.append([ run, splash, bump, scaleFactor ])

    outfile = outpath+"out.root"
    if(i < 1):
        #create a new root file
        fout = r.TFile(outfile, "RECREATE")
        h3y.Write("h_"+str(run))
    else:
        #append to that root file
        fout = r.TFile(outfile, "UPDATE")
        h3y.Write("h_"+str(run))
    fout.Close()
    # break

df = pandas.DataFrame(ratios, columns=['run', 'splash', 'bump', 'scalefactor'])
print(df.head())
print(df.describe())

df.to_csv(outpath+"df.csv", sep="|")

print("All done.")