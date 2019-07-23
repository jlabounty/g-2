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

    #13 parameter fit + changing omega_cbo
    def blinded_wiggle_changing_cbo(self, x, p):
        norm     = p[0]
        life     = p[1]
        asym     = p[2]
        R        = p[3]
        phi      = p[4]
        A1       = p[5]
        A2       = p[6]
        A3       = p[7]
        lifeCBO  = p[8]
        #omegaCBO = p[9]
        phiCBO1  = p[10]
        phiCBO2  = p[11]
        phiCBO3  = p[12]
        
        time  = x[0]
        omega = self.getBlinded.paramToFreq(R)

        if( "tracker" in self.cboFrequencyModel ):
            omegaCBO = self.getModel_ChangingCBOFrequency(self.cboFrequencyModel, 
                                        time, [ p[9], p[13], p[14], p[15], p[16], p[17] ] )
        elif( "elba" == self.cboFrequencyModel):
            omegaCBO = self.getModel_ChangingCBOFrequency(self.cboFrequencyModel, 
                                        time, [ p[9], p[14], p[15], p[16], p[17] ] ) #p13 unused in elba model
        elif( "elbaFixed" in self.cboFrequencyModel):
            omegaCBO = self.getModel_ChangingCBOFrequency(self.cboFrequencyModel, 
                                        time, [ p[9] ] ) #p13 - p17 unused in fixed elba model
        else:
            raise ValueError("ERROR: cboFrequencyModel is poorly defined")
        
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
        
        if( "elbaFixed" in self.cboFrequencyModel):
            omegaCBO = self.getModel_ChangingCBOFrequency(self.cboFrequencyModel, 
                                        time, [ p[9] ] ) #p13 - p17 unused in fixed elba model


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

        if( "elbaFixed" in self.cboFrequencyModel):
            omegaCBO = self.getModel_ChangingCBOFrequency(self.cboFrequencyModel, 
                                        time, [ p[9] ] ) #p13 - p17 unused in fixed elba model
        
        cCBO = 1-math.exp(-time/lifeCBO)*A1*math.cos(omegaCBO*time + phiCBO1)
        ACBO = asym * (1 - math.exp(-time/lifeCBO) * A2 * math.cos(omegaCBO*time + phiCBO2))
        phiCBO = phi + math.exp(-time/lifeCBO)*A3*math.cos(omegaCBO*time + phiCBO3)
        cVW = 1 - Avw*math.exp(-time/lifeVW)*math.cos(omegaVW*time + phiVW)

        if(self.KlossHist == None):
            raise AttributeError("ERROR: Kloss Histogram has not been initialized")
        
        return ( norm * math.exp(-time/life) * cCBO * cVW * (1 - ACBO*math.cos(omega*time + phiCBO)) 
                * (1 - Kloss*self.KlossHist.Interpolate(time)) )

    def getModel_ChangingCBOFrequency(self, whichModel, time, p):
        '''
            Function to select which model of the changing CBO frequency to use. p should be only the 
                subset of parameters which are necessary to execute this function, in order from left to right
            Input
                whichModel (str) : controls which model is returned
                time (double) : x value in the fit, time
                p (list of doubles) : parameters of the fit. not the same indexing as main fit.
        '''
        if self.cboFrequencyModel is None:
            raise ValueError("ERROR: Please set a model for omega_cbo")
        elif( self.cboFrequencyModel == "constant" ):
            omegaCBO = p[0]

        elif( self.cboFrequencyModel == "tracker" ): # docDB:15376
            omega_0 = p[0]
            deltaOmega = p[1] / 100. / 1000.
            A = p[2] / 100.
            tauA = p[3]
            B = p[4] / 100.
            tauB = p[5]
            omegaCBO = omega_0 * (1 + deltaOmega*time + A*math.exp(-time / tauA) + B*math.exp( -time / tauB ) )

        elif( self.cboFrequencyModel == "trackerFixed"):
            if(self.cboFrequencyParameters is None):
                raise ValueError("ERROR: self.cboFrequencyParameters not set. Please input parameters.")
            omega_0 = p[0]
            deltaOmega = self.cboFrequencyParameters[0]
            A = self.cboFrequencyParameters[1]
            tauA = self.cboFrequencyParameters[2]
            B = self.cboFrequencyParameters[3]
            tauB = self.cboFrequencyParameters[4]
            omegaCBO = omega_0 * (1 + deltaOmega*time + A*math.exp(-time / tauA) + B*math.exp( -time / tauB ) )

        elif( self.cboFrequencyModel == "elba"):
            cutoffTime = 1 # 1/t explodes at low values, cut off here to avoid math errors
            omega_0 = p[0]
            A = p[1] 
            tauA = p[2]
            B = p[3] 
            tauB = p[4]
            if( time > cutoffTime ):
                return omega_0 + A * math.exp(-time / tauA) / time + B * math.exp(-time / tauB) / time
            else:
                return ( omega_0 +  A * math.exp(-cutoffTime / tauA) / cutoffTime +
                                    B * math.exp(-cutoffTime / tauB) / cutoffTime )

        elif( self.cboFrequencyModel == "elbaFixed"):
            if(self.cboFrequencyParameters is None):
                print("Warning: self.cboFrequencyParameters not set. Using default parameters (station 18, 9d):")
                self.cboFrequencyParameters = [2.89, 79.2, 5.44, 9.2] #from Aaron's email, station 18 9day.
                print("    ", self.cboFrequencyParameters)
            cutoffTime = 1 # 1/t explodes at low values, cut off here to avoid math errors
            omega_0 = p[0]
            A = self.cboFrequencyParameters[0]
            tauA = self.cboFrequencyParameters[1]
            B = self.cboFrequencyParameters[2]
            tauB = self.cboFrequencyParameters[3]
            if( time > cutoffTime ):
                return omega_0 + A * math.exp(-time / tauA) / time + B * math.exp(-time / tauB) / time
            else:
                return ( omega_0 +  A * math.exp(-cutoffTime / tauA) / cutoffTime +
                                    B * math.exp(-cutoffTime / tauB) / cutoffTime )
        else:
            raise ValueError("ERROR: omega_cbo model is unknown")

        return omegaCBO

    def getModel_ChangingCBOAmplitude(self, whichModel, time, p):
        '''
            Function to select which model of the CBO envelope to use. p should be only the 
                subset of parameters which are necessary to execute this function, in order from left to right
            Input
                whichModel (str) : controls which model is returned
                time (double) : x value in the fit
                p (list of doubles) : parameters of the fit. not the same indexing as main fit.
        '''
        if self.cboAmplitudeModel is None:
            raise ValueError("ERROR: Please set a tracker model")
        elif( self.cboAmplitudeModel == "exponential" ): # docDB:15376
            lifetime = p[1]
            A = p[0]
            A_CBO = A*math.exp( -1*time / lifetime )
        elif( self.cboAmplitudeModel == "exponentialPlusConstant" ): # docDB:15376
            A = p[0]
            lifetime = p[1]
            C = p[2]
            A_CBO = A*math.exp( -1*time / lifetime ) + C
        elif( self.cboAmplitudeModel == "MikeS" ): # docDB:15376 / 11544
            A = p[0]
            lifetime = p[1]
            B = p[2]
            T = p[3]
            phi = p[4]

            A_CBO = A*math.exp( -1*time / lifetime )*( 1 + B*math.cos( 2*math.pi*time/T - phi ) )
        else:
            raise ValueError("ERROR: tracker model is unknown")

        return A_CBO

    #23-parameter function, adds changing cbo
    def blinded_wiggle_cbo_vw_Kloss_changingCBO(self, x, p):
        norm     = p[0]
        life     = p[1]
        asym     = p[2]
        R        = p[3]
        phi      = p[4]
        A1       = p[5]
        A2       = p[6]
        A3       = p[7]
        lifeCBO  = p[8]
        #changing cbo freq
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
        
        omegaCBO = self.getModel_ChangingCBOFrequency(self.cboFrequencyModel, 
                                    time, [ p[9], p[18], p[19], p[20], p[21], p[22] ])
        #omegaCBO = p[9] * (1 + p[18]*time + p[19]*math.exp(-time / p[20]) + p[21]*math.exp( -time / p[22] ) )
        
        cCBO = 1-math.exp(-time/lifeCBO)*A1*math.cos(omegaCBO*time + phiCBO1)
        ACBO = asym * (1 - math.exp(-time/lifeCBO) * A2 * math.cos(omegaCBO*time + phiCBO2))
        phiCBO = phi + math.exp(-time/lifeCBO)*A3*math.cos(omegaCBO*time + phiCBO3)
        cVW = 1 - Avw*math.exp(-time/lifeVW)*math.cos(omegaVW*time + phiVW)
        
        return ( norm * math.exp(-time/life) * cCBO * cVW * (1 - ACBO*math.cos(omega*time + phiCBO)) 
                * (1 - Kloss*self.KlossHist.Interpolate(time)) )

    def defineCustomFunction(self, x, p):
        '''
            Function which returns the results of evaluating the self.customFunction string.
            Must be written in the form: p[0]*x[0] + p[1] ... 
            Must be written with x -> x[0] (like all pyroot functions)
            Must be written pythonically (i.e.  TMath::Pi() -> r.TMath.Pi() )
        '''
        return eval( self.customFunction )
    
    def __init__(self, blindingPhrase, kind, customFunction = None):
        self.getBlinded = Blinders(FitType.Omega_a, str(blindingPhrase))

        self.KlossHist = None
        self.funcDict = {   "5par"  : self.five_parameter, 
                            "13par" : self.blinded_wiggle_cbo,
                            "13par_changing" : self.blinded_wiggle_changing_cbo,
                            "17par" : self.blinded_wiggle_cbo_vw,
                            "18par" : self.blinded_wiggle_cbo_vw_Kloss,
                            "23par" : self.blinded_wiggle_cbo_vw_Kloss_changingCBO,
                            "custom": self.defineCustomFunction
                         }

        self.cboAmplitudeModel = None
        self.cboFrequencyModel = None
        self.cboFrequencyParameters = None
        self.isCBOFree = True
        self.customFunction = customFunction
        
        if kind in self.funcDict.keys():
            self.kind = kind
        else:
            raise ValueError("ERROR: Function corresponding to "+str(kind)+" not found.")
    
    def __call__(self, x, p):
        return (self.getFunc())(x, p)

