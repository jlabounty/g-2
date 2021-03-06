def DumpClass( item ):
    ''' 
        Dump the contents of a class in a more readable way. 
    '''
    try:
        print("Dumping: ", item)
        print("Class: ", type(item))
        ding = vars(item)
        #print(ding)
        for var in ding:
            print("   ", var, "=", ding[var])
    except:
        print("Unable to dump members of this class")

def GetBlindingPhrase( file ):
    '''
        simple util to get the first line of a file and return as string for use as a blinding phrase
    '''
    with open(file) as f:
        content = f.readlines()
        phrase = content[0].strip()
    return str(phrase)

class SaveToRootFile():
    '''
        Utility to save all compatable items of a class as a root file.
        Input:
            toSave (any class): will loop over the items in the class and determine which ones can be saved
            name (str): prefix of the output file.
        Output:
            A .root file with objects stored as 
    '''
    
    verbosity = 0

    def __init__(self, toSave, name = "ExportedClass", addTime = True):  
        import ROOT as r  
        import datetime
        from array import array
        import os

        time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        if(addTime):
            fileName = name+"_"+str(time)+".root"
        else:
            fileName = name+".root"

        try:
            os.remove(fileName)
        except:
            if(self.verbosity > 0):
                print("No file to remove")

        print("Saving class", toSave, " to file ", fileName)

        self.toSave = toSave
        self.fileName = fileName
        
        self.file = r.TFile(fileName,"NEW")
        self.file.cd()
        
        t = r.TTree("t","Variable Tree")
        
        self.arrs = []
        self.arrCounter = 0

        dic = vars(toSave)
        self.items = []
        for key in dic:
            self.items.append( dic[key] )

        self.keys = [ x for x in dic ]
        if(self.verbosity > 0):
            print("Keys: ", self.keys)

        for i, key in enumerate(self.keys):
            item = self.items[i]
            if(self.verbosity > 0):
                print(key, item)

            if(item is None):
                #do nothing
                continue

            elif(isinstance(item, int) or isinstance(item, float)):
                self.CreateBranchFloat( key, item, t )
                #r.gROOT.cd()

            elif( isinstance(item, list) ):
                if( len(item) > 0 ):
                    #loop and get type of the most nested element of list
                    depth = self.depth(item)
                    #print(depth)
                    isFloatOrInt = "item"
                    for i in range(depth):
                        isFloatOrInt += "[0]"
                    itemNested = eval(isFloatOrInt)
                    #print(itemNested)
                    #if most nested element is a int/float, then create a branch
                    if(isinstance(itemNested, int) or isinstance(itemNested, float)):
                        self.CreateBranchFloat( key, item, t )
                    elif( isinstance(item[0], str) ):
                        for i, itemi in enumerate(item):
                            stri = r.TNamed(key+"_"+str(i),itemi)
                            stri.Write()
                    else:
                        print("This type of list is not supported:", item)
                #r.gROOT.cd()

            elif( isinstance(item, str) ):
                #strings
                stri = r.TNamed(key,item)
                stri.Write()

            elif( "ROOT.TH1" in (str(type(item)))  ):
                #dic[key].SetDirectory(0)
                dic[key].SetDirectory(self.file)
                self.file.cd()

                hi = eval("self.toSave."+key)
                hi.SetDirectory(0)
                hi.Write()
                self.file.Write()
                
            elif( "ROOT.TH2" in (str(type(item))) ):
                #print("Have to handle TH2's seperately...")
                hi2 = self.CopyTH2(toSave, key)
                hi2.SetDirectory(self.file)
                self.file.Write()

            elif( "ROOT.TF1" in (str(type(item))) ):
                f1 = dic[key]
                f1.Write()

            elif( "ROOT.TPaveText" in (str(type(item))) ):
                p1 = dic[key]
                p1.Write()

            else:
                print("Type not supported", type(item) )

                
        t.Fill()
        
        self.file.cd()
        self.file.Write()
        self.file.Close()

    def depth(self, l):
        if isinstance(l, list):
            return 1 + max(self.depth(item) for item in l)
        else:
            return 0
        
    def CreateBranchFloat( self, key, item, t ):
        from array import array
        length = 0
        if(isinstance(item, list)):
            length = len(item)
            if(length == 0):
                return
            else:
                #print(length, item)
                if( isinstance(item[0], list) ):
                    for i in range(len(item)):
                        self.CreateBranchFloat( key+"_"+str(i), item[i], t )
                    return
            
        ni = array( 'f', [ 0 for x in range(length+1) ] )
        if(length > 0):
            for i in range(length):
                #print(ni, list(item)[i])
                ni[i] = list(item)[i]
        else:
            ni[0] = item
            
        self.arrs.append( ni )
        i = len(self.arrs) - 1
        if(length == 0):
            keystring = key+"/F"
        else:
            keystring = key+"["+str(length)+"]/F"
        t.Branch(key, self.arrs[i], keystring)
        #r.gROOT.cd()

    def GetHistogramClone(self, toSave, key):
        hi = eval("self.toSave."+str(key))
        #print(hi.GetNbinsX(), hi.GetXaxis().GetXmin() )
        #print(hi.GetBinContent(2,2))
        return hi

    def CopyTH2(self, toSave, key):
        import ROOT as r
        hi = eval("self.toSave."+str(key))
        if( "ROOT.TH2" not in str(type(hi)) ):
            raise ValueError("ERROR: This is not a TH2")
        Naxes = 2
        axes = []
        for axis in range(Naxes):
            axi = ( GetAxis(axis, hi).GetNbins(), GetAxis(axis, hi).GetXmin(), GetAxis(axis, hi).GetXmax()  )
            axes.append( axi )

        h2 = r.TH2D(key, hi.GetTitle(), axes[0][0], axes[0][1], axes[0][2], axes[1][0], axes[1][1], axes[1][2] )
        for binx in range(axes[0][0]+1):
            for biny in range(axes[1][0]+1):
                h2.SetBinContent(binx, biny, hi.GetBinContent(binx,biny))
                h2.SetBinError(binx, biny, hi.GetBinError(binx,biny))

        #print(axes)
        
        #h2 = "ding"
        return h2

