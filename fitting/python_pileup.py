spec = (
    ("verbosity",int32),
    ("deltat", float64),
    #('hpy', typeof(ding))
)


from functools import partial
from numba import prange


class PythonPileup:
    '''
        Reimplementation of the pileup correction algorithm from Aaron using numpy arrays, in order to boost speed.
            Inputs:
                h (TH2) : histogram to be pileup corrected
                name (str): name of the histogram
                iteration (int): how many times has this gone through the correction algorithm
            Outputs:
                Double/Triple pileup spectrum
    '''
    def __init__(self, h, name, iteration = 0, deltat = 2, verbosity = -1, tFitLow = 30):
        
        self.verbosity = verbosity
        #self.h = h.Clone("N_initial_"+str(iteration)+"_"+name)
        self.hpy = pyTH2(h)
        self.deltat = deltat
        #self.image, self.hpy = TH2ToNumpyArray(h)
    
    def __defaults__(self):
        return [None]
    
    def __getitem__(self, index):
        return [self.h, self.hpy][index]

    @staticmethod
    @njit(parallel=True)
    def rhoDoublePulse( E, t, hpy ):
        #timeBin = self.h.GetXaxis().FindBin( t )
        timeBin = hpy.findbin( t ) 

        h2 = hpy.contents[:,timeBin:timeBin+1]
        
        Nbins = len(h2)
            
        rho = float(0)
        for bin in prange(int(Nbins)):
            E2 = hpy.getbincenter(bin,1)
            #print("Energies:", E ,E2)
            if( E < E2 ):
                r1 = float(0.)
            else:
                bin2 = hpy.findbin( E - E2, 1 ) 
                #print(bin, bin2)
                r1 = h2[bin2][0]
                
            #print(bin, bin2, E, E2)
            r2 = h2[bin][0]
            rho += r1*r2
        
        return rho
    
    #@jit(nopython=True)
    def computeRhoDouble(self):
        #self.rhoDouble = self.h.Clone("h_rhoDouble_"+str(self.iteration)+"_"+self.name)
        self.rhoDouble = pyTH2(self.hpy)
        self.rhoDouble.clear_contents()

        nBinsX = int(self.rhoDouble.binsx -2)
        nBinsY = int(self.rhoDouble.binsy -2)
        
        self.rhoDouble.contents_overflow = self._computeRhoDouble(nBinsX, nBinsY, 
                                                                  self.hpy, self.rhoDoublePulse, 
                                                                  self.rhoDouble.contents_overflow )
        
    @staticmethod
    @njit(parallel=True)
    def _computeRhoDouble(nBinsX, nBinsY, hpy, rhoDoublePulse, rhoDouble ):

        print("Computing rho_double histogram")
        for binx in prange(int(nBinsX)):
            #print("    ", binx,"/",nBinsX+1)
            for biny in prange(int(nBinsY)):
                #print(biny)
                #Ei = self.rhoDouble.GetYaxis().GetBinCenter(biny)
                #ti = self.rhoDouble.GetXaxis().GetBinCenter(binx)
                Ei = float(hpy.getbincenter(biny, 1))
                ti = float(hpy.getbincenter(binx, 0))
                rhoi = float(rhoDoublePulse( Ei, ti, hpy ))
                
                #print(Ei, ti, rhoi)
                rhoDouble[biny+1][binx+1] = rhoi
        print("All done")
        return rhoDouble
        
        
        
        
    ''' and now to calculate the double pileup bin by bin '''
    @staticmethod
    @njit
    def _rhoDoublePileup(energyBin, timeBin, h_cont, rhoDouble_cont, deltat):
 
        #timeBin = self.hpy.findbin( t, 0 ) - 1
        #energyBin = self.hpy.findbin( E, 1 ) - 1
        #h2 = self.hpy.contents[:,timeBin:timeBin+1]
        integralN = np.sum(h_cont[:,timeBin:timeBin+1])
        
        rho = deltat * ( rhoDouble_cont[energyBin][timeBin] - 2*h_cont[energyBin][timeBin]*integralN )
        #print(rho, self.deltat , self.rhoDouble.contents[energyBin][timeBin],  - 2*self.hpy.contents[energyBin][timeBin], integralN )
        return rho

    ''' and now actually compute the double correction '''
    def ComputeDoubleCorrection( self ):
        self.doublePileup = pyTH2(self.hpy)
        self.doublePileup.clear_contents()
        
        nBinsX = self.doublePileup.binsx -2
        nBinsY = self.doublePileup.binsy -2
        
        self.doublePileup.contents_overflow =  self._ComputeDoubleCorrection(self.hpy.contents,
                                                                             self.rhoDouble.contents, nBinsX, nBinsY, self.deltat
                                                                            # self.doublePileup.contents_overflow 
                                                                             )
        
    @staticmethod
    @njit(parallel=True)
    def _ComputeDoubleCorrection(h_cont, rhoDouble_cont, nBinsX, nBinsY, deltat ):
        output = np.zeros( (h_cont.shape[0] +2, h_cont.shape[1] + 2) , dtype=np.float64)
        print("Computing double pileup correction")
        for binx in prange(int(nBinsX)):
            for biny in prange(int(nBinsY)):
                #rhoi = self.rhoDoublePileup(biny, binx, h_cont, rhoDouble_cont, deltat )
                integralN = np.sum(h_cont[:,binx:binx+1])
                rhoi = deltat * ( rhoDouble_cont[biny][binx] - 2*h_cont[biny][binx]*integralN )
                output[biny][binx] = rhoi
                
        return output
                
        
    @staticmethod
    @njit(parallel=True)
    def rhoTriplePileup(E, t, hpy, rhoDouble, deltat):
        timeBinN = hpy.findbin(t, 0) 
        energySliceN = hpy.contents[:,timeBinN:timeBinN+1]
        if np.sum(energySliceN) < 10**(-10):
            return 0.        
        timeBinRho = timeBinN
        energySliceRho = rhoDouble.contents[:,timeBinN:timeBinN+1]
        

        
        int1s = np.zeros(int(len(energySliceRho)),dtype=float64)
        if(len(energySliceRho) > 0.1):
            for bin1 in prange( int(len(energySliceRho)) ):
                Ed = float(hpy.centers(1)[ bin1 ])
                if( Ed > E ):
                    #print(Ed, E)
                    int1s[bin1] = 0.
                else:
                    #print(bin1, E, Ed, energySliceRho, energySliceN)
                    rho1 = energySliceN[ hpy.findbin( E - Ed, 1 ) ][0]
                    rho2 = energySliceRho[ hpy.findbin(Ed, 1)  ][0]
                    int1s[bin1] = rho1*rho2
                    #print(rho1,rho2)
                #print(int1)
        
        int1 = np.sum(int1s)
        int2 = np.sum(energySliceN)
        int3 = (int2)**2
        
        rhoDoubleEt = rhoDouble.contents[ rhoDouble.findbin(E, 1)  ][timeBinN]
        rhoEt = hpy.contents[ rhoDouble.findbin(E, 1)  ][timeBinN]
        
        if(t > 670):
            print(E, t, timeBinN, int1, int2, int3, rhoDoubleEt, rhoEt)
            print(energySliceN)
        
        return ((deltat)**2) * ( int1 - 3*rhoDoubleEt*int2 + 3*rhoEt*int3 )

    
    def ComputeTripleCorrection(self):
        self.triplePileup = pyTH2(self.hpy)
        self.triplePileup.clear_contents()
        
        nBinsX = self.triplePileup.binsx -2
        nBinsY = self.triplePileup.binsy -2
        
        self.triplePileup.contents_overflow = self._ComputeTripleCorrection(nBinsX, nBinsY, self.hpy, 
                                                                            self.doublePileup, self.deltat, 
                                                                            self.rhoTriplePileup )
    
    @staticmethod
    @njit(parallel=True)
    def _ComputeTripleCorrection(nBinsX, nBinsY, hpy, doublePileup, deltat, 
                                 rhoTriplePileup):

        print("Starting triple correction")
        output = np.zeros( (hpy.contents_overflow.shape[0], hpy.contents_overflow.shape[1]) , dtype=np.float64)
        for binx in prange(nBinsX):
            for biny in prange(nBinsY):
                #ti, Ei = self.triplePileup.centers_overflow[biny][binx]
                Ei = float(hpy.getbincenter(biny, 1))
                ti = float(hpy.getbincenter(binx, 0))
                
                #print(binx, biny, Ei, ti)
                rhoi = rhoTriplePileup(Ei, ti, hpy, doublePileup, deltat)
                #print(rhoi)
                output[biny+1][binx+1] = rhoi
                
        return output
                
    def fitPileup(self):
        return -1