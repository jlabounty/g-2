import numba
from numba import int32, float64    # import the types
from numba import *

import numpy as np
import ROOT as r
import matplotlib.colors as colors

import pickle
from functools import wraps, update_wrapper

import numpy as np
from numba import jitclass, int32, float64

class jitpickler: # https://stackoverflow.com/questions/49246021/serialization-of-numba-classes
    '''
    pickler
    '''
    def __init__(self, jitobj):
        self.__dict__['obj'] = jitobj
        self.__dict__['__module__'] = jitobj.__module__
        self.__dict__['__doc__'] = jitobj.__doc__

    def __getstate__(self):
        obj = self.__dict__['obj']
        typ = obj._numba_type_
        fields = typ.struct

        return typ.classname, {k: getattr(obj, k) for k in fields}

    def __setstate__(self, state):
        name, value = state
        cls = globals()[name]
        value['_decorator'] = False
        jitobj = cls(**value)
        self.__init__(jitobj)

    def __getattr__(self, attr):
        return getattr(self.__dict__['obj'], attr)

    def __setattr__(self, attr, value):
        return setattr(self.__dict__['obj'], attr, value)

    def __delattr__(self, attr):
        return delattr(self.__dict__['obj'], attr)

def jitpickle(cls):
    decoratorkw = '_decorator'
    @wraps(cls)
    def decorator(*args, **kwargs):
        if kwargs.get(decoratorkw, True):
            kwargs.pop(decoratorkw, None)
            return jitpickler(cls(*args, **kwargs))
        else:
            kwargs.pop(decoratorkw, None)
            return cls(*args, **kwargs)
    return decorator


def fillPyTH2fromRoot(h, hpy):
    
    hpy.binsx = h.GetNbinsX()+2
    hpy.binsy = h.GetNbinsY()+2
    
    #print(np.array([h.GetXaxis().GetBinWidth(1),h.GetYaxis().GetBinWidth(1)]))
    hpy.binwidth = np.array([h.GetXaxis().GetBinWidth(1),h.GetYaxis().GetBinWidth(1)], dtype=np.float64)
    
    hpy.rangex = np.array([h.GetXaxis().GetBinCenter(1) - hpy.binwidth[0]/2.0 , 
                   h.GetXaxis().GetBinCenter(hpy.binsx - 1) - hpy.binwidth[0]/2.0 ], dtype=np.float64)
    hpy.rangey = np.array([h.GetYaxis().GetBinCenter(1) - hpy.binwidth[1]/2.0 , 
                   h.GetYaxis().GetBinCenter(hpy.binsy - 1) - hpy.binwidth[1]/2.0], dtype=np.float64)
    
    
    hpy.edgesx = np.array([h.GetXaxis().GetBinLowEdge(x) for x in range(hpy.binsx)], dtype=np.float64)
    hpy.edgesy = np.array([h.GetYaxis().GetBinLowEdge(x) for x in range(hpy.binsy)], dtype=np.float64)
    
    #print(hpy.binsx, hpy.binsy)
    hpy.contents_overflow = np.zeros((hpy.binsy, hpy.binsx), dtype=np.float64)
    hpy.errors_overflow = np.zeros((hpy.binsy, hpy.binsx), dtype=np.float64)

    hpy.centers_overflow = np.zeros((hpy.binsy, hpy.binsx,2), dtype=np.float64)

    #hpy.contents = hpy.contents_overflow[1:-1,1:-1]
    #hpy.erorrs = hpy.errors_overflow[1:-1,1:-1]
    
    for i in range( hpy.binsx ):
        for j in range( hpy.binsy ):
            content = h.GetBinContent(i, j)
            if(np.abs(content) > 10**(-15) ):
                hpy.contents_overflow[j][i] = content
                if(content - hpy.contents_overflow[j][i] > 0.1):
                    print("ERROR", content, content - hpy.contents_overflow[j][i] , i, j)
                    hpy.contents_overflow[j][i] -= ( content - hpy.contents_overflow[j][i] )
                hpy.errors_overflow[j][i] = h.GetBinError(i,j)
                hpy.centers_overflow[j][i][:] = (hpy.edgesx[i], hpy.edgesy[j])
    

spec1 = (
        ('binsx', int32),
        ('binsy' , int32),
        ('binwidth', float64[:]),
        ('rangex' ,float64[:]),
        ('rangey' , float64[:]),
        ('edgesx' , float64[:]),
        ('edgesy' , float64[:]),
        ('contents_overflow' , float64[:,:]),
        ('errors_overflow' , float64[:,:]),
        #('erorrs' , float64[:,:]),
        #('contents' , float64[:,:]),
        ('centers_overflow' , float64[:,:,:])
)