class BuildTF1:
    '''
        Class which takes as input a WiggleFit object and uses it to construct a TF1 with the correct 
        parameters / parameter names
        Takes the following inputs:
            func (WiggleFit): the function to fit
            nPar (int): number of parameters
            kind (str): the kind of function (somewhat redundant, but one could imagine having multiple functions with 
                the same nPar)
            name (str): the to give the function
            fitLow (double): the lower bound of the function
            fitHigh (double): the upper bound of the function
    '''
    
    def __init__(self, func, nPar, kind, name, fitLow, fitHigh):
        if(func.kind != kind):
            raise ValueError("The kind of function being defined here does not match: "+str(kind)+" (new) vs. "+(func.kind))
        self.f = r.TF1(name, func, fitLow, fitHigh, nPar)
        self.f.SetNpx(10000)
        self.nPar = nPar
        self.name = name
        self.fitLow = fitLow
        self.fitHigh = fitHigh
        self.funcRaw = func
        self.kind = kind
        self.nameDict = {   "5par" : ["N", "#tau_{#mu}", "A","R","#phi_{a}"],
                            "13par": ['N', '#tau', 'A', 'R', '#phi', 'A_{CBO - N}', 'A_{CBO - A}', 'A_{CBO - #phi}', '#tau_{CBO}', '#omega_{CBO}', '#phi_{CBO - N}', '#phi_{CBO - A}', '#phi_{CBO - #phi}'],
                            "13par_changing": ['N', '#tau', 'A', 'R', '#phi', 'A_{CBO - N}', 'A_{CBO - A}', 'A_{CBO - #phi}', '#tau_{CBO}', '#omega_{CBO}', '#phi_{CBO - N}', '#phi_{CBO - A}', '#phi_{CBO - #phi}', "#delta#omega_{CBO}", "A_{CBO}", "#tau_{CBO - A}", "B_{CBO}", "#tau_{CBO - B}"],
                            "17par": ['N', '#tau', 'A', 'R', '#phi', 'A_{CBO - N}', 'A_{CBO - A}', 'A_{CBO - #phi}', '#tau_{CBO}', '#omega_{CBO}', '#phi_{CBO - N}', '#phi_{CBO - A}', '#phi_{CBO - #phi}', 'A_{VW}', '#tau_{VW}', '#omega_{VW}', '#phi_{VW}'],
                            "18par": ['N', '#tau', 'A', 'R', '#phi', 'A_{CBO - N}', 'A_{CBO - A}', 'A_{CBO - #phi}', '#tau_{CBO}', '#omega_{CBO}', '#phi_{CBO - N}', '#phi_{CBO - A}', '#phi_{CBO - #phi}', 'A_{VW}', '#tau_{VW}', '#omega_{VW}', '#phi_{VW}', "K_{loss}"],
                            "23par": ['N', '#tau', 'A', 'R', '#phi', 'A_{CBO - N}', 'A_{CBO - A}', 'A_{CBO - #phi}', '#tau_{CBO}', '#omega_{CBO}', '#phi_{CBO - N}', '#phi_{CBO - A}', '#phi_{CBO - #phi}', 'A_{VW}', '#tau_{VW}', '#omega_{VW}', '#phi_{VW}', "K_{loss}", "#delta#omega_{CBO}", "A_{CBO}", "#tau_{CBO - A}", "B_{CBO}", "#tau_{CBO - B}"]
                         }
        
    '''
        Set the parameters of the fit.
        Inputs:
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
    def SetDumbParameters(self, par = 1):
        for i in range(self.nPar):
            self.f.SetParameter(i, par)
            self.initialParameters[i] = par
            
    def SetParameter(self, i, par):
        if(i > self.nPar - 1):
            raise ValueError("This parameter number is outside the range")
        else:
            self.f.SetParameter(i, par)
            self.initialParameters[i] = par
            
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

    def ImportParameters(self, prevFunc):
        if(self.nPar < prevFunc.GetNpar() ):
            raise ValueError("Parameters do not match")
        for i in range(prevFunc.GetNpar()):
            self.f.SetParameter(i, prevFunc.GetParameter(i) )

class WiggleFitter():
    '''
        Fits the histogram with the included options any number of times. 
        Stores intermediate parameters and chi2 values.
        Inputs:
            hist (TH1)
            fit (TF1 or BuildTF1)
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
        self.h.SetDirectory(0)
        self.f = None
        if("ROOT.TF1" in str(type(fit))):
            self.f = r.TF1(fit)
        else:
            self.f = r.TF1(fit.f)
        self.f.AddToGlobalList()
        self.name = name+"_fitter"
        self.f.SetName(self.name)
        self.nPar = self.f.GetNpar()
        self.fitOptions = fitOptions
        self.nFit = nFit
        try:
            self.fitLow = fit.fitLow
            self.fitHigh = fit.fitHigh
        except:
            self.fitLow = 0
            self.fitHigh =  -1
            print("ERROR: could not set fit bounds automatically. Please set self.fitLow / self.fitHigh.")

        self.intermediateParameters = []
        self.intermediateErrors = []
        self.intermediateChi2 = []

        self.pt = r.TPaveText(.7,.2,.95,0.95,"brNDC")
        self.pt.SetLabel("Parameters Text Box")
        
        self.resid = None
        self.fft = None

    def StoreIntermediateParameters(self, pars, parErrs, chi2):
        self.intermediateParameters.append(pars)
        self.intermediateErrors.append(parErrs)
        self.intermediateChi2.append(chi2)

    def PrintParameters(self):
        print("Parameters from this fit: ")
        if( self.f.GetNDF() != 0):
            print("     ChiSq/NDF = ", self.f.GetChisquare(), "/", self.f.GetNDF(),"=", self.f.GetChisquare() / self.f.GetNDF())
        for i in range(self.nPar):
            print("     ", self.f.GetParName(i), " = ", self.f.GetParameter(i), "+/-", self.f.GetParError(i) )

    def DumpParameters(self):
        return [ (self.f.GetParameter(i), self.f.GetParError(i)) for i in range(self.nPar) ]

    def DumpChiSquare(self):
        return [ self.f.GetChisquare(), self.f.GetNDF() ]

    def FixParameter(self, par, value = None):
        if(value is None):
            self.f.FixParameter(par, self.f.GetParameter(par))
        else:
            self.f.FixParameter(par, value)

    def SetParLimits(self, par, limLow, limHigh):
        self.f.SetParLimit(par, limLow, limHigh)

    def Fit(self, verbosity = 0, nFiti = None ):
        if(nFiti is not None):
            self.nFit = nFiti
        for i in range(self.nFit):
            if(verbosity > 0):
                print("Starting fit", i+1, "/", self.nFit)
                self.h.Fit(self.f, self.fitOptions)
            else:
                self.h.Fit(self.f, self.fitOptions+"Q")
            parametersi = [ self.f.GetParameter(x) for x in range( self.nPar ) ]
            parErrsi = [ self.f.GetParError(x) for x in range( self.nPar ) ]
            if(self.f.GetNDF() > 0):
                self.StoreIntermediateParameters( parametersi, parErrsi, self.f.GetChisquare() / self.f.GetNDF() )
            else:
                self.StoreIntermediateParameters( parametersi, parErrsi, np.nan )
            if(verbosity > 0):
                self.PrintParameters()

        self.ComputeResiduals()
        #self.ComputeFFT(self.fitLow, self.fitHigh)

    def ComputeResiduals(self):
        self.resid = self.h.Clone("h_resid_"+self.name)
        self.resid.SetTitle("Residuals")
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

    def DrawFFT(self, freqs = None, freqNames = None):
        '''
            Draws the FFT on a root canvas along with various Frequency lines.
            Input:
                frequencies (array of float): input array of floats which are drawn on the canvas and added to the legend
                freqNames (array of str): Names of said frequencies for those settings. If None, will not be added
            Output:
                TCanvas containing histograms
        '''
        if(self.fft is None):
            self.ComputeFFT()

        c = r.TCanvas("c","c",1200,500)
        self.fft.Draw("hist")
        
        yMin = 0.01 #self.fft.GetYaxis().GetXmin()
        yMax = self.fft.GetMaximum()*1.1 #self.fft.GetYaxis().GetXmax()

        if(freqs is not None):
            self.freqLines = []
            if(len(freqs) > 0):
                for i, freq in enumerate(freqs):
                    #print(freq, yMin, yMax)
                    fi = r.TLine(freq, yMin, freq, yMax)
                    fi.SetLineColor(i+1)
                    fi.SetLineStyle(8)
                    fi.Draw("SAME")
                    self.freqLines.append(fi)
            #print(self.freqLines)
            
            self.leg = r.TLegend(0.7,0.6,0.9,0.9)
            for i, fi in enumerate(self.freqLines):
                #print(fi)
                fi.Draw()
                if(len(freqNames) == len(freqs)):
                    self.leg.AddEntry(fi, freqNames[i]+" = "+str(round(freqs[i], 3)), "l")
                else:
                    self.leg.AddEntry(fi, "Frequency "+str(i+1)+" = "+str(round(freqs[i], 3)),"l")
            self.leg.Draw()

        c.Modified()
        c.Update()
        c.Draw()
        
        return c


    def Draw(self, t1 = None, t2 = None):

        c = r.TCanvas("c","c",1000,700)
        #c.Divide(1,2)

        c.cd(0)
        p1 = r.TPad("p1","p1",0,0.4,1,1)
        p1.Draw()
        p1.cd()

        if(t1 == None or t2 == None):
            t1 = self.fitLow
            t2 = self.fitHigh
        self.h.GetXaxis().SetRangeUser(t1,t2)
        self.h.SetStats(False)
        self.h.Draw("hist e")
        self.f.Draw("SAME")

        self.FillParametersBox()
        self.pt.Draw()
        p1.Draw()
        
        r.gPad.SetLogy()
        r.gPad.SetGrid()

        
        c.cd(0)
        p2 = r.TPad("p2","p2",0,0,1,0.4)
        p2.Draw()
        p2.cd()
        if(self.resid == None):
            self.ComputeResiduals()
        self.resid.SetStats(False)
        self.resid.Draw()
        self.resid.GetXaxis().SetRangeUser(t1,t2)

        #r.gPad.SetLogy()
        r.gPad.SetGrid()

        c.Modified()
        c.Update()
        c.Draw()

        return c

    def ReturnParameters(self):
        pars = []
        for i in range(self.nPar):
            pars.append( (self.f.GetParameter(i), self.f.GetParError(i)) )
        return pars

    def FillParametersBox(self):
        self.pt.Clear()
        self.pt.SetTextAlign(11)
        self.pt.AddText("ChiSq / NDF = "+str(self.f.GetChisquare())+" / "+str(self.f.GetNDF()))
        if(self.f.GetNDF() != 0 ):
            self.pt.AddText("            = "+str(self.f.GetChisquare() / self.f.GetNDF() ) )
        for i in range(self.nPar):
            texti = ( self.f.GetParName(i)+" = "+
                    '{:0.5e}'.format( self.f.GetParameter(i) )+" #pm "+
                    '{:0.5e}'.format( self.f.GetParError(i) ) )
            self.pt.AddText( texti )
        


