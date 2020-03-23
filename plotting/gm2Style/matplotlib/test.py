import ROOT as r
import numpy as np
import matplotlib.pyplot as plt


#plt.style.use('./gm2.mplstyle')

data = np.sin(np.linspace(0, 2 * np.pi))
plt.plot(data,"o:")
plt.show()
