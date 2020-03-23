from fit_util import *
from omega_a_fitting import *
import matplotlib.pyplot as plt
import uncertainties

class EnergyThresholdScan:
    '''
        Class to perform various energy threshold scans and to compute the optimal parameters
        Inputs:
            energy vs. time vs. calo plot (TH3)
            binOrEnergy (str) : whether to count in bins or energy
            eLow (double/int) : low point in energy scan
            eHigh (double/int): high point in energy scan
            
        Outputs: 
            Parameters from each fit
            Parameter errors from each fit

        Creates:
            Plot of the error in any parameter vs. the bin center
    '''

    def __init__(self, h, eLow, eHigh, deltaE, binOrEnergy = "energy", caloNum = 0, upperOrLower = "lower", verbosity = 0, nFit = 1, nAxes = 3):
        self.h = h.Clone()
        self.eLow = eLow
        self.eHigh = eHigh
        self.deltaE = deltaE
        self.calo = caloNum
        self.initialParameters = None
        self.inflectionPoint = [None for x in range(5)]
        self.nFit = nFit

        self.eBinLow = h.GetYaxis().FindBin(self.eLow)
        self.eBinHigh = h.GetYaxis().FindBin(self.eHigh)
        self.nAxes = nAxes
        if(nAxes > 2):
            self.caloBin = h.GetZaxis().FindBin(self.calo)

        self.binOrEnergy = binOrEnergy
        self.upperOrLower = upperOrLower
        self.verbosity = verbosity

        if( binOrEnergy != "energy"):
            raise ValueError("Error: bin specification not yet implemented")

        self.parameters = []
        self.parErrors = []

        self.GetWhichBins()

        if(self.verbosity > 0):
            print("Looping over bins: ")
        for ebin in self.whichBins:
            if(self.verbosity > 0):
                print("    Starting bin", ebin)
            if(self.upperOrLower == "lower"):
                parsi = self.DoWiggleFit(ebin, self.eBinHigh)
            elif(self.upperOrLower == "upper"):
                parsi = self.DoWiggleFit(self.eBinLow, ebin)
            else:
                raise ValueError("ERROR: select upper or lower energy scan")
            
            pi, pei = zip( *parsi )
            self.parameters.append(pi)
            self.parErrors.append(pei)

    def DoWiggleFit(self, e1_bin, e2_bin):
        if(self.nAxes > 2):
            wiggle = MakeWiggleFromTH3(self.h, e1_bin, e2_bin, self.calo, 1, False, "bin")
        elif(self.nAxes == 2):
            wiggle = MakeWiggleFromTH2(self.h, e1_bin, e2_bin, self.calo, 1, False, "bin")
        if(self.verbosity > 0):
            DumpClass(wiggle)
        
        fitFunc = WiggleFit(GetBlindingPhrase("./blinding.txt"), "5par")
        
        fit = BuildTF1(fitFunc, 5, "5par", "five_parameter_fit", 30, 650)
        if(self.initialParameters is None):
            fit.SetParameters([8926203,64.434,0.34402,-48., 1.5])
        else:
            fit.SetParameters(self.initialParameters)
        fit.SetParNames()

        self.parNames = ( [x for x in fit.nameDict['5par'] ] )
        
        fitter = WiggleFitter(wiggle.h, fit, "5par", "REMBQ", self.nFit)
        fitter.Fit( self.verbosity )

        return fitter.ReturnParameters()

    def GetWhichBins(self):
        self.energyBinCenters = []
        self.energyBinLowerBounds = []
        self.whichBins = []
        self.whichBinEnergies = []

        for i in range(self.h.GetNbinsY()+1):
            self.energyBinCenters.append( self.h.GetYaxis().GetBinCenter(i) )
            boundi = self.h.GetYaxis().GetBinCenter(i) - self.h.GetYaxis().GetBinWidth(i)/2.0
            if(self.upperOrLower == "lower" ):
                if((boundi >= self.eLow - self.deltaE) and (boundi <= self.eLow + self.deltaE)):
                    self.whichBins.append(i)
                    self.whichBinEnergies.append( self.h.GetYaxis().GetBinCenter(i) )
            elif(self.upperOrLower == "upper" ):
                if((boundi >= self.eHigh - self.deltaE) and (boundi <= self.eHigh + self.deltaE)):
                    self.whichBins.append(i)
                    self.whichBinEnergies.append( self.h.GetYaxis().GetBinCenter(i) )
            else:
                raise ValueError("ERROR: upperOrLower is not well defined")
            self.energyBinLowerBounds.append( boundi )

        if(self.verbosity > 0):
            print("Bins to loop over: ", self.whichBins)

    def PlotParameterVsBin(self, i, title = None):
        pars = [ self.parameters[x][i] for x in range(len(self.parameters))]
        parErrs = [ self.parErrors[x][i] for x in range(len(self.parameters))]

        fig, ax = plt.subplots(1,2, figsize=(15,5) )
        if(title is None):
            plt.suptitle("Parameter Scan: "+self.parNames[i] , y=1.01, size=18)
        else:
            plt.suptitle(title , y=1.01, size=18)

        inflectionPoint = self.GetInflectionPoint(i)
        func = inflectionPoint[2]

        ax[0].errorbar( self.whichBinEnergies, pars, yerr = parErrs, fmt=".:" )
        ax[0].set_title(self.parNames[i])
        ax[0].set_xlabel("Energy [MeV]")
        ax[0].set_ylabel(self.parNames[i])
        ax[0].grid()

        ax[1].set_title(r"$\delta$ "+self.parNames[i])
        ax[1].plot( self.whichBinEnergies, parErrs, ".", label="Minimum: "+str(inflectionPoint[0])+" +/-"+str(inflectionPoint[1]))
        ax[1].plot( func[0], func[1], "-", label="Fitted Function")
        ax[1].grid()
        
        plt.legend()
        plt.tight_layout()
        plt.show()

    def GetInflectionPoint(self, i, parOrError = 1, func = "pol2", nPar = 3):
        '''
            Helper function to get the quadratic (or other function) inflection point of the given parameter
            parOrError: 0 for parameter, 1 for parameter error
        '''
        if(parOrError == 0):
            pars = [ self.parameters[x][i] for x in range(len(self.parameters))]
        elif(parOrError == 1):
            pars = [ self.parErrors[x][i] for x in range(len(self.parameters))]
        else:
            raise ValueError("parOrError outside of allowed range")

        gr = r.TGraph()
        for j in range(len(pars)):
            gr.SetPoint(j, self.whichBinEnergies[j], pars[j])
        fit = r.TF1("fit",func)
        for fiti in range(2):
            gr.Fit(fit,"")

        quadPars = [fit.GetParameter(x) for x in range(nPar)]
        quadErrs = [fit.GetParError(x) for x in range(nPar)]

        if(func == "pol2"):
            p1 = uncertainties.ufloat( quadPars[1], quadErrs[1] )
            p2 = uncertainties.ufloat( quadPars[2], quadErrs[2] )
            if(p2 != 0):
                self.inflectionPoint[i] = -1*p1 / (2*p2)
            else:
                return((0,0,[]))
            
            return (self.inflectionPoint[i].n, self.inflectionPoint[i].s, 
                    TF1toPython(fit, self.whichBinEnergies[0], self.whichBinEnergies[len(pars) - 1]))
        else:
            print("Unable to calculate inflection point for this function. Returning raw parameters instead.")
            return (quadPars, quadErrs, TF1toPython(fit, self.whichBinEnergies[0], self.whichBinEnergies[len(pars) - 1]))