class MakeWiggleFromTH3:
    '''
        From the TH3 of Energy vs. Time vs. Calo, create a TH1 which will be passed to the fitter
    '''
    def __init__(self, h3, elow, ehigh, caloNum = 0, timeScaleFactor = 1 , isPileupCorrected = False, 
                                 BinOrEnergy = "energy" ):
        # dont save th3 for memory reasons
        self.elow = elow
        self.ehigh = ehigh
        self.timeScaleFactor = timeScaleFactor
        self.caloNum = caloNum
        self.isPileupCorrected = isPileupCorrected
        self.BinOrEnergy = BinOrEnergy

        h3.GetXaxis().UnZoom()
        if(BinOrEnergy == "energy"):
            h3.GetYaxis().SetRangeUser(elow, ehigh)
            self.title = "Wiggle Plot for ["+str(elow)+" < E (MeV) < "+str(ehigh)+"] in Calo "+str(caloNum)
        elif(BinOrEnergy == "bin"):
            h3.GetYaxis().SetRange(elow, ehigh)
            self.title = "Wiggle Plot for ["+str(elow)+" < E (Bin) < "+str(ehigh)+"] in Calo "+str(caloNum)
        else:
            raise ValueError("BinOrEnergy has an unsupported value")

        if(caloNum == 0):
            h3.GetZaxis().UnZoom()
        elif(caloNum > 24 or caloNum < 0):
            raise ValueError("Calo Number is outside allowed range")
        else:
            caloBin = h3.GetZaxis().FindBin(caloNum)
            h3.GetZaxis().SetRange(caloBin,caloBin)

        self.h = h3.Project3D("x").Clone("wiggle_"+str(elow)+"_"+str(ehigh)+"_"+str(caloNum))
        self.h.SetTitle(self.title)

