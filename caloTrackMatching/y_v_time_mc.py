import ROOT as r 
from numba import jit
import numpy as np

@jit
def randomizeTimes( x, p=[None] ):
    inputtime = x[0]
    time = inputtime
    
    w0 = 2.6094;
    A = 2.80;
    tauA = 56.6;
    B = 6.18;
    tauB = 6.32;
    
    wCBO =  (w0 - (A/(tauA)) * r.TMath.Exp(-time/(1000.0*tauA)) - (B/(tauB)) * r.TMath.Exp(-time/(tauB*1000.0)) ); #MHz
    wa =  r.TMath.TwoPi() * 0.2291; #MHZ
    wc =  r.TMath.TwoPi() / 0.14919; #MHz

    factor = 1.0;
    wY = factor * (wCBO) * r.TMath.Sqrt( (2 * wc / (factor * wCBO)) -1.0 ) ;
    wVW = wc - (2.0 * wY);

    TCBO = r.TMath.TwoPi() / wCBO;
    Ta = r.TMath.TwoPi() / wa;
    TVW = r.TMath.TwoPi() / wVW;
    TY = r.TMath.TwoPi() / wY;
    T_diff= r.TMath.TwoPi()/(wCBO-wa);
    
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


def main():
    print("Starting...")

    ytau = 7
    xtau = 64.4


    def f_rand(x, p):
        randtime = randomizeTimes([x[0]])
        #print(x[0], randtime)
        #newx = [randtime, x[1]]
        #return f_nonRand(newx,p)

        t = x[0]
        y = x[1]
        
        return (p[0]*((3-y) - r.TMath.Exp(-t/p[1]))**2 + p[2])*r.TMath.Exp(-randtime/p[3])

    f2 = r.TF2("func2",f_rand,0,100,0,6,4)
    f2.SetParameters(-1,ytau,10,xtau)
    print(f2)


    
    '''
    h = r.TH2D("h","Random y's vs. Times", 100,0,100,60,0,6)
    h.FillRandom("func2",10)

    c = r.TCanvas()
    h.Draw("colz")
    c.Draw()

    fout = r.TFile("./randhist.root","RECREATE")
    h.Write()
    fout.Close()
    '''

if __name__ == "__main__":
    main()