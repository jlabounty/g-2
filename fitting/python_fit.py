

class fitVector():

    def __init__(self, x=None, y=None, function=None, xerr = None, yerr = None, fitoptions = "RQ", nFit = 2, input_file=None):
        '''
            Dumps a python vector of x and y points into a TGraph, then fits with the TF1 function and returns the fit result
            Input:
                x          - vector of x points to fit
                y          - vector of y points to fit
                function   - ROOT.TF1 object used for fitting
                xerr       - vector of x error points to fit. If none, will not assign errors, unless yerr is defined. The will be all 0's.
                xyerr      - vector of y error points to fit. If none, will not assign errors.
                fitoptions - options to pass to the function.Fit() call, default is "RQ"
                nFit       - number of times to do fit. Iteration can sometimes produce better results.
                    
        '''

        if(input_file is not None):
            self.from_file(input_file)
            return
        
        if(x is None or y is None or function is None):
            raise ValueError("One or more required arguments (x,y,func) is not defined")
        
        import ROOT as r
        import numpy as np
        import time
        import ctypes 

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
        #conf_int = ctypes.c_double
        if (len(x) == len(fitresult.GetConfidenceIntervals(0.95))):
            conf_int = [ fitresult.GetConfidenceIntervals(0.95)[i] for i in range(len(x))] #95% confidence level for this fit
            self.xmin = min(x)
            self.xmax = max(x)
        else:
            x1 = ctypes.c_double()
            x2 = ctypes.c_double()
            fnew.GetRange(x1,x2)
            x1 = x1.value
            x2 = x2.value

            self.xmin = x1
            self.xmax = x2
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
        pullsInRange = []
        residualsInRange = []
        
        for i, xi in enumerate(fitx):
            if(x[i] >= self.xmin and x[i] <= self.xmax):
                residualsInRange.append(y[i] - xi)
            residuals.append(y[i] - xi)
            if(yerr is None):
                pulls.append(np.nan)
                if(x[i] >= self.xmin and x[i] <= self.xmax):
                    pullsInRange.append(np.nan)
            elif( np.abs(yerr[i]) > 10**(-10) ):
                pulls.append((y[i] - xi)/yerr[i])
                if(x[i] >= self.xmin and x[i] <= self.xmax):
                    pullsInRange.append((y[i] - xi)/yerr[i])
            else:
                pulls.append(np.nan)
                if(x[i] >= self.xmin and x[i] <= self.xmax):
                    pullsInRange.append(np.nan)
            
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
        self.residualsInRange = residualsInRange
        self.pullsInRange = pullsInRange

    def from_file(self, filename):
        print("Importing from:", filename)
        import ROOT as r

        f = r.TFile(filename)
        f.ls()

        t = f.Get("t")

        keys = [x.GetName() for x in f.GetListOfKeys() if (x.GetName() is not "t")]
        print(keys )

        for key in keys:
            ding = f.Get(key)
            #ding.SetDirectory(0)
            exec("self."+str(key)+" = ding")
            #exec("self."+str(key)+".SetDirectory(0)")

        keys = [x.GetName() for x in t.GetListOfBranches()]
        extractedVecs = [None for i in keys]
        for j, entry in enumerate(t): #should only be 1
            #print(entry)
            for i, key in enumerate(keys):
                entries = entry.Draw(key,"","goff")
                content = [entry.GetVal(0)[x] for x in range(entries)]
                #print(content)
                if(len(content) is 1):
                    content = content[0]
                try:
                    content = list(content)
                except:
                    pass
                #print(content)
                extractedVecs[i] = content 
            break
        #print(extractedVecs)

        #reform the _N entries into sublists
        formattedVecs = []
        formattedEntries = []
        dicti = {}
        for key in keys:
            dicti[key.split("_")[0]] = []
        print(dicti)
        for (key, veci) in zip(keys,extractedVecs):
            corekey = key.split("_")[0]
            nentries = sum(corekey in s for s in keys)
            if(nentries > 1 and len(key.split("_")) > 1):
                print(key)
                dicti[corekey].append(veci)
            else:
                formattedVecs.append(veci)
                formattedEntries.append(key)
        
        for key in keys:
            corekey = key.split("_")[0]
            if len(dicti[corekey]) > 1:
                exec("self."+str(corekey)+" = "+str(dicti[corekey]))

        for(key, vec) in zip(formattedEntries, formattedVecs):
            exec("self."+str(key)+" = "+str(vec))

        f.Close()

    def __getitem__(self,index):
        '''
            Implemented only to maintain compatability with functions that were written when this was a
            function that returned a list
        '''
        self.itemList = (self.fitx, (self.pars, self.parErrs), self.chiSq, self.gri, 
                    self.f, self.covarianceMatrix, self.confidenceIntervals, 
                    self.x, self.residuals, self.pulls)
        return self.itemList[index]

    def parNames(self):
        return [self.convertRootLabelsToPython(str(self.f.GetParName(i))) for i in range(len(self.pars))]

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
    
    def convertRootLabelsToPython(self, label):
        '''
            ROOT and Python parse LaTeX slightly differently for their legends. Lets convert between them.
        '''
        if("#" in label or "_" in label):
            #print(label)

            ding = label.replace("#","\\")
            ding = r"$"+ding+"$ "

            #print(ding)
            return ding
        else:
            return label
        
    def labelFit(self, parNames=None, functionString=None, formatStr="7.3E", func=None,fitname=None):
        import ROOT as r
        import textwrap
        import ctypes 

        pars = self.pars
        parErrs = self.parErrs
        chiSquare = self.chiSq

        if(parNames is None):
            #parNames = ["p"+str(i) for i in range(len(pars))]
            parNames = [self.convertRootLabelsToPython(str(self.f.GetParName(i))) for i in range(len(pars))]
        if(func is not None):
            x1 = ctypes.c_double()
            x2 = ctypes.c_double()
            func.GetRange(x1, x2)
            x1 = x1.value 
            x2 = x2.value 
            parstring = "Fit Result ["+str(round(x1,2))+" - "+str(round(x2,2))+"]"+"\n"
        else:
            parstring = "Fit Result"+"\n"
        if(fitname is not None):
            parstring += str(fitname)+"\n"

        if(functionString is not None):
            wrapped = textwrap.wrap(functionString, 25)
            parstring+="Function: "+wrapped[0]+"\n"
            if(len(wrapped)>1):
                for fi in wrapped[1:]:
                    parstring += "                "+fi+"\n"
        for i in range(len(pars)):
            #parstring += str(parNames[i])+"\t= "+str(format(pars[i], formatStr))
            if(parErrs is not None):
                parstring += ("{0}".ljust(10)+" = {1:.3e} $\\pm$ {2:.3e}").format(parNames[i], pars[i], parErrs[i])+"\n"
                #parstring += "\t"+r"$\pm$ "+str(format(parErrs[i], formatStr))+"\n"
            else:
                parstring += ("{0}".ljust(10)+" = {1:.3e}").format(parNames[i], pars[i])+"\n"
                #parstring += "\n"
        if(chiSquare is not None):
            parstring += r"$\chi^{2}/NDF$ = "+str(chiSquare)
            
        return parstring

    def draw(self,  title = "Fit Result", yrange=[None, None], xrange=None, data_title = "Data", 
                    resid_title = "Fit Pulls", do_pulls=True, fit_hist=True, fmti=".-"):
        '''
            Creates a figure in matplotlib and draws the fitresult / residuals on it
        '''

        import matplotlib.pyplot as plt
        import numpy as np

        #fig, axs = plt.subplots(2,1,figsize=(15,8), sharex=True)
        fig = plt.figure(figsize=(15,8))
        gs = fig.add_gridspec(2,3)
        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, :-1])
        ax3 = fig.add_subplot(gs[1, -1:])

        axs = [ax1, ax2, ax3]
        ax = axs[0]
        ax.errorbar(self.x, self.y ,yerr=self.yerr, fmt=fmti, label="Data", ecolor='xkcd:grey', zorder=35)
        
        self.drawFitResult(ax, scaleFactor=int(len(self.x)*10))
        self.drawConfidenceIntervals(ax,"blue", "95% Confidence Level")
        ax.grid()
        if(yrange[0] is None):
            ymean = np.mean(self.y)
            ystd = np.std(self.y)
            ax.set_ylim(ymean - ystd*2, ymean + ystd*2)
        else:
            ax.set_ylim(yrange[0][0],yrange[0][1])
        if(xrange is not None):
            ax.set_xlim(xrange[0], xrange[1])
        leg = ax.legend(ncol=1, loc=4)
        leg.set_zorder(37)
        ax.set_ylabel(data_title)


        ax = axs[1]
        if(do_pulls):
            ax.set_title("Fit Pulls")
            self.plotResiduals(ax,1,fmti,"All Residuals",1)
        else:
            ax.set_title("Fit Residuals")
            self.plotResiduals(ax,0,fmti,"All Residuals",1)
        ax.set_ylabel(resid_title)
        ax.grid()
        if(yrange[1] is None):
            ymean = np.mean(self.residuals)
            ystd = np.std(self.residuals)
            ax.set_ylim(ymean - ystd*2, ymean + ystd*2)
        else:
            ax.set_ylim(yrange[1][0],yrange[1][1])
        #ax.set_ylim(-10,10)
        if(xrange is not None):
            ax.set_xlim(xrange[0], xrange[1])
        
        ax = axs[2]
        ax.grid()
            
        if(do_pulls):
            ax.set_title("Histogram of Fit Pulls")
            hist1 = ax.hist(self.pullsInRange, bins=40)
        else:
            ax.set_title("Histogram of Fit Residuals")
            hist1 = ax.hist(self.residualsInRange, bins=40)
            
        if(fit_hist):
            fitHistGaussian(hist1, ax, True, True)
            ax.legend()

        plt.suptitle(title, y=1.02, fontsize=18)
        plt.tight_layout()
        
        return (fig, axs)

    def drawFitResult(self, ax, scaleFactor=100, drawFormat="-", label="Default", color="xkcd:orange", fitname=None):
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
            labelString = self.labelFit( None, str(self.f.GetExpFormula()), "7.3E",self.f, fitname=fitname) 
        else:
            labelString = label
        
        ax.plot(xs,ys,drawFormat,label=labelString, zorder=36, color=color)
        

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

    def plotRunningAverage(self, averages=[1,10,100], showplot=True, fmti="."):
        fig,ax = plt.subplots(figsize=(15,5))
        for average in averages:
            fitresult.plotResiduals(ax, 1, fmti, str(average), average)
        plt.grid()
        plt.title("Running Average of Residuals")
        plt.legend()
        return (fig,ax)

    def fft(self, xrange=None, option=0, time_conversion_factor = 10**(-6), drawHist = True, logy=True):
        '''
            Performs an FFT using python on the functions stored in this class. 
            Options:
                0 = Input function
                1 = Residuals
                2 = Pulls
            xrange: Range over which to perform the FFT. Can be used to exclude data points at beginning/end.
            time_conversion_factor: conversion factor to get the x axis time units to seconds
            drawHist: whether or not to draw the histogram
            logy : Should the fft axis be a log scale
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
            for axi in ax:
                axi.grid()
            ax[0].plot(xs,points,"-")
            ax[0].set_title("Input function")
            ax[1].set_title("FFT result")
            ax[1].plot([np.abs(x) for x in freq],np.abs(ding),'.:',label='FFT Result')
            #ax[1].set_xlim(0,50)
            if(logy):
                ax[1].set_yscale("log")
            plt.xlabel("Frequency [MHz]")
            #plt.xlim(0,6.7157787731503555 / 2)# *10.**6)
            plt.legend()
            plt.suptitle("FFT Of Fit Result", y=1.02, fontsize=18)
            plt.tight_layout()
            plt.show()

        return (freq, ding)
    
    def save(self, outfile_name):
        print("Saving to:", outfile_name)
        import inspect 
        import ROOT as r

        self.arrs = []
        self.arrCounter = 0

        toSave = []
        attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
        #print(attributes)
        for x in attributes:
            if ("__" not in x[0]):
                print(x)
                toSave.append(x)
        
        self.fout = r.TFile(outfile_name,"RECREATE")
        self.fout.cd()

        t = r.TTree("t","Variable Tree")

        for key, item in toSave:
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

            elif( "ROOT.TF1" in (str(type(item))) ):
                f1 = item
                f1.Write(key)

            else:
                print("Type not supported", type(item) )

        t.Fill()

        self.fout.cd()
        self.fout.Write()
        self.fout.Close()

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
        
        #print(keystring, ni)
        t.Branch(key, self.arrs[i], keystring)
        #r.gROOT.cd()
    
    
#from standardInclude import *

def fitHistGaussian(hist, ax, draw = False, label=True):
    '''
        Fits a python histogram to a gaussian function and draws the result
    '''
    
    import ROOT as r
    from standardInclude import histToTH1, TH1ToNumpyArray

    xmin = min(hist[1])
    xmax = max(hist[1])
    fgaus = r.TF1("fgaus","gaus",xmin, xmax)
    if("ROOT.TH" not in str(type(hist))):
        roothist = histToTH1(hist)
    else:
        roothist = hist
    fgaus.SetParameters(10, roothist.GetMean(), roothist.GetStdDev())
    x, y, *_ = TH1ToNumpyArray(roothist)
    
    fiti = fitVector(x,y,fgaus)
    if(label):
        labeli= "Mean:  "+str(round(fiti.pars[1],4))+r" $\pm$ "+str(round(fiti.parErrs[1],4))+"\n"
        labeli+=r"$\sigma$:         "+str(round(fiti.pars[2],4))+r" $\pm$ "+str(round(fiti.parErrs[2],4))
    else:
        labeli=None
    
    if(draw):
        fiti.drawFitResult(ax,label=labeli)
        
    return fiti
    
def compareFits(fitdict, fig=None, ax=None, fmti=',', drawFits=True, drawData = True, labelData = False):
    '''
        Utility to compare overtop two members of the fitVector class
        Inputs:
            fitdict             - dictionary of name:fit
            fig,ax (optional)   - axes to draw the fit on
            fmt                 - format string
            drawFits            - bool, whether or not to draw the fit results
            drawData            - bool, whether or not the draw the underlying data
            labelData           - bool, whether or not to label the data on the legend
        Returns:
            fig,ax
    '''
    import matplotlib.pyplot as plt 

    if(fig is None):
        fig,ax = plt.subplots(figsize=(15,5))
    plt.sca(ax)
    
    colors =     ['blue', 'xkcd:orange', 'xkcd:forest green']
    datacolors = ['xkcd:lightblue', 'xkcd:light orange', 'xkcd:light green']
    counter = 0
    for name in fitdict:
        fit = fitdict[name]
        #ax.plot(fit.x, fit.y, fmti, color=datacolors[counter],label="Data: "+str(name))
        if(labelData):
            datalabel="Data: "+str(name) 
        else:
            datalabel=None 
        if(drawData):
            ax.errorbar(fit.x, fit.y, fmt=fmti, yerr=fit.yerr, 
                        ecolor='xkcd:grey', color=datacolors[counter],
                        label=datalabel)
        if(drawFits):
            fit.drawFitResult(ax,color=colors[counter], scaleFactor=1000, fitname=name)
        counter+=1
        
    plt.title("Comparison of Fits")
    #plt.legend(ncol=counter)
    plt.grid()
    return (fig,ax)

class fitHist(fitVector):
    '''
        Subclass of the fitVector class
        Takes as input a root or python histogram and converts it to a vector format, then passes that to the fitVector class
    '''
    def __init__(self, hist, func, binErrors = True, fitoptions = "RQ", nfit=2, input_file=None):
        #extract the required information from the histogram
        if("TH1" in str(type(hist))):
            self.inputHist = hist.Clone("inputHist")
            self.inputHist.SetDirectory(0)
            self.binWidth = hist.GetBinWidth(1)
            nbins = hist.GetNbinsX()
            xs = []
            ys = []
            xerr = []
            yerr = []
            for i in range(1,nbins+1):
                xs.append(hist.GetBinCenter(i))
                ys.append(hist.GetBinContent(i))
                if(binErrors):
                    yerr.append(hist.GetBinError(i))
                else:
                    yerr.append(0)
                xerr.append(0) # TODO: Implement x errors in a consistent way
        else:
            raise ValueError("Histogram type unsupported")


        #use the fitVector init class
        fitVector.__init__(self, x=xs, y=ys, function=func, xerr = xerr, yerr = yerr, 
                            fitoptions = fitoptions, nFit = nfit, input_file=input_file)