class MakeWiggleFromTH2:
    '''
        From the TH2 of Energy vs. Time, create a TH1 which will be passed to the fitter
    '''
    def __init__(self, h3, elow, ehigh, caloNum = 0, timeScaleFactor = 1 , isPileupCorrected = False, 
                                 BinOrEnergy = "energy" ):
        # dont save th3 for memory reasons
        self.elow = elow
        self.ehigh = ehigh
        self.timeScaleFactor = timeScaleFactor
        self.caloNum = caloNum
        self.isPileupCorrected = isPileupCorrected
        self.BinOrEnergy = BinOrEnergy

        self.ebinlow = h3.GetYaxis().FindBin( self.elow )
        self.ebinhigh = h3.GetYaxis().FindBin( self.ehigh )

        h3.GetXaxis().UnZoom()
        if(BinOrEnergy == "energy"):
            h3.GetYaxis().SetRangeUser(elow, ehigh)
            self.title = "Wiggle Plot for ["+str(elow)+" < E (MeV) < "+str(ehigh)+"] in Calo "+str(caloNum)
        elif(BinOrEnergy == "bin"):
            h3.GetYaxis().SetRange(elow, ehigh)
            self.title = "Wiggle Plot for ["+str(elow)+" < E (Bin) < "+str(ehigh)+"] in Calo "+str(caloNum)
        else:
            raise ValueError("BinOrEnergy has an unsupported value")

        if(caloNum > 24 or caloNum < 0):
            raise ValueError("Calo Number is outside allowed range")

        self.h = h3.ProjectionX("", self.ebinlow, self.ebinhigh).Clone("wiggle_"+str(elow)+"_"+str(ehigh)+"_"+str(caloNum))
        self.h.SetTitle(self.title)

