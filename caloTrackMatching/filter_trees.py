import ROOT as r 
import numpy as np 
import pandas 
import os 

def main():
    outdir = "/pnfs/GM2/scratch/users/labounty/caloTrackMatching/"

    paths = [
        #'./input/', 
        #'./input_endgame/', 
        #'./input_endgame_sam/',
        "./input_9day/",
        #'./data/',
         ]

    cutstring = {
        'trackCalo':"trackQuality", 
        'clusters':None, 
        'tracks':"passTrackQuality", 
        'trackAndTrackCalo':"passTrackQuality && nCluMatches == 1 && hasDecayVertex && !hitVolume && passDecayVertexQuality"
        }

    treenames = {
        'trackCalo':"TrackCaloMatching", 
        'tracks':"tracker", 
        'trackAndTrackCalo':"tree"
    }

    for path in paths:
        os.system("mkdir -p "+outdir+path)
        files = [x for x in os.listdir(path) if ".root" in x]
        for file in files:
            f = r.TFile(path+file)
            #f.ls()
            for name in cutstring:
                result = f.cd(name)
                #f.ls()
                print(name, result)
                if(result == True):
                    print("Processing appropriate function")
                    if(cutstring[name] is None):
                        processHistFile(name, f, file)
                    else:
                        processTreeFile(name, f, cutstring[name], outdir+path+name+"_"+file, treenames[name])
                else:
                    print("Cannot access this directory. Skipping file", file)

def processHistFile(name, f, file):
    print("Doing nothing to histograms")

def processTreeFile(name, f, cutstring, outfile,treename):
    t = f.Get(name+"/"+treename)
    t.Print()
    fout = r.TFile(outfile, "RECREATE")
    fnew = t.CopyTree(cutstring)
    fnew.Write()
    fout.Write()
    fout.Close()
    print("Written file:", outfile)




    


if __name__ == "__main__":
    main()