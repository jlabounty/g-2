import ROOT as r 
import math
import numpy as np 
#g-2 Blinding Software
from BlindersPy3 import Blinders
from BlindersPy3 import FitType

#this file will store the functions, parameters, their names, etc. for the various omega_a fitting functions

class WiggleFit:

    '''
       Class of function which creates a wiggle fit function to be passed into a TF1.
       Takes the following inputs:
           blindingPhrase (str): Blinding phrase used in the BlindersPy3 class
           kind (str): uses the dict implemented in this class to determine which form to use    
    '''
        
    def getFunc(self):
        return self.funcDict[self.kind]
        
    #5 parameter fit
    def five_parameter(self, x,p):
        norm  = p[0]
        life  = p[1]
        asym  = p[2]
        R     = p[3]
        phi   = p[4]

        time  = x[0]
        omega = self.getBlinded.paramToFreq(R)

        return norm * math.exp(-time/life) * (1 - asym*math.cos(omega*time + phi))

    #13 parameter fit
    def blinded_wiggle_cbo(self, x, p):
        norm     = p[0]
        life     = p[1]
        asym     = p[2]
        R        = p[3]
        phi      = p[4]
        A1       = p[5]
        A2       = p[6]
        A3       = p[7]
        lifeCBO  = p[8]
        omegaCBO = p[9]
        phiCBO1  = p[10]
        phiCBO2  = p[11]
        phiCBO3  = p[12]
        
        time  = x[0]
        omega = self.getBlinded.paramToFreq(R)
        
        cCBO = 1-math.exp(-time/lifeCBO)*A1*math.cos(omegaCBO*time + phiCBO1)
        ACBO = asym * (1 - math.exp(-time/lifeCBO) * A2 * math.cos(omegaCBO*time + phiCBO2))
        phiCBO = phi + math.exp(-time/lifeCBO)*A3*math.cos(omegaCBO*time + phiCBO3)
        
        return norm * math.exp(-time/life) * cCBO * (1 - ACBO*math.cos(omega*time + phiCBO))

    #17 parameter fit
    def blinded_wiggle_cbo_vw(self, x, p):
        norm     = p[0]
        life     = p[1]
        asym     = p[2]
        R        = p[3]
        phi      = p[4]
        A1       = p[5]
        A2       = p[6]
        A3       = p[7]
        lifeCBO  = p[8]
        omegaCBO = p[9]
        phiCBO1  = p[10]
        phiCBO2  = p[11]
        phiCBO3  = p[12]
        Avw      = p[13]
        lifeVW   = p[14]
        omegaVW  = p[15]
        phiVW    = p[16]
        
        time  = x[0]
        omega = self.getBlinded.paramToFreq(R)
        
        cCBO = 1-math.exp(-time/lifeCBO)*A1*math.cos(omegaCBO*time + phiCBO1)
        ACBO = asym * (1 - math.exp(-time/lifeCBO) * A2 * math.cos(omegaCBO*time + phiCBO2))
        phiCBO = phi + math.exp(-time/lifeCBO)*A3*math.cos(omegaCBO*time + phiCBO3)
        cVW = 1 - Avw*math.exp(-time/lifeVW)*math.cos(omegaVW*time + phiVW)
        
        return norm * math.exp(-time/life) * cCBO * cVW * (1 - ACBO*math.cos(omega*time + phiCBO))

    def initializeKloss(self, h):
        self.KlossHist = h.Clone("KlossHist")
        self.KlossHist.SetDirectory(0)

    #18 parameter fit. Kloss histogram will need to be initialized before this can be called
    def blinded_wiggle_cbo_vw_Kloss(self, x, p):
        norm     = p[0]
        life     = p[1]
        asym     = p[2]
        R        = p[3]
        phi      = p[4]
        A1       = p[5]
        A2       = p[6]
        A3       = p[7]
        lifeCBO  = p[8]
        omegaCBO = p[9]
        phiCBO1  = p[10]
        phiCBO2  = p[11]
        phiCBO3  = p[12]
        Avw      = p[13]
        lifeVW   = p[14]
        omegaVW  = p[15]
        phiVW    = p[16]
        Kloss    = p[17]
        
        time  = x[0]
        omega = self.getBlinded.paramToFreq(R)
        
        cCBO = 1-math.exp(-time/lifeCBO)*A1*math.cos(omegaCBO*time + phiCBO1)
        ACBO = asym * (1 - math.exp(-time/lifeCBO) * A2 * math.cos(omegaCBO*time + phiCBO2))
        phiCBO = phi + math.exp(-time/lifeCBO)*A3*math.cos(omegaCBO*time + phiCBO3)
        cVW = 1 - Avw*math.exp(-time/lifeVW)*math.cos(omegaVW*time + phiVW)

        if(self.KlossHist == None):
            raise AttributeError("ERROR: Kloss Histogram has not been initialized")
        
        return ( norm * math.exp(-time/life) * cCBO * cVW * (1 - ACBO*math.cos(omega*time + phiCBO)) 
                * (1 - Kloss*self.KlossHist.GetBinContent(self.KlossHist.FindBin(time))) )
    
    
    def __init__(self, blindingPhrase, kind):
        self.getBlinded = Blinders(FitType.Omega_a, str(blindingPhrase))

        self.KlossHist = None
        self.funcDict = {   "5par" : self.five_parameter, 
                            "13par" : self.blinded_wiggle_cbo,
                            "17par" : self.blinded_wiggle_cbo_vw,
                            "18par" : self.blinded_wiggle_cbo_vw_Kloss
                         }
        
        if kind in self.funcDict.keys():
            self.kind = kind
        else:
            raise ValueError("ERROR: Function corresponding to "+str(kind)+" not found.")
    
    def __call__(self, x, p):
        return (self.getFunc())(x, p)