class MakeWiggleFromTH1:
    '''
        From the TH1 of Energy vs. Time, create a TH1 which will be passed to the fitter
    '''
    def __init__(self, h3, elow, ehigh, caloNum = 0, timeScaleFactor = 1 , isPileupCorrected = False, 
                                 BinOrEnergy = "energy" ):
        # dont save th3 for memory reasons
        self.elow = elow
        self.ehigh = ehigh
        self.timeScaleFactor = timeScaleFactor
        self.caloNum = caloNum
        self.isPileupCorrected = isPileupCorrected
        self.BinOrEnergy = BinOrEnergy

        #self.ebinlow = h3.GetYaxis().FindBin( self.elow )
        #self.ebinhigh = h3.GetYaxis().FindBin( self.ehigh )

        h3.GetXaxis().UnZoom()
        if(BinOrEnergy == "energy"):
            self.title = "Wiggle Plot for ["+str(elow)+" < E (MeV) < "+str(ehigh)+"] in Calo "+str(caloNum)
        elif(BinOrEnergy == "bin"):
            self.title = "Wiggle Plot for ["+str(elow)+" < E (Bin) < "+str(ehigh)+"] in Calo "+str(caloNum)
        else:
            raise ValueError("BinOrEnergy has an unsupported value")

        self.h = h3.Clone("wiggle_"+str(elow)+"_"+str(ehigh)+"_"+str(caloNum))
        self.h.SetTitle(self.title)

