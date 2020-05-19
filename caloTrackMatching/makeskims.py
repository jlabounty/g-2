import ROOT as r
import os

path = "/gm2/data/g2be/Production/TrackAndTrackCaloTrees/Run1/EG/"
files = os.listdir(path)

for file in files:
    if("root" in file):
        f = r.TFile(path+file)
        f.ls()
        t_full = f.Get("trackAndTrackCalo/tree")
        f_temp = r.TFile("/pnfs/GM2/scratch/users/labounty/eg_tracks/"+file,"recreate")
        t = t_full.CopyTree("passTrackQuality && nCluMatches == 1 && hasDecayVertex && !hitVolume && passDecayVertexQuality ")
        t.Print()
        f_temp.Write()
        f_temp.Close()