import ROOT as r 
import numpy as np 
import pandas
import os



def main():

    names = ['trackCalo', 'clusters', 'tracks', 'trackAndTrackCalo']
    funcdict = {'trackCalo':trackcalo, 'clusters':clusters, 'tracks':tracks, 'trackAndTrackCalo':trackCaloSam}

    paths = [
        #'./input/',                 #run2c trees
        #'./input_endgame/',         #endgame trees for tracks only
        './input_endgame_sam/',    #endgame trees for clusters + calo-track matching
        #'./data/',                 #test directory for local area
         ]
    paths = ["/pnfs/GM2/scratch/users/labounty/caloTrackMatching/"+x for x in paths]
    #path = paths[3]
    #files = ['gm2tracker_ana.root']
    for path in paths:
        print("Starting path:", path)
        files = [x for x in os.listdir(path) if ".root" in x]
        print(files)

        r.globalSeed = 1234
        r.gInterpreter.ProcessLine('.L testfunc.C')
        r.initializeRNG(1234)

        for file in files:
            f = r.TFile(path+file)
            #f.ls()
            for name in names:
                result = f.cd(name)
                #f.ls()
                print(name, result)
                
                if(result == True):
                    print("Processing appropriate function")
                    funcdict[name](name+"/", f, file)
                elif(name in file):
                    print("Processing appropriate function")
                    funcdict[name]("", f, file)
                else:
                    print("Cannot access this directory. Skipping file", file)
                
    print("All done!")

def gethist(name, title, timebins, binstart, binend):
    '''
        Creates a 3D histogram with the apprpriate bins
        X: time
        Y: y-position
        Z: calo/station number
    '''
    h = r.TH3I(name,title,
            timebins, binstart, binend,
            600, -200, 200,
            2,10,20
        )
    h.SetDirectory(0)
    return h

def saveToRootFile(name, hists):
    fout = r.TFile(name,'recreate')
    fout.cd()
    for h in hists:
        h.Write()
    fout.Write()
    fout.Close()

    print("Histograms written to:", name)

def randomizeTimes( x, p=[None] ):
    inputtime = x[0]
    time = inputtime
    
    w0 = 2.6094
    A = 2.80
    tauA = 56.6
    B = 6.18
    tauB = 6.32
    
    wCBO =  (w0 - (A/(tauA)) * r.TMath.Exp(-time/(1000.0*tauA)) - (B/(tauB)) * r.TMath.Exp(-time/(tauB*1000.0)) ) #MHz
    wa =  r.TMath.TwoPi() * 0.2291 #MHZ
    wc =  r.TMath.TwoPi() / 0.14919 #MHz

    factor = 1.0
    wY = factor * (wCBO) * r.TMath.Sqrt( (2 * wc / (factor * wCBO)) -1.0 ) 
    wVW = wc - (2.0 * wY)

    TCBO = r.TMath.TwoPi() / wCBO
    Ta = r.TMath.TwoPi() / wa
    TVW = r.TMath.TwoPi() / wVW
    TY = r.TMath.TwoPi() / wY
    T_diff= r.TMath.TwoPi()/(wCBO-wa)
    
    #time += (rng->Uniform()-0.5)*(Ta*1000.0);// w_a 4365
    timestorandomize = [
                        Ta, 
                        TCBO, 
                        TVW, 
                        TY, 
                        T_diff,
                       ]
    
    for periodi in timestorandomize:
        #time += (np.random.random() - 0.5)*(periodi)
        time += -1*np.abs((np.random.random() - 0.5))*(periodi)
    #print(inputtime, time, TCBO, Ta)
    
    #print(time, time/1000.)
    return time