# performs a fourier transform on the residuals from a plot.
def fourierXformWiggle( wigglePlot, inputFit, fitBoundLow, fitBoundHigh, title ):
    '''
        Computes fourier transform of a given histogram within the given bounds
    '''
    try:
        fitFunction = r.TF1(inputFit)
        fitFunction.Eval(10)
    except:
        raise ValueError("Error: Unable to clone/evaluate input fit function")

    c3 = r.TCanvas()
    residualsFull_5Param = wigglePlot.Clone() 
    nBins = residualsFull_5Param.GetSize() - 2 #total number of bins excluding over/underflow
    #print(nBins)
    residVec = []
    for i in range(nBins):
        binCenterX = wigglePlot.GetXaxis().GetBinCenter(i)
        if (binCenterX > fitBoundLow and binCenterX < fitBoundHigh):
            residVec.append( (binCenterX, wigglePlot.GetBinContent(i) - fitFunction.Eval(binCenterX) ) )
            #residualsFull_5Param.SetBinContent(i, wigglePlot.GetBinContent(i) - fitFunction.Eval(binCenterX))
        else:
            residualsFull_5Param.SetBinContent(i, 0)

    #print(len(residVec),[residVec[i] for i in range(5)])
    centers, bins = zip(*residVec)
    htest = r.TH1D("htest","htest",len(residVec),centers[0],centers[len(residVec)-1])
    for i,ding in enumerate(bins):
        htest.SetBinContent(i, ding)

    #residualsFull_5Param.Delete()
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
    #print(Npart, capT, minBinCenter, maxBinCenter)
    deltaT = capT/Npart #microseconds
    #deltaF = 1/capT
    #print(deltaT, deltaF)

    deltaTns = deltaT*1000 #nanoseconds
    limmaxHz = (1/(deltaTns*math.pow(10.0,-9)))
    limmaxMHz = limmaxHz / math.pow(10.0,6)

    #limmax = 2*deltaF*Npart #400-25
    #print(limmax,limmaxMHz)
    #hxform.GetXaxis().SetLimits(0,limmax)
    #nbins = residualsFull_5Param.GetSize() - 2
    hxform.SetBins(Npart,0,limmaxMHz)
    hxform.GetXaxis().SetRangeUser(0,limmaxMHz/2)
    #hxform.GetXaxis().SetRangeUser(0,1.4)

    #c2.SetLogy()
    #c2.Draw()
    #c2.Print("./images/FullIslands_5ParamResiduals.png")
    #c2.Print("./images/FullIslands_5ParamResiduals.root")
    
    return hxform


def InitializeWiggleFitterFromFile( fileName ):
    '''
        Function to take a wiggle 
    '''