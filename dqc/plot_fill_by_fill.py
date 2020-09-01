import ROOT as r
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def main():
    # filepath = "/pnfs/GM2/daq/run2/offline/gm2_5116A/runs_26000/26500/"
    # filepath = "/pnfs/GM2/daq/run2/offline/gm2_5116A/runs_26000/"
    filepath = "/pnfs/GM2/daq/run2/offline/gm2_5116A/runs_26000/"
    prefix = "gm2calo::FillByFillDQCArtRecord_dqcRecorder__caloReco.obj."
    cut = f"{prefix}runNum > 0"

    allFiles = []
    t = r.TChain("Events")
    for path in Path(filepath).rglob('*.root'):
        # print(path.name)
        # print(path, type(path))
        if("00.root" in path.name):
            t.Add(str(path))
            allFiles.append(str(path))
        # break
    # t.Print()
    print(allFiles)
    print(len(allFiles))

    # return -1

    c = r.TCanvas("c","c",1200,600)
    c.Divide(1,4)
    h = r.TH2I("h","Kicker DQC vs. Run/SubRun Number", (-26450+26625)*1000, 26450, 26625,
                                                        2,0,2)
    
    h2 = h.Clone("h2")
    h2.SetTitle("T0 DQC vs. Run/Subrun Number")

    h3 = h.Clone("h3")
    h3.SetTitle("Quad DQC vs. Run/Subrun Number")

    h4 = h.Clone("h3")
    h4.SetTitle("Pass All DQC vs. Run/Subrun Number")

    t.Draw(f"{prefix}pass_kicker:{prefix}runNum + {prefix}subRunNum/1000.>>h",cut,"goff")
    print("**************************************************************************")

    t.Draw(f"{prefix}pass_T0:{prefix}runNum + {prefix}subRunNum/1000.>>h2",cut,"goff")
    print("**************************************************************************")

    t.Draw(f"{prefix}pass_laser:{prefix}runNum + {prefix}subRunNum/1000.>>h3",cut,"goff")
    print("**************************************************************************")

    t.Draw(f"{prefix}pass_alldqc:{prefix}runNum + {prefix}subRunNum/1000.>>h4",cut,"goff")
    print("**************************************************************************")

    c.cd(1)
    h.Draw("colz")
    c.cd(2)
    h2.Draw("colz")
    c.cd(3)
    h3.Draw("colz")
    c.cd(4)
    h4.Draw("colz")

    # t.Draw(f"{prefix}pass_kicker:{prefix}bunchNum",cut,"colz")
    # t.Draw(f"{prefix}pass_T0:{prefix}eventNum",cut,"colz")

    c.Draw()

    c.Print("./Kicker_DQC_BySubrun_Run2E.root")
    c.Print("./Kicker_DQC_BySubrun_Run2E.png")



if __name__ == "__main__":
    main()

