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
            elif(isinstance(item, int) or isinstance(item, float) or isinstance(item, list)):
                self.CreateBranchFloat( key, item, t )
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

            else:
                print("Type not supported", type(item) )

                
        t.Fill()
        
        self.file.cd()
        self.file.Write()
        self.file.Close()
        
    def CreateBranchFloat( self, key, item, t ):
        from array import array
        length = 0
        if(isinstance(item, list)):
            length = len(item)
            if(isinstance(item[0], list)):
                for i in range(len(item)):
                    self.CreateBranchFloat( key+"_"+str(i), item[i], t )
                return
            
        ni = array( 'f', [ 0 for x in range(length+1) ] )
        if(length > 0):
            for i in range(length):
                ni[i] = item[i]
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