class BuildTF1:
    '''
        Class which takes as input a WiggleFit object and uses it to construct a TF1 with the correct parameters / parameter names
        Takes the following inputs:
            func (WiggleFit): the function to fit
            nPar (int): number of parameters
            kind (str): the kind of function (somewhat redundant, but one could imagine having multiple functions with the same nPar)
            name (str): the to give the function
            fitLow (double): the lower bound of the function
            fitHigh (double): the upper bound of the function
    '''
    
    def __init__(self, func, nPar, kind, name, fitLow, fitHigh):
        if(func.kind != kind):
            raise ValueError("The kind of function being defined here does not match")
        self.f = r.TF1(name, func, fitLow, fitHigh, nPar)
        self.f.SetNpx(10000)
        self.nPar = nPar
        self.name = name
        self.fitLow = fitLow
        self.fitHigh = fitHigh
        self.funcRaw = func
        self.kind = kind
        self.nameDict = {   "5par" : ["N", "#tau_{#mu}", "A","R","#phi_{a}"],
                            "13par": ['N', '#tau', 'A', 'R', '#phi', 'A_{1}', 'A_{2}', 'A_{3}', '#tau_{CBO}', '#omega_{CBO}', '#phi_{CBO - 1}', '#phi_{CBO - 2}', '#phi_{CBO - 3}'],
                            "17par": ['N', '#tau', 'A', 'R', '#phi', 'A_{1}', 'A_{2}', 'A_{3}', '#tau_{CBO}', '#omega_{CBO}', '#phi_{CBO - 1}', '#phi_{CBO - 2}', '#phi_{CBO - 3}', 'A_{VW}', '#tau_{VW}', '#omega_{VW}', '#phi_{VW}'],
                            "18par": ['N', '#tau', 'A', 'R', '#phi', 'A_{1}', 'A_{2}', 'A_{3}', '#tau_{CBO}', '#omega_{CBO}', '#phi_{CBO - 1}', '#phi_{CBO - 2}', '#phi_{CBO - 3}', 'A_{VW}', '#tau_{VW}', '#omega_{VW}', '#phi_{VW}', "K_{loss}"]
                         }
        
    '''
        Set the parameters of the fit.
        Inputs:
            nPar: number of parameters
            parameters: list of parameter values
    '''
    def SetParameters(self, parameters):
        self.initialParameters = parameters
        if(len(parameters) == self.nPar):
            for i in range(self.nPar):
                self.f.SetParameter(i, parameters[i])
        else:
            raise ValueError("Number of parameters does not match initialzed value")
            
    #quickly initialize to avoid divide by zero errors
    def SetDumbParameters(self):
        for i in range(self.nPar):
            self.f.SetParameter(i, 1)
            
    def SetParameter(self, i, par):
        if(i > self.nPar - 1):
            raise ValueError("This parameter number is outside the range")
        else:
            self.f.SetParameter(i, par)
            
    def SetParLimits(self, i, lim1, lim2):
        if(i > self.nPar - 1):
            raise ValueError("This parameter number is outside the range")
        else:
            self.f.SetParLimits(i, lim1, lim2)
            
    def SetParNames(self, names = None):
        if(names == None): #use default names
            for i in range(self.nPar):
                self.f.SetParName(i, self.nameDict[self.kind][i])
        elif( len(names) != self.nPar ):
            raise ValueError("Number of names does not match initialzed number of parameters")
        else:
            for i in range(self.nPar):
                self.f.SetParName(i, names[i])