def trackcalo(name, f, file):
    '''
        Process the matched calo trees into an appropriate histogram format and save
    '''
    print(f, name)
    f.cd(name)
    f.ls()

    #t = f.Get(name+"/TrackCaloMatching")
    t = f.Get(name+"TrackCaloMatching")
    t.Print()
    #cutstring = "passTrackQuality && nCluMatches == 1 && hasDecayVertex && !hitVolume && passDecayVertexQuality"
    cutstring = "trackQuality"

    h_trackerBeamPos = gethist("trackerBeamPos", 
                        "Tracker Beam Position vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:decayVertexPosY:clusterTime/1000.>>trackerBeamPos",cutstring,"goff")

    h_trackerBeamPosRand = gethist("trackerBeamPosRand", 
                        "Tracker Beam Position vs. Rand Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:decayVertexPosY:testfunc(clusterTime)/1000.>>trackerBeamPosRand",cutstring,"goff")

    h_trackerCaloPos = gethist("trackerCaloPos", 
                        "Tracker Calo Face Position vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:caloVertexPosY:clusterTime/1000.>>trackerCaloPos",cutstring,"goff")

    h_trackerCaloPosRand = gethist("trackerCaloPosRand", 
                        "Tracker Calo Face Position vs. Rand Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:caloVertexPosY:testfunc(clusterTime)/1000.>>trackerCaloPosRand",cutstring,"goff")
    
    h_caloCaloPos = gethist("caloCaloPos", 
                        "Calo Face Position from Clusters vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:(clusterY):clusterTime/1000.>>caloCaloPos",cutstring,"goff")

    h_caloCaloPosRand = gethist("caloCaloPosRand", 
                        "Calo Face Position from Clusters vs. Rand Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:(clusterY):testfunc(clusterTime)/1000.>>caloCaloPosRand",cutstring,"goff")

    h_trackerCaloPos_noRadialField = gethist("trackerCaloPos_noRadialField", 
                        "Tracker Calo Face Position [Straight Line Extrapolation] vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    #t.Draw("station:(clusterTime-decayTime)*decayVertexMomY/(14.9723):clusterTime/1000.>>h_trackerCaloPos_noRadialField",cutstring,"goff")
    t.Draw("station:(decayVertexPosY - (time - decayTime)*299.79*decayVertexMomY/TMath::Sqrt(decayVertexMomZ**2 + decayVertexMomY**2 + decayVertexMomZ**2)):clusterTime/1000.>>h_trackerCaloPos_noRadialField",cutstring,"goff")


    h_trackerCaloPos_noRadialFieldRand = gethist("trackerCaloPos_noRadialFieldRand", 
                        "Tracker Calo Face Position [Straight Line Extrapolation] vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    #t.Draw("station:(clusterTime-decayTime)*decayVertexMomY/(14.9723):clusterTime/1000.>>h_trackerCaloPos_noRadialField",cutstring,"goff")
    t.Draw("station:(decayVertexPosY - (time - decayTime)*299.79*decayVertexMomY/TMath::Sqrt(decayVertexMomZ**2 + decayVertexMomY**2 + decayVertexMomZ**2)):testfunc(clusterTime)/1000.>>h_trackerCaloPos_noRadialFieldRand",cutstring,"goff")

    saveToRootFile("./data/matchedTracks_"+file,  [h_trackerBeamPos, h_trackerCaloPos, h_caloCaloPos,
                                                   h_trackerCaloPosRand, h_caloCaloPosRand, h_trackerBeamPosRand,
                                                   h_trackerCaloPos_noRadialField, h_trackerCaloPos_noRadialFieldRand])

    print("All done!")

def trackCaloSam(name, f, file):
    '''
        Process the matched calo trees produced by Sam into an appropriate histogram format and save
    '''
    print(f, name)
    f.cd(name)
    f.ls()

    #t = f.Get(name+"/tree")
    t = f.Get(name+"tree")
    t.Print()
    cutstring = "passTrackQuality && nCluMatches == 1 && hasDecayVertex && !hitVolume && passDecayVertexQuality"
    #cutstring = "trackQuality"

    h_trackerBeamPos = gethist("trackerBeamPos", 
                        "Tracker Beam Position vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:decayVertexPosY:clusterTime/1000.>>trackerBeamPos",cutstring,"goff")

    h_trackerBeamPosRand = gethist("trackerBeamPosRand", 
                        "Tracker Beam Position vs. Rand Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:decayVertexPosY:testfunc(clusterTime)/1000.>>trackerBeamPosRand",cutstring,"goff")

    h_trackerCaloPos = gethist("trackerCaloPos", 
                        "Tracker Calo Face Position vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:caloVertexPosY:clusterTime/1000.>>trackerCaloPos",cutstring,"goff")

    h_trackerCaloPosRand = gethist("trackerCaloPosRand", 
                        "Tracker Calo Face Position vs. Rand Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:caloVertexPosY:testfunc(clusterTime)/1000.>>trackerCaloPosRand",cutstring,"goff")
    
    h_caloCaloPos = gethist("caloCaloPos", 
                        "Calo Face Position from Clusters vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:(clusterY):clusterTime/1000.>>caloCaloPos",cutstring,"goff")

    
    h_caloCaloPosRand = gethist("caloCaloPosRand", 
                        "Calo Face Position from Clusters vs. Rand Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:(clusterY):testfunc(clusterTime)/1000.>>caloCaloPosRand",cutstring,"goff")

    h_trackerCaloPos_noRadialField = gethist("trackerCaloPos_noRadialField", 
                        "Tracker Calo Face Position [Straight Line Extrapolation] vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    #t.Draw("station:(clusterTime-decayTime)*decayVertexMomY/(14.9723):clusterTime/1000.>>trackerCaloPos_noRadialField",cutstring,"goff")
    t.Draw("station:(decayVertexPosY - (caloVertexTime - decayTime) * 299.79 * decayVertexMomY / decayVertexMom):(decayTime)/1000.>>trackerCaloPos_noRadialField",cutstring,"goff")


    h_trackerCaloPos_noRadialFieldRand = gethist("trackerCaloPos_noRadialFieldRand", 
                        "Tracker Calo Face Position [Straight Line Extrapolation] vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    #t.Draw("station:(clusterTime-decayTime)*decayVertexMomY/(14.9723):testfunc(clusterTime)/1000.>>trackerCaloPos_noRadialFieldRand",cutstring,"goff")
    t.Draw("station:(decayVertexPosY - (caloVertexTime - decayTime) * 299.79 * decayVertexMomY / decayVertexMom):testfunc(decayTime)/1000.>>trackerCaloPos_noRadialFieldRand",cutstring,"goff")

    saveToRootFile("./data/matchedTracksSam_"+file, [h_trackerBeamPos, h_trackerCaloPos, h_caloCaloPos,
                                                   h_trackerCaloPosRand, h_caloCaloPosRand, h_trackerBeamPosRand,
                                                   h_trackerCaloPos_noRadialField, h_trackerCaloPos_noRadialFieldRand])


def tracks(name, f, file):
    print(f, name)
    f.cd(name)
    f.ls()

    #t = f.Get(name+"/tracker")
    t = f.Get(name+"tracker")
    t.Print()
    #cutstring = "passTrackQuality && nCluMatches == 1 && hasDecayVertex && !hitVolume && passDecayVertexQuality"
    cutstring = "passTrackQuality"

    h_trackerBeamPos = gethist("trackerBeamPos", 
                        "Tracker Beam Position vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:decayVertexPosY:decayTime/1000.>>trackerBeamPos",cutstring,"goff")

    h_trackerCaloPos = gethist("trackerCaloPos", 
                        "Tracker Calo Face Position vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:caloVertexPosY:decayTime/1000.>>trackerCaloPos",cutstring,"goff")

    h_trackerBeamPosRand = gethist("trackerBeamPosRand", 
                        "Tracker Beam Position vs. Rand Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:decayVertexPosY:testfunc(decayTime)/1000.>>trackerBeamPosRand",cutstring,"goff")

    h_trackerCaloPosRand = gethist("trackerCaloPosRand", 
                        "Tracker Calo Face Position vs. Rand Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:caloVertexPosY:testfunc(decayTime)/1000.>>trackerCaloPosRand",cutstring,"goff")

    h_trackerCaloPos_noRadialField = gethist("trackerCaloPos_noRadialField", 
                        "Tracker Calo Face Position [Straight Line Extrapolation] vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    t.Draw("station:maxDriftTime*decayVertexMomY/(14.9723):decayTime/1000.>>trackerCaloPos_noRadialField",cutstring,"goff")
    t.Draw("station:(decayVertexPosY - (time - decayTime)*299.79*decayVertexMomY/TMath::Sqrt(decayVertexMomZ**2 + decayVertexMomY**2 + decayVertexMomZ**2)):(time)/1000.>>trackerCaloPos_noRadialField",cutstring,"goff")


    h_trackerCaloPos_noRadialFieldRand = gethist("trackerCaloPos_noRadialFieldRand", 
                        "Tracker Calo Face Position [Straight Line Extrapolation] vs. Time; Time [#mu s]; y [mm]; Station Number",
                        4698, 0, 700).Clone()
    #t.Draw("station:maxDriftTime*decayVertexMomY/(14.9723):testfunc(decayTime)/1000.>>trackerCaloPos_noRadialFieldRand",cutstring,"goff")
    t.Draw("station:(decayVertexPosY - (time - decayTime)*299.79*decayVertexMomY/TMath::Sqrt(decayVertexMomZ**2 + decayVertexMomY**2 + decayVertexMomZ**2)):testfunc(time)/1000.>>trackerCaloPos_noRadialFieldRand",cutstring,"goff")


    saveToRootFile("./data/tracksOnly_"+file, [h_trackerBeamPos, h_trackerCaloPos, 
                                                h_trackerBeamPosRand, h_trackerCaloPosRand, 
                                                h_trackerCaloPos_noRadialField,h_trackerCaloPos_noRadialFieldRand])



def clusters(name, f, file):
    print(f, name)
    f.cd(name)
    f.ls()

    clusters13 = f.Get(name+"/clusters13")
    randclusters13 = f.Get(name+"/randclusters13")
    clusters19 = f.Get(name+"/clusters19")
    randclusters19 = f.Get(name+"/randclusters19")

    histstosave = [clusters13, randclusters13, clusters19, randclusters19]
    for h in histstosave:
        h.SetDirectory(0)

    saveToRootFile("./data/clustersOnly_"+file, histstosave)


if __name__ == "__main__":
    main()