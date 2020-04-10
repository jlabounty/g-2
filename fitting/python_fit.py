

class fitVector():

    def __init__(self, x, y, function, xerr = None, yerr = None, fitoptions = "RQ", nFit = 2, function_python=None):
        '''
            Dumps a python vector of x and y points into a TGraph, then fits with the TF1 function and returns the fit result
        '''
        
        import ROOT as r
        import numpy as np
        import time

        x = list(x)
        y = list(y)
        if(xerr is not None):
            xerr = list(xerr)
            yerr = list(yerr)
        
        fnew = function#.Clone()
        gri = r.TGraphErrors()
        pointi = 0
        for i in range(len(x)):
            if("Timestamp" in str(type(x[i]))):
                x[i] = int(time.mktime(x[i].timetuple()))
            if(y[i] is not np.nan):
                gri.SetPoint(pointi,x[pointi],y[pointi])
                if(yerr is not None):
                    if(xerr is None):
                        xerr = [0 for fiefj in yerr]
                    gri.SetPointError(pointi, xerr[pointi], yerr[pointi])
                pointi += 1
        for i in range(nFit):
            fitresult = gri.Fit(fnew, fitoptions+"S")
            
        cov = fitresult.GetCovarianceMatrix()
        #conf_int = r.Double()
        if (len(x) == len(fitresult.GetConfidenceIntervals(0.95))):
            conf_int = [ fitresult.GetConfidenceIntervals(0.95)[i] for i in range(len(x))] #95% confidence level for this fit
        else:
            x1 = r.Double()
            x2 = r.Double()

            fnew.GetRange(x1,x2)
            #print(x1,x2)
            conf_int_x = [xi for xi in x if(xi >= x1 and xi <= x2)]
            conf_int_y = [fnew.Eval(xi) for xi in conf_int_x]
            #conf_int = [0 for i in range(len(x))]
            conf_int = [ conf_int_x, 
                        conf_int_y,
                        [ fitresult.GetConfidenceIntervals(0.95)[i] for i in range(len(fitresult.GetConfidenceIntervals(0.95)))]] #95% confidence level for this fit
            
        #get the fit parameters and associated errors
        pars = []
        parErrs = []
        for i in range(fnew.GetNpar()):
            pars.append( fnew.GetParameter(i) )
            parErrs.append( fnew.GetParError(i) )
        chiSq = (fnew.GetChisquare() / fnew.GetNDF())
            
        #create a vector of y-points at each of the x points with the fitted function
        fitx = []
        for xi in x:
            fitx.append(fnew.Eval(xi))
        #print("hi")
        
        #get fit residuals
        residuals = []
        pulls = []
        for i, xi in enumerate(fitx):
            residuals.append(y[i] - xi)
            if(yerr is None):
                pulls.append(np.nan)
            elif( np.abs(yerr[i]) > 10**(-10) ):
                pulls.append((y[i] - xi)/yerr[i])
            else:
                pulls.append(np.nan)
            
        self.x = x
        self.y = y 
        self.xerr = xerr
        self.yerr = yerr
        self.f = fnew 
        self.fitx = fitx 
        self.gri = gri 
        self.pars = pars 
        self.parErrs = parErrs 
        self.chiSq = chiSq 
        self.covarianceMatrix = cov 
        self.confidenceIntervals = conf_int 
        self.residuals = residuals 
        self.pulls = pulls 

    def __getitem__(self,index):
        '''
            Implemented only to maintain compatability with functions that were written when this was a
            function that returned a list
        '''
        self.itemList = (self.fitx, (self.pars, self.parErrs), self.chiSq, self.gri, 
                    self.f, self.covarianceMatrix, self.confidenceIntervals, 
                    self.x, self.residuals, self.pulls)
        return self.itemList[index]

    def drawConfidenceIntervals( self, ax, color='blue',labeli=None, drawHist=True):

        if(len(self.confidenceIntervals) is not 3):
            xvals = self.x
            conf_int_high = [x+y for (x,y) in zip(self.fitx, self.confidenceIntervals)]
            conf_int_low = [x-y for (x,y) in zip(self.fitx, self.confidenceIntervals)]

            xvals_sorted, conf_int_high_sorted = zip(*sorted(zip(xvals, conf_int_high)))
            xvals_sorted, conf_int_low_sorted = zip(*sorted(zip(xvals, conf_int_low)))
        else:
            xvals = self.confidenceIntervals[0]
            #print("Warning: Confidence interval length does not match data length")
            conf_int_high = [x+y for (x,y) in zip(self.confidenceIntervals[1], self.confidenceIntervals[2])]
            conf_int_low = [x-y for (x,y) in zip(self.confidenceIntervals[1], self.confidenceIntervals[2])]

            xvals_sorted, conf_int_high_sorted = zip(*sorted(zip(xvals, conf_int_high)))
            xvals_sorted, conf_int_low_sorted = zip(*sorted(zip(xvals, conf_int_low)))

        #ax.plot(xvals_sorted, conf_int_high_sorted)
        #ax.plot(xvals_sorted, conf_int_low_sorted)
        if(drawHist):
            ax.fill_between(xvals_sorted, conf_int_high_sorted, conf_int_low_sorted,
                        facecolor=color, interpolate=True,
                        alpha = 0.2,
                        label=labeli)
        return( xvals_sorted, conf_int_high_sorted, conf_int_low_sorted )
        
    def labelFit(self, parNames=None, functionString=None, formatStr="7.3E", func=None):
        import ROOT as r
        import textwrap

        pars = self.pars
        parErrs = self.parErrs
        chiSquare = self.chiSq

        if(parNames is None):
            parNames = ["p"+str(i) for i in range(len(pars))]
        if(func is not None):
            x1 = r.Double()
            x2 = r.Double()
            func.GetRange(x1, x2)
            parstring = "Fit Result ["+str(round(x1,2))+" - "+str(round(x2,2))+"]"+"\n"
        else:
            parstring = "Fit Result"+"\n"
            
        if(functionString is not None):
            wrapped = textwrap.wrap(functionString, 25)
            parstring+="Function: "+wrapped[0]+"\n"
            if(len(wrapped)>1):
                for fi in wrapped[1:]:
                    parstring += "                "+fi+"\n"
        for i in range(len(pars)):
            parstring += str(parNames[i])+"\t= "+str(format(pars[i], formatStr))
            if(parErrs is not None):
                parstring += "\t"+r"$\pm$ "+str(format(parErrs[i], formatStr))+"\n"
            else:
                parstring += "\n"
        if(chiSquare is not None):
            parstring += r"$\chi^{2}/NDF$ = "+str(chiSquare)
            
        return parstring

    def draw(self,  title = "", yrange=[None, None], xrange=None, data_title = "Data", 
                    resid_title = "Fit Pulls", do_pulls=True):
        '''
            Creates a figure in matplotlib and draws the fitresult / residuals on it
        '''

        import matplotlib.pyplot as plt
        import numpy as np

        fig, axs = plt.subplots(2,1,figsize=(15,8), sharex=True)
        ax = axs[0]
        ax.errorbar(self.x, self.y ,yerr=self.yerr, label="Data")
        
        self.drawFitResult(ax)
        self.drawConfidenceIntervals(ax,"blue", "95% Confidence Level")
        ax.grid()
        if(yrange[0] is None):
            ymean = np.mean(self.y)
            ystd = np.std(self.y)
            ax.set_ylim(ymean - ystd*2, ymean + ystd*2)
        else:
            ax.set_ylim(yrange[0][0],yrange[0][1])
        ax.legend(ncol=1, loc=4)
        ax.set_ylabel(data_title)


        ax = axs[1]
        if(do_pulls):
            self.plotResiduals(ax,1,".:","All Residuals",1)
        else:
            self.plotResiduals(ax,0,".:","All Residuals",1)
        ax.set_ylabel(resid_title)
        ax.grid()
        if(yrange[1] is None):
            ymean = np.mean(self.residuals)
            ystd = np.std(self.residuals)
            ax.set_ylim(ymean - ystd*2, ymean + ystd*2)
        else:
            ax.set_ylim(yrange[1][0],yrange[1][1])
        #ax.set_ylim(-10,10)
        #ax.set_xlim(0,30)

        plt.suptitle(title, y=1.02, fontsize=18)
        plt.tight_layout()
        
        return (fig, ax)

    def drawFitResult(self, ax, scaleFactor=100, drawFormat="-", label="Default"):
        #print(fitresult)
        '''
            Draws a fit result object returned by fitVector function on 'ax' (axes or plot from matplotlib)
        '''
        import numpy as np
        #from standardInclude import labelFit

        if(scaleFactor > 1):
            x0 = self.x[0]
            xn = self.x[len(self.x)-1]
            xs = np.linspace(x0,xn,scaleFactor)
            ys = [self.f.Eval(xi) for xi in xs]
        else:
            xs = self.x
            ys = self.fitx
        
        if(label == "Default"):
            labelString = self.labelFit( None, str(self.f.GetExpFormula()), "7.3E",self.f) 
        else:
            labelString = label
        
        ax.plot(xs,ys,drawFormat,label=labelString)

    def plotResiduals(self, ax, to_plot = 0, fmt=".",labeli="Fit Residuals", runningAverage = 1):
        '''
            Inputs:
                ax             - axis on which to plot
                to_plot        - 0 = residuals; 1 = pulls
                format         - string of formats
                labeli         - what to put in the legend
                runningAverage - Number of points around the residual to compute the running average for
            Outputs:
                matplotlib object containing residuals            
        '''
        import numpy as np

        x = self.x
        if(to_plot == 1):
            resid = self.pulls
        else:
            resid = self.residuals
        
        resid_to_plot = []
        if(runningAverage > 1):
            #resid = [np.nan for i in range(runningAverage)]+resid+[np.nan for i in range(runningAverage)]
            for i in range(len(x)):
                #ri = resid[i]
                if((i >= runningAverage) and ((len(x) - i) >= runningAverage)):
                    mean_ri = np.nanmean(resid[i-runningAverage:i+runningAverage])
                else:
                    mean_ri = np.nan
                resid_to_plot.append(mean_ri)
        else:
            resid_to_plot = resid
        
        #print(resid_to_plot)
        ding = ax.plot(x,resid_to_plot,fmt,label=labeli)
        return ding

    def fft(self, xrange=None, option=0, time_conversion_factor = 10**(-6), drawHist = True):
        '''
            Performs an FFT using python on the functions stored in this class. 
            Options:
                0 = Input function
                1 = Residuals
                2 = Pulls
            xrange: Range over which to perform the FFT. Can be used to exclude data points at beginning/end.
            time_conversion_factor: conversion factor to get the x axis time units to seconds
            drawHist: whether or not to draw the histogram
        '''
        import numpy as np
        import matplotlib.pyplot as plt

        if(option == 0):
            points_raw = self.y
        elif(option == 1):
            points_raw = self.residuals
        elif(option == 2):
            points_raw = self.pulls
        else:
            raise ValueError("Invalid option in fft: "+str(option))

        if(xrange is not None):
            points = []
            xs = []
            print("Restricting range of FFT to:", xrange)
            if(len(xrange) is not 2):
                raise ValueError("xrange is not well defined")
            for i, xi in enumerate(self.x):
                if(xi >= xrange[0] and xi <= xrange[1]):
                    points.append(points_raw[i])
                    xs.append(xi)
        else:
            xs = self.x
            points = points_raw

        ding = np.fft.fft(np.array(points))
        n = len(points)
        d = xs[1] - xs[0]
        freq = np.fft.fftfreq(n, d)
        if(drawHist):
            fig, ax = plt.subplots(1,2,figsize=(15, 5))
            ax[0].plot(xs,points,"-")
            ax[0].set_title("Input function")
            ax[1].set_title("FFT result")
            ax[1].plot([np.abs(x) for x in freq],np.abs(ding),'.:',label='FFT Result')
            #ax[1].set_xlim(0,50)
            plt.xlabel("Frequency [???]")
            #plt.xlim(0,6.7157787731503555 / 2)# *10.**6)
            plt.legend()
            plt.suptitle("FFT Of Fit Result", y=1.02, fontsize=18)
            plt.tight_layout()
            plt.show()

        return (freq, ding)