def GetAxis(n,h):
    if(n == 0):
        return h.GetXaxis()
    elif(n == 1):
        return h.GetYaxis()
    elif(n == 2):
        return h.GetZaxis()
    else:
        raise ValueError("Axis out of range")


def TF1toPython(func, xmin, xmax, nbins = 1000):
    '''
        returns array of points in x and y to be plotted in matplotlib
    '''
    import ROOT as r
    import numpy as np

    if( "ROOT.TF1" not in str(type(func))):
        raise TypeError("ERROR: func is not of type TF1")
    xs = []
    ys = []
    for xi in np.linspace(xmin, xmax, nbins):
        xs.append(xi)
        ys.append( func.Eval(xi) )

    return (xs, ys)

def TF2toPython(func, xmin, xmax, ymin, ymax, nbins = 1000):
    '''
        returns array of points in x and y to be plotted in matplotlib
    '''
    import ROOT as r
    import numpy as np

    if( "ROOT.TF2" not in str(type(func))):
        raise TypeError("ERROR: func is not of type TF2")
    xs = []
    ys = []
    zs = []
    for xi in np.linspace(xmin, xmax, nbins):
        for yi in np.linspace(ymin, ymax, nbins):
            xs.append(xi)
            ys.append(yi)
            zs.append( func.Eval(xi, yi) )

    return (xs, ys, zs)

def CompareFitParameters( fs, width = 6, names = None, verbosity = 0):
    '''
        Function which takes as input 1+ TF1's and compares their parameter values. 
        If they do not have the same number of parameters, then the lower value will be looped over (for comparing 18 vs. 5 par values)
    '''
    import ROOT as r
    import numpy as np
    import math
    import matplotlib.pyplot as plt 
    
    f1 = fs[0]
    ns = [x.GetNpar() for x in fs]
    if(names is None):
        names = ["f"+str(i) for i in range(len(ns))]
        
    npar = min(ns)
    
    #width = 6
    height = int(np.ceil( npar / width ) )

    fig, ax = plt.subplots(height, width, figsize=(width*5,height*4))
    for i in range(npar):
        valsi = [ (f1.GetParameter(i), f1.GetParError(i)) for f1 in fs]
        if(verbosity > 0):
            print(f1.GetParName(i)," ---- ", [x for x in valsi] )
        axi = ax[int(np.floor(i / width))][i % width]

        titlei = f1.GetParName(i)
        if("phi" in f1.GetParName(i)[:5]):
            pars = [x[0] % 2*math.pi for x in valsi]
            titlei += " [Modulo 2 pi]"
        else:
            pars = [x[0] for x in valsi]
        parErrs = [x[1] for x in valsi]

        axi.errorbar( [x for x in range(len(pars))], pars, xerr=0, yerr=parErrs, fmt="o")
        axi.set_title(titlei)
        plt.sca(axi)
        plt.grid()
        plt.xticks(np.arange(len(ns)), names)

    plt.suptitle("Comparison of Fit Parameters", y=1.01, size=18)
    plt.tight_layout()
    plt.show()

def InvertTH1(h, title = None, color = 38, alpha = 0.3, scaleFactor = -1):
    '''
        Utility function to simply invert a given TH1 and return the result. Also changes the color.
        Inputs:
            h (TH1): histogram to be inverted
            title (str): optional, title of new hist
            color (int): optional, color of new hist
    '''
    h2 = h.Clone()
    h2.SetDirectory(0)

    for i in range(h2.GetNbinsX()+1):
        h2.SetBinContent(i, h.GetBinContent(i)*(scaleFactor))

    if(title is not None):
        h2.SetTitle(title)
    else:
        h2.SetTitle(h.GetTitle()+" [Inverse]")

    h2.SetLineColor(color)
    h2.SetFillColorAlpha(color, alpha)

    return h2
