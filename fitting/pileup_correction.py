import ROOT as r 
import math
import numpy as np 
#g-2 Blinding Software
from BlindersPy3 import Blinders
from BlindersPy3 import FitType

# this will contain modules which compute the double/triple pileup correction and apply it to an input histogram
# using Aarons bootstrapped pileup method

class PileupCorrector:
    '''

    '''