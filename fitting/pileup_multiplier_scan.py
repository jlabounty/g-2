from omega_a_fitting import *
from fit_util import *
import matplotlib.pyplot as plt
import uncertainties
import ROOT as r
import numpy as np
import scipy.interpolate
from mpl_toolkits.axes_grid1 import make_axes_locatable

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
        
        
    def DoScan(self, MultLow, MultHigh, NumberOfScans, MultLowTriple = None, MultHighTriple = None, NumberOfScansTriple = None):
        
        self.eBinLow = self.Ninitial.GetYaxis().FindBin(self.eLow)
        self.eBinHigh = self.Ninitial.GetYaxis().FindBin(self.eHigh)
        self.multLow = MultLow
        self.multHigh = MultHigh
        self.NumberOfScans = NumberOfScans
        self.multLowTriple = MultLowTriple
        self.multHighTriple = MultHighTriple
        self.NumberOfScansTriple = NumberOfScansTriple
        
        doubleMult = []
        tripleMult = []
        
        for x in np.linspace(MultLow, MultHigh, NumberOfScans):
            doubleMult.append(x)
            if(self.TripleHist is not None):
                tripleMult.append(x)
            else:
                tripleMult = [1]

        if(self.multLowTriple is not None):
            tripleMult = []
            for x in np.linspace(MultLowTriple, MultHighTriple, NumberOfScansTriple):
                tripleMult.append(x)
        
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
                
    def SinglePointGetWiggle(self, dM, tM, th2 = False):
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
        
        if(th2):
            return hi
        else:
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
        if(mult == 0):
            ax[0].set_xlabel("Double Pileup Multiplier")
        elif(mult == 1):
            ax[0].set_xlabel("Triple Pileup Multiplier")
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

    def GetInflectionPoint2D(self, i = 3, chiSq = False, parOrError = 1):
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
            
        mults = [x for x in self.multipliers]
            
        nPar = 5
        gr = r.TGraph2D()
        for j in range(len(pars)):
            gr.SetPoint(j, mults[j][0], mults[j][1], pars[j])
        func = "[0] + [1]*x + [2]*x*x + [3]*y + [4]*y*y"
        fit = r.TF2("fit",func)
        for i in range(5):
            fit.SetParameter(i, 1)
        for fiti in range(2):
            gr.Fit(fit,"Q")
            
        quadPars = [fit.GetParameter(x) for x in range(nPar)]
        quadErrs = [fit.GetParError(x) for x in range(nPar)]
        
        p1 = uncertainties.ufloat( quadPars[1], quadErrs[1] )
        p2 = uncertainties.ufloat( quadPars[2], quadErrs[2] )
        p3 = uncertainties.ufloat( quadPars[3], quadErrs[3] )
        p4 = uncertainties.ufloat( quadPars[4], quadErrs[4] )
        
        inflectionPoint = ( -1*p1 / (2*p2) , -1*p3 / (2*p4) )
        print(inflectionPoint)
        return ( inflectionPoint , TF2toPython(fit, mults[0][0], mults[len(pars) - 1][0], mults[0][1], mults[len(pars) - 1][1]) )


