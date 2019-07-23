from omega_a_fitting import *
from fit_util import *
import matplotlib.pyplot as plt
import uncertainties
import ROOT as r
import numpy as np

class PileupMultiplierScan():
    '''
        Class which takes an uncorrected histogram and a pileup histogram and scans over the parameter space of each multiplier
        Inputs:
            Uncorrected histogram (TH2)
            Double pileup histogram (TH2)
            Triple pileup histogram (TH2)
            Initial Pileup multiplier value(s) (float)
            MultLow (float): 
            MultHigh (float)
            NumberOfScans (int)
        Outputs:
            Scan showing the Parameter values/errors for various pilup multiplier values
              
    '''
    
    def __init__(self, Ninitial, DoubleHist, doubleMultInitial, TripleHist = None, tripleMultInitial = None):
        self.Ninitial = Ninitial.Clone("Ninitial")
        self.DoubleHist = DoubleHist.Clone("DoublesUnscaled")
        self.doubleMultInitial = doubleMultInitial
        if(TripleHist is not None):
            self.TripleHist = TripleHist.Clone("TriplesUnscaled")
        else:
            self.TripleHist = None
        self.tripleMultInitial = tripleMultInitial
        
        self.eLow = 1700
        self.eHigh = 6000
        
        self.nFit = 1
        
        self.initialParameters = None
        self.parameters = []
        self.parErrors = []
        self.multipliers = []
        self.chiSq = []
        
        self.verbosity = 2
        self.fitter = None
        
        self.ffts = []
        
        
    def InitializeFitter(self, fitLow = 30., fitHigh = 650.):
        self.fitLow = fitLow
        self.fitHigh = fitHigh
        
        fitFunc = WiggleFit(GetBlindingPhrase("./blinding.txt"), "5par")
        self.fitter = BuildTF1(fitFunc, 5, "5par", "five_parameter_fit", 30, 650)
        
        
    def GetFitter(self):
        if(self.fitter is None):
            self.InitializeFitter()
        
        return self.fitter
        
        
    def DoScan(self, MultLow, MultHigh, NumberOfScans):
        
        self.eBinLow = self.Ninitial.GetYaxis().FindBin(self.eLow)
        self.eBinHigh = self.Ninitial.GetYaxis().FindBin(self.eHigh)
        
        doubleMult = []
        tripleMult = []
        
        for x in np.linspace(MultLow, MultHigh, NumberOfScans):
            doubleMult.append(x)
            if(self.TripleHist is not None):
                tripleMult.append(x)
            else:
                tripleMult = [1]
        print(doubleMult, tripleMult)
        
        nScans = len(doubleMult) * len(tripleMult)
        scanCounter = 1
        
        for dM in doubleMult:
            for tM in tripleMult:
                print("Beginning scan point: ", dM, tM, "(", scanCounter,"/",nScans,")")
                scanCounter += 1
                self.multipliers.append( (dM, tM) )
                hi = self.Ninitial.Clone("hi")
                hdi = self.DoubleHist.Clone("hdi")
                hdi.Scale(dM*self.doubleMultInitial)
                if(self.TripleHist is not None):
                    hti = self.TripleHist.Clone("hti")
                    hti.Scale(tM*self.tripleMultInitial)
                    hi.Add(hti, -1)
                hi.Add(hdi, -1)
                
                hi_x = hi.ProjectionX("", self.eBinLow, self.eBinHigh).Clone("hi_x")
                fit = self.GetFitter()
                
                if(self.initialParameters is None):
                    fit.SetParameters([8926203,64.434,0.34402,-38,5.15])
                else:
                    fit.SetParameters(self.initialParameters)
                fit.SetParNames()

                self.parNames = ( [x for x in fit.nameDict['5par'] ] )

                fitter = WiggleFitter(hi_x, fit, "5par", "REMBQ", self.nFit)
                fitter.Fit( self.verbosity )
                
                fitter.ComputeFFT()
                self.ffts.append( fitter.fft.Clone("fft_"+str(dM)+"_"+str(tM)))
                
                print(fitter.ReturnParameters())
                pi, pei = zip(*(fitter.ReturnParameters()))
                self.parameters.append(pi)
                self.parErrors.append(pei)
                self.chiSq.append( fitter.f.GetChisquare() / fitter.f.GetNDF() )
                
    def SinglePointGetWiggle(self, dM, tM):
        self.eBinLow = self.Ninitial.GetYaxis().FindBin(self.eLow)
        self.eBinHigh = self.Ninitial.GetYaxis().FindBin(self.eHigh)
        print("Beginning scan point: ", dM, tM)
        self.multipliers.append( (dM, tM) )
        hi = self.Ninitial.Clone("hi")
        hdi = self.DoubleHist.Clone("hdi")
        hdi.Scale(dM*self.doubleMultInitial)
        if(self.TripleHist is not None):
            hti = self.TripleHist.Clone("hti")
            hti.Scale(tM*self.tripleMultInitial)
            hi.Add(hti, -1)
        hi.Add(hdi, -1)

        hi_x = hi.ProjectionX("", self.eBinLow, self.eBinHigh).Clone("hi_x")
        
        return hi_x 
                
    def PlotParameterVsDouble(self, i, title = None, mult = 0, chiSq = False):
        pars = [ self.parameters[x][i] for x in range(len(self.parameters))]
        parErrs = [ self.parErrors[x][i] for x in range(len(self.parameters))]
        
        #0 for double, 1 for triples
        mults = [ self.multipliers[x][mult] for x in range(len(self.parameters))]

        fig, ax = plt.subplots(1,2, figsize=(15,5) )
        if(title is None):
            plt.suptitle("Parameter Scan: "+self.parNames[i] , y=1.01, size=18)
        else:
            plt.suptitle(title , y=1.01, size=18)

        ax[0].errorbar( mults, pars, yerr = parErrs, fmt=".:" )
        ax[0].set_title(self.parNames[i])
        ax[0].set_xlabel("Pileup Multiplier")
        ax[0].set_ylabel(self.parNames[i])
        ax[0].grid()
        
        inflectionPoint = self.GetInflectionPoint(i, mults, chiSq)
        func = inflectionPoint[2]

        if(chiSq):
            ax[1].set_title(r"$\chi^{2}$")
            ax[1].plot( mults, self.chiSq, ".", label="Minimum: "+str(inflectionPoint[0])+" +/-"+str(inflectionPoint[1]))
            ax[1].plot( func[0], func[1], "-", label="Fitted Function")
            ax[1].grid()
        else:
            ax[1].set_title(r"$\delta$ "+self.parNames[i])
            ax[1].plot( mults, parErrs, ".", label="Minimum: "+str(inflectionPoint[0])+" +/-"+str(inflectionPoint[1]))
            ax[1].plot( func[0], func[1], "-", label="Fitted Function")
            ax[1].grid()
        
        plt.legend()
        plt.tight_layout()
        plt.show()
    
        
    def GetInflectionPoint(self, i, mults, chiSq = False, parOrError = 1, func = "pol2", nPar = 3):
        '''
            Helper function to get the quadratic (or other function) inflection point of the given parameter
            parOrError: 0 for parameter, 1 for parameter error
        '''
        if(chiSq):
            pars = [ self.chiSq[x] for x in range(len(self.parameters)) ]
        elif(parOrError == 0):
            pars = [ self.parameters[x][i] for x in range(len(self.parameters))]
        elif(parOrError == 1):
            pars = [ self.parErrors[x][i] for x in range(len(self.parameters))]
        else:
            raise ValueError("parOrError outside of allowed range")

        gr = r.TGraph()
        for j in range(len(pars)):
            gr.SetPoint(j, mults[j], pars[j])
        fit = r.TF1("fit",func)
        for fiti in range(2):
            gr.Fit(fit,"Q")

        quadPars = [fit.GetParameter(x) for x in range(nPar)]
        quadErrs = [fit.GetParError(x) for x in range(nPar)]

        if(func == "pol2"):
            p1 = uncertainties.ufloat( quadPars[1], quadErrs[1] )
            p2 = uncertainties.ufloat( quadPars[2], quadErrs[2] )
            inflectionPoint = -1*p1 / (2*p2)
            return (inflectionPoint.n, inflectionPoint.s, 
                    TF1toPython(fit, mults[0], mults[len(pars) - 1]))
        else:
            print("Unable to calculate inflection point for this function. Returning raw parameters instead.")
            return (quadPars, quadErrs, TF1toPython(fit, mults[0], mults[len(pars) - 1]))