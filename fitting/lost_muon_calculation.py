import ROOT as r 
import math
import numpy as np 
#g-2 Blinding Software
from BlindersPy3 import Blinders
from BlindersPy3 import FitType

# this will contain utilities which compute / store the lost muon distributions which can then be 
#   accessed by the fitter modules

class MuonLoss:
    '''
        A class to hold/compute the muon loss histogram. 
        Inputs:
            triples (th2)
            backwards triples (th2)
            caloNum (int): which calo to compute the correction for. 0 = all
            Muon lifetime (double)
            iteration (int) : how many times this has gone through the fitter
        Outputs:
            Muon loss function in histogram form (TH1)
    '''

    def __init__(self, triples, backwardsTriples, lifetime, iteration = 0, subtractBackwards = False, caloNum = 0):
        if(caloNum < 0 or caloNum > 24):
            raise ValueError("caloNum out of range")
        elif(caloNum > 0 and caloNum < 25):
            binY = triples.GetYaxis().FindBin(caloNum)
            triples.GetYaxis().SetRange(binY, binY)
            backwardsTriples.GetYaxis().SetRange(binY, binY)

        self.triples = triples.ProjectionX().Clone("triples")
        self.backwardsTriples = backwardsTriples.ProjectionX().Clone("b_triples")
        self.tau = lifetime
        self.subtractBackwards = subtractBackwards

        self.muonLossHist = None
        self.iteration = iteration

        self.ComputeLossFunction()

    def ComputeLossFunction(self):
        triplesX = self.triples.Clone("triplesX")
        if(self.subtractBackwards):
            triplesX.Add(self.backwardsTriples, -1)

        for i in range(1,triplesX.GetNbinsX()):
            binCenter = triplesX.GetBinCenter(i)
            triplesX.SetBinContent(i, triplesX.GetBinContent(i)*r.TMath.Exp(binCenter / self.tau))

        self.muonLossHist = self.triples.Clone("muonLossHist")
        self.muonLossHist.SetTitle(str(self.tau))

        for i in range(1,self.muonLossHist.GetNbinsX()+1):
            inti = triplesX.Integral(1,i)
            self.muonLossHist.SetBinContent(i, inti)