def PlotPileupScan2D(self, i = 3, title = None, chiSq = False):
    print(self)
    pars = np.array( [ self.parameters[x][i] for x in range(len(self.parameters))] )
    parErrs = [ self.parErrors[x][i] for x in range(len(self.parameters))]

    multsDouble = np.array([ self.multipliers[x][0] for x in range(len(self.parameters))])
    multsTriple = np.array([ self.multipliers[x][1] for x in range(len(self.parameters))])
    
    xi, yi = np.linspace(multsDouble.min(), multsDouble.max(), 300), np.linspace(multsTriple.min(), multsTriple.max(), 300)
    xi, yi = np.meshgrid(xi, yi)
    zi = scipy.interpolate.griddata((multsDouble, multsTriple), pars, (xi, yi), method='linear')

    fig, ax = plt.subplots(1,2, figsize=(15,5) )
    if(title is None):
        plt.suptitle("Parameter Scan: "+self.parNames[i] , y=1.01, size=18)
    else:
        plt.suptitle(title , y=1.01, size=18)

    
    cmap = plt.cm.get_cmap('viridis')
    im = ax[0].imshow(zi, vmin=pars.min(), vmax=pars.max(), origin='lower',
                        extent=[multsDouble.min(), multsDouble.max(), multsTriple.min(), multsTriple.max()], 
                        cmap=cmap, interpolation='nearest', aspect='auto')
    ax[0].scatter(multsDouble, multsTriple, c = pars, cmap = cmap, edgecolors='black')
    
    ax[0].set_title(self.parNames[i])
    ax[0].set_xlabel("Double Pileup Multiplier")
    ax[0].set_ylabel("Triple Pileup Multiplier")
    ax[0].grid()
    plt.gca()
    divider = make_axes_locatable(ax[0])
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax, cmap = cmap)
    #plt.colorbar(im, ax = ax[0], cmap = cmap)
    
    #return

    inflectionPoint = self.GetInflectionPoint2D(i, chiSq)
    func = inflectionPoint[1]

    if(chiSq):        
        ax[1].set_title(r"$\chi^{2}$")
        zchi = scipy.interpolate.griddata((multsDouble, multsTriple), self.chiSq, (xi, yi), method='linear')

        #ax[1].plot( mults, self.chiSq, ".", label="Minimum: "+str(inflectionPoint[0])+" +/-"+str(inflectionPoint[1]))
        im2 = ax[1].imshow(zchi, vmin=min(self.chiSq), vmax=max(self.chiSq), origin='lower',
                           extent=[multsDouble.min(), multsDouble.max(), multsTriple.min(), multsTriple.max()],
                           cmap=cmap, interpolation='nearest', aspect='auto')
        ax[1].scatter(multsDouble, multsTriple, c = self.chiSq, cmap = cmap, edgecolors='black')

        #zfit = scipy.interpolate.griddata((func[0], func[1]), func[2], (xi, yi), method='linear')
        #ax[1].contour([xi, yi], zfit)
        
        labeli = "Inflection Point: (x,y) = ( "
        for x in inflectionPoint[0]:
            labeli += '{:.3u}'.format(x)
            labeli += ", "
        labeli = labeli[:-2]+")"
        #ax[1].plot([inflectionPoint[0][0].n],[inflectionPoint[0][1].n],"r*",label=labeli)
        ax[1].errorbar( [inflectionPoint[0][0].n],[inflectionPoint[0][1].n],
                        xerr=[inflectionPoint[0][0].s], yerr=[inflectionPoint[0][1].s],
                        fmt="r*",label=labeli)
        
        plt.gca()
        divider2 = make_axes_locatable(ax[1])
        cax2 = divider2.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im2, cax=cax2, cmap = cmap)
        
        #ax[1].plot( func[0], func[1], "-", label="Fitted Function")
        ax[1].grid()
        ax[1].legend()
        
    else:
        ax[1].set_title(r"$\delta$ "+self.parNames[i])

        zchi = scipy.interpolate.griddata((multsDouble, multsTriple), parErrs, (xi, yi), method='linear')

        #ax[1].plot( mults, self.chiSq, ".", label="Minimum: "+str(inflectionPoint[0])+" +/-"+str(inflectionPoint[1]))
        im2 = ax[1].imshow(zchi, vmin=min(parErrs), vmax=max(parErrs), origin='lower',
                           extent=[multsDouble.min(), multsDouble.max(), multsTriple.min(), multsTriple.max()], 
                           cmap=cmap, interpolation='nearest', aspect='auto')
        ax[1].scatter(multsDouble, multsTriple, c = parErrs, cmap = cmap, edgecolors='black')
        ax[1].set_aspect('auto')
    

        plt.gca()
        divider2 = make_axes_locatable(ax[1])
        cax2 = divider2.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax2, cmap = cmap)
        
        #ax[1].plot( func[0], func[1], "-", label="Fitted Function")
        ax[1].grid()

    #plt.legend()
    plt.tight_layout()
    plt.show()
    
    #plt.scatter(func[0], func[1], c=func[2])
    #plt.show()