#@jitpickle 
@jitclass(spec = spec1)
class pyTH2():
    
    def __init__(self,h=None, binsxi=None, binrangexi=None, binsyi=None, binrangeyi=None):
        '''
            Class which holds a TH2 object in a python array
        '''
        
        #if("ROOT" in str(type(h))):
        #    self._fromRoot(h)
        #print(h)

        if(binsxi is not None):
            self._fromBins(binsxi, binsyi, binrangexi, binrangeyi)
        elif(h is None):
            self._initialize()
            print("You will need to initialize this function")
        #elif("pickle" in str(h)):
        #    print("Loading from file...")
        #    self._fromPickle(h)
        #elif(binsxi > 0):
        #    self._initialize()
        #    print("hi")
        #    self._fromBins(binsxi, binsyi, binrangexi, binrangexi)
        else:
            print("Copying from existing python structure...")
            self._fromPython(h)
            
    def _initialize(self):
        self.binsx = -1
        self.binsy = -1
        self.binwidth = np.zeros(2, dtype=np.float64)

    def _fromBins(self, binsx, binsy, binrangex, binrangey):
        '''
            Basically duplicates the root constructor for a TH2 histogram
        '''
        #print("hi")
        
        self.binsx = binsx + 2
        self.binsy = binsy + 2
        
        self.rangex = np.array( binrangex, dtype=np.float64)
        self.rangey = np.array( binrangey, dtype=np.float64)

        self.binwidth = np.array( [ (self.rangex[1] - self.rangex[0])/(self.binsx - 2) , 
                                    (self.rangey[1] - self.rangey[0])/(self.binsy - 2) ] , dtype=np.float64)
        
        self.edgesx = np.linspace(self.rangex[0] - self.binwidth[0], self.rangex[1] + self.binwidth[0], self.binsx+2)
        self.edgesy = np.linspace(self.rangey[0] - self.binwidth[1], self.rangey[1] + self.binwidth[1], self.binsy+2)

        self.contents_overflow = np.zeros((self.binsy, self.binsx), dtype=np.float64)
        self.errors_overflow = np.zeros((self.binsy, self.binsx), dtype=np.float64)
        self.centers_overflow = np.zeros((self.binsy, self.binsx,2), dtype=np.float64)
        
    def _fromPython(self, h):
        self.binsx = h.binsx
        self.binsy = h.binsy
        self.binwidth = np.copy(h.binwidth)
        self.rangex = np.copy(h.rangex)
        self.rangey = np.copy(h.rangey)
        self.edgesx = np.copy(h.edgesx)
        self.edgesy = np.copy(h.edgesy)
        self.contents_overflow = np.copy(h.contents_overflow)
        self.errors_overflow = np.copy(h.errors_overflow)
        #self.erorrs = self.errors_overflow[1:-1,1:-1]
        #self.contents = self.contents_overflow[1:-1,1:-1]
        self.centers_overflow = np.copy(h.centers_overflow)

    def _fromPickle(self, h):
        print(h)
        return -1
        
    def clear_contents(self):
        print("Clearing...")
        self.contents_overflow = np.zeros((self.binsy, self.binsx), dtype=np.float64)
        self.errors_overflow = np.zeros((self.binsy, self.binsx), dtype=np.float64)
        self.centers_overflow = np.zeros((self.binsy, self.binsx,2), dtype=np.float64)
        print("Contents of arrays cleared")

    @property    
    def contents(self):
        return (self.contents_overflow[1:-1,1:-1])
    
    @property
    def errors(self):
        return self.errors_overflow[1:-1,1:-1]
    
    def centers(self, axis=0):
        dicti = {0:self.edgesx, 1:self.edgesy}
        return (dicti[axis][1:-1] + self.binwidth[axis]/2.0 )
    
    
    def findbin(self,x, axis=0, overflow=False ):
        dicti = {0:self.edgesx, 1:self.edgesy}
        #print(dicti[axis])
        #valuei = np.nanargmin(np.where(dicti[axis] > x, x, np.nan))
        if(overflow):
            if(x < dicti[axis][1]):
                return -1
            elif( x > dicti[axis][len(dicti[axis])-1]):
                return -2

        for i, xi in enumerate(dicti[axis]):
            if(x >= xi and x < dicti[axis][i+1]):
                return i-1
        raise ValueError("Bin not in range")
    
    def getbincenter(self, bini, axis=0):
        dicti = {0:self.edgesx, 1:self.edgesy}
        ding =  dicti[axis][1:-1][bini]+self.binwidth[axis]/2.0       
        #print(ding)
        return ding
    
    def draw(self, yscale="log", ax = None, invert = False):
        drawTH2(self, yscale, ax, invert)

    def fill(self, xi, yi, weight=1.):
            binx = self.findbin(yi, 1, True) 
            biny = self.findbin(xi, 0, True)
            #print(binx, biny)
            if((binx > 0) and (biny > 0)):
                self.contents_overflow[ binx + 1 ][ biny+1 ] += weight


def drawTH2(ding, yscale="log", ax = None, invert = False):
    import matplotlib.pyplot as plt
    if(ax is None):
        fig, ax = plt.subplots(figsize=(7,5))
    if(invert):
        todraw = -1*(ding.contents)
    else:
        todraw = ding.contents
    #print((np.absding.contents).min(), ding.contents.max()))
    thisplot = ax.imshow(todraw, aspect='auto', origin='lower', extent=(list(ding.rangex)+ list(ding.rangey)),
                        norm=colors.LogNorm(vmin=np.min(np.abs(ding.contents[np.nonzero(ding.contents)])), vmax=ding.contents.max()))
    cbar = plt.colorbar(thisplot)
    return thisplot


def compareTH2andPython(h, hpy):
    delta = np.zeros((h.GetNbinsY()+2, h.GetNbinsX()+2))
    for i in range(h.GetNbinsX()):
        for j in range(h.GetNbinsY()):
            #print(i,j)
            delta[j][i] = hpy.contents[j][i] - h.GetBinContent(i+1,j+1)
    return delta
