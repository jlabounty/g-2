import math
from BlindersPy3 import Blinders
from BlindersPy3 import FitType


fitdict={
    "fitrange":[50,500],
    "npar":5,
    "initial_values":[1000000,64.4, 0.333, 10, 0.1],
    "parnames": ["N", "tau", "A", "R", "phi"],
    "blindingPhrase":"ding!!!",
}
fitdict['blindingLib'] = Blinders(FitType.Omega_a, str(fitdict['blindingPhrase']))

def fitfunc(x,p):
    norm  = p[0]
    life  = p[1]
    asym  = p[2]
    R     = p[3]
    phi   = p[4]

    time  = x[0]
    omega = fitdict['blindingLib'].paramToFreq(R)

    return norm * math.exp(-time/life) * (1 - asym*math.cos(omega*time + phi))