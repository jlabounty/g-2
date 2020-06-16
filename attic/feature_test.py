from python_fit import *
import ROOT as r
import matplotlib.pyplot as plt
from standardInclude import *

x = [1,2,3,4,5,6]
y = [2,4,6.2,9,10,13]
yerr = [1,1,1,2,1,1]
xerr = [0 for i in range(len(x))]

import ROOT as r
f1 = r.TF1("f1","pol1",1,5.5,2)
ding = fitVector(x,y, f1, xerr, yerr)
print(ding)
# ding.draw()
# plt.show()

ding.computeConfidenceIntervals(0.95,[-1,10],10)

print(ding.confidenceIntervals)

ding.draw(draw_confidence_intervals=True)
plt.show()


print("All done")