class WiggleFitter():
    '''
        Fits the histogram with the included options any number of times. Stores intermediate parameters and chi2 values.
        Inputs:
            hist (TH1)
            fit (TF1)
            fitOptions (str):
            nFit (int):
            name (str)
        Outputs/Stored Objects:
            residuals
            FFT of residuals
            intermediate fit parameters
    '''

    def __init__(self, hist, fit, name, fitOptions = "", nFit = 1):
        self.h = hist.Clone(name)
        self.f = r.TF1(fit.f)
        self.name = name+"_fitter"
        self.f.SetName(self.name)
        self.nPar = self.f.GetNpar()
        self.fitOptions = fitOptions
        self.nFit = nFit
        self.fitLow = fit.fitLow
        self.fitHigh = fit.fitHigh
        

        self.intermediateParameters = []
        self.intermediateChi2 = []

    def StoreIntermediateParameters(self, pars, chi2):
        self.intermediateParameters.append(pars)
        self.intermediateChi2.append(chi2)

    def PrintParameters(self):
        for i in range(self.nPar):
            print( self.f.GetParName(i), " = ", self.f.GetParameter(i), "+/-", self.f.GetParError(i) )

    def Fit(self, verbosity = 0):
        for i in range(self.nFit):
            self.h.Fit(self.f, self.fitOptions)
            parametersi = [ self.f.GetParameter(x) for x in range( self.nPar ) ]
            if(self.f.GetNDF() > 0):
                self.StoreIntermediateParameters( parametersi, self.f.GetChisquare() / self.f.GetNDF() )
            else:
                self.StoreIntermediateParameters( parametersi, np.nan )
            if(verbosity > 0):
                self.PrintParameters()

        self.ComputeResiduals()

    def ComputeResiduals(self):
        self.resid = self.h.Clone("h_resid_"+self.name)
        self.resid.Reset()
        for i in range(self.resid.GetNbinsX()):
            ri = self.h.GetBinContent(i) - self.f.Eval( self.h.GetBinCenter(i) )
            self.resid.SetBinContent(i, ri)

    def ComputeFFT(self, t1 = None, t2 = None):
        title = "FFT of Residuals of "+str(self.name)+" in range "+str(self.fitLow)+" < t < "+str(self.fitHigh) 
        if(t1 == None or t2 == None):
            self.fft = fourierXformWiggle( self.h, self.f, self.fitLow, self.fitHigh, title )
        else:
            self.fft = fourierXformWiggle( self.h, self.f, t1, t2, title )
        

# performs a fourier transform on the residuals from a plot.
def fourierXformWiggle( wigglePlot, fitFunction, fitBoundLow, fitBoundHigh, title ):
    '''
        Computes fourier transform of a given histogram within the given bounds
    '''
    c3 = r.TCanvas()
    residualsFull_5Param = wigglePlot.Clone() 
    nBins = residualsFull_5Param.GetSize() - 2 #total number of bins excluding over/underflow
    print(nBins)
    residVec = []
    for i in range(nBins):
        binCenterX = wigglePlot.GetXaxis().GetBinCenter(i)
        if (binCenterX > fitBoundLow and binCenterX < fitBoundHigh):
            residVec.append( (binCenterX, wigglePlot.GetBinContent(i) - fitFunction.Eval(binCenterX) ) )
            residualsFull_5Param.SetBinContent(i, wigglePlot.GetBinContent(i) - fitFunction.Eval(binCenterX))
        else:
            residualsFull_5Param.SetBinContent(i, 0)

    print(len(residVec),[residVec[i] for i in range(5)])
    centers, bins = zip(*residVec)
    htest = r.TH1D("htest","htest",len(residVec),centers[0],centers[len(residVec)-1])
    for i,ding in enumerate(bins):
        htest.SetBinContent(i, ding)

    residualsFull_5Param.Delete()
    residualsFull_5Param = htest
    nBins = residualsFull_5Param.GetSize() - 2 #total number of bins excluding over/underflow

    #apply a windows function to try to get rid of the imaginary peaks
    welchVec = []
    for i in range(nBins):
        unwindowed = residualsFull_5Param.GetBinContent(i)
        welch = 1 #- ( ( i - (nBins - 1) / 2) / ((nBins - 1) / 2) )**2
        welchVec.append(welch)
        residualsFull_5Param.SetBinContent(i, unwindowed *  welch)

    residualsFull_5Param.Draw()
    residualsFull_5Param.GetXaxis().SetRangeUser(30,700)
    residualsFull_5Param.SetTitle("(Windowed) Residuals of the Fit")
    c3.Draw()    

    hxform = r.TH1D()
    hxform = 0
    r.TVirtualFFT.SetTransform(0)
    hxform = residualsFull_5Param.FFT(hxform,"MAG P")
    hxform.SetTitle( title )
    #NOTE: for "real" frequencies you have to divide the x-axes range with the range of your function
    #    y-axes has to be rescaled by a factor of 1/SQRT(n) to be right: this is not done automatically!
    normXform = hxform.GetEntries()
    hxform.Scale(1/normXform)
    c2 = r.TCanvas()
    c2.cd()
    #c2.SetLogy()
    hxform.GetXaxis().SetTitle("Frequency (MHz)")
    hxform.GetYaxis().SetTitle("Arb. Units")
    hxform.Draw("HIST P0 L")
    #c2.Draw()

    Npart = residualsFull_5Param.GetSize() - 2
    minBinCenter = residualsFull_5Param.GetXaxis().GetBinCenter(0)
    maxBinCenter = residualsFull_5Param.GetXaxis().GetBinCenter(Npart)

    capT = maxBinCenter - minBinCenter
    print(Npart, capT, minBinCenter, maxBinCenter)
    deltaT = capT/Npart #microseconds
    deltaF = 1/capT
    print(deltaT, deltaF)

    deltaTns = deltaT*1000 #nanoseconds
    limmaxHz = (1/(deltaTns*math.pow(10.0,-9)))
    limmaxMHz = limmaxHz / math.pow(10.0,6)

    limmax = 2*deltaF*Npart #400-25
    print(limmax,limmaxMHz)
    #hxform.GetXaxis().SetLimits(0,limmax)
    nbins = residualsFull_5Param.GetSize() - 2
    hxform.SetBins(Npart,0,limmaxMHz)
    hxform.GetXaxis().SetRangeUser(0,limmaxMHz/2)
    #hxform.GetXaxis().SetRangeUser(0,1.4)

    #c2.SetLogy()
    #c2.Draw()
    #c2.Print("./images/FullIslands_5ParamResiduals.png")
    #c2.Print("./images/FullIslands_5ParamResiduals.root")
    
    return hxform;



