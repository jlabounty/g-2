import matplotlib.pyplot as plt
import numpy as np
from omega_a_fitting import *
import math

class TimeScan():
    
    '''
        Class which performs a start time scan over the given histogram for the given function
        Inputs:
            h (TH1): wigle histogram to be fit
            WiggleFit (WiggleFit): a function from the WiggleFit class
            tLow, tHigh (float): time bounds for the scan
            initialParamaters (list of floats): initial parameters to set the wiggle fit with
    '''    
    def __init__(self, fitter, h, tLow, tHigh, nScans, tFixed, initialParameters, nPar = 5, functionName="5par", startOrEnd = "start"):
        self.fitter = fitter
        self.h = h.Clone("StartTimeScanHist")
        self.h.SetDirectory(0)
        self.tLow = tLow
        self.tHigh = tHigh
        self.nScans = nScans
        self.tFixed = tFixed
        self.initialParameters = initialParameters
        self.StartOrEnd = startOrEnd
        self.nPar = nPar
        self.functionName = functionName
        self.nFits = 2

        self.parameters = []
        self.parErrors = []
        self.chiSquare = []
        self.timesScanned = []
        self.fixedParameters = []

        self.previousBin = -1
        
        self.verbosity = 0
        
    def BuildFitter(self, timei):
        if(self.StartOrEnd == "start"):
            fit = BuildTF1(self.fitter, self.nPar, self.functionName, "startTimeScan", timei , self.tFixed)
        elif(self.StartOrEnd == "end"):
            fit = BuildTF1(self.fitter, self.nPar, self.functionName, "endTimeScan", self.tFixed, timei)
        else:
            raise ValueError("ERROR: start or end is not properly defined")
            
        fit.SetParameters(self.initialParameters)
        fit.SetParNames()
        self.parameterNames = [fit.f.GetParName(i) for i in range(self.nPar)]
        for (par,value) in self.fixedParameters:
            if(value is None):
                fit.f.FixParameter(par, fit.f.GetParameter(par))
            else:
                fit.f.FixParameter(par, value)
            
        return fit

    def FixParameters(self, par, value = None):
        '''
            Function to add a parameter to the list of parameters to fix. If value = None, then the parameter 
                will be fixed to its current value
        '''
        self.fixedParameters.append( (par, value) )


    def DoScan(self):
        if(self.verbosity > 0):
            print("Performing time scan with bounds:", self.tLow, self.tHigh,"in", self.nScans,"steps")
            
        exactTimes = np.linspace(self.tLow, self.tHigh, self.nScans)
        binnedTimes = []
        binWidth = self.h.GetXaxis().GetBinWidth(2)
        for t in exactTimes:
            bini = self.h.GetXaxis().FindBin( t )
            if(bini == self.previousBin):
                continue
            self.previousBin = bini
            binCenter = self.h.GetXaxis().GetBinCenter(bini)
            binnedTimes.append( binCenter - binWidth )

        if(self.verbosity > 0):
            print("Times: ", binnedTimes)
            
        for timei in binnedTimes:
            if(self.verbosity > 0):
                print("Starting time scan at time:", timei)
            #create a fitter with the relevant parameters
            
            fit = self.BuildFitter(timei)
            
            fitter = WiggleFitter(self.h, fit, "StartTimeScan", "REMB", self.nFits)
            
            #fit the histogram
            fitter.Fit( self.verbosity )
            
            #extract the parameters and append to self.[] variables
            parsi = fitter.DumpParameters()
            pi, pei = zip(*parsi)
            self.parameters.append( list(pi) )
            self.parErrors.append( list(pei) )
            self.timesScanned.append( timei )
            self.chiSquare.append( list( (fitter.f.GetChisquare(), fitter.f.GetNDF()) ) )
        
    def PlotStartTimeScan(self, par, name):
        pars = [x[par] for x in self.parameters]
        parErrs = [x[par] for x in self.parErrors]
        
        band = self.ComputeKawallBand(par)
        
        fig,ax = plt.subplots(figsize=(15,5))
        plt.errorbar(self.timesScanned, pars, yerr=parErrs, fmt="o")
        plt.fill_between(self.timesScanned, 
                         [pars[0] + band[i] for i,x in enumerate(self.timesScanned)], 
                         [pars[0] - band[i] for i,x in enumerate(self.timesScanned)],
                         alpha = 0.3)
        plt.title(str(name), size=18)
        plt.xlabel("time of "+self.StartOrEnd+" time scan [microseconds]")
        plt.ylabel("Parameter Value")
        plt.grid()
        plt.show()
        
    
    def ComputeKawallBand(self, par):
        '''
            Computes the Kawall band according to aarons thesis equation 6.16: sigma^2_k = sigma^2_scan - sigma^2_initial
            Inputs:
                Parameter number (int): parameter for which to compute the Kawall band
            Outputs:
                kBand (list of floats) : list giving the allowed \pm 1 \sigma values of each point in the start time scan
        '''
        
        kBand = []
        initialErr = self.parErrors[0][par]
        
        for i in range( len(self.timesScanned) ):
            thisErr = self.parErrors[i][par]
            sigmai = math.sqrt( math.pow(thisErr, 2) - math.pow(initialErr, 2)  )
            kBand.append(thisErr)
        
        return kBand