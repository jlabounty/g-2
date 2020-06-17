int root_intro() //the name of the function must match the name of the file for you to run it like 'root -l XXX'
{

    //this uses C++ syntax, and so all of our variables must be declared explicitly
    int i = 2;
    double j = 6.8;
    std::cout << i << " " << j << std::endl;


    //**************************************************************************************

    int nBins = 100;
    double xLow = 0;
    double xHigh = 1;
    TH1D* h = new TH1D( // The 'D' here means that each bin contains a double. 
        "h",    // Name of the histogram
        "Example Histogram with a Fancy Title using Latex: //omega/n//pi [//mus]; X-Axis Title; Y-Axis Title", // Title 
        nBins,       // Number of bins (there is also an under/overflow bin)
        xLow, xHigh); // Range of the lowest bin edge to the highest bin edge


        

    // now we have a histogram, lets draw it on a canvas
    // TCanvas *c = new TCanvas()                             // default parameters are fine, or...
    TCanvas *c = new TCanvas("c","First Canvas", 1200,600); // we can specify a name/dimensions

    h->Draw();

    c->Draw();

    // ////// Nice, we have an empty histogram, now lets fill it with some data

    // In[5]:

    TRandom3 *rng = new TRandom3();
    double weight = 1;
    for (int i = 0; i < 10000; i++)
    {
        h->Fill(rng->Gaus(0.50, .50), weight); // we can fill the histogram with a different weight if we wish. If we leave off this argument, the default is 1
    }


    // In[6]:


    // lets see how our histogram has changed
    TCanvas *c2 = new TCanvas("c","First Canvas", 1200,600); // we can specify a name/dimensions

    h->Draw();

    c2->Draw();



    // ////// Maybe we can make this look a little better....

    // In[7]:


    // lets see how our histogram has changed
    TCanvas *c3 = new TCanvas("c","First Canvas", 1200,600); // we can specify a name/dimensions

    h->SetLineColor(2); // see: https://root.cern.ch/doc/master/classTColor.html
    h->SetFillColorAlpha(45,0.2);
    h->Draw();

    c3->SetGrid(); // we can make the values a little easier to read with a grid
    c3->SetLogy(); // or maybe we think this would look better on a log scale
    c3->Draw();


    // ////// What if our data is more than one dimensional? Well theres a histogram for that too

    // In[8]:


    TH2D *h2 = new TH2D("h2", "A 2D histogram; Ding; Dong", 
            200, 0, 1,  //x-axis
            10, 0, 100); //y-axis, the number of bins and the ranges can be different for each of the axes

    // randomdata_x = np.random.random(10000)
    // randomdata_y = np.random.random(10000)

    // for (x,y) in zip(randomdata_x,randomdata_y):
    //     h2.Fill(x,y*100)

    for (int i = 0; i < 10000; i++)
    {
        h2->Fill(rng->Gaus(0.50, .50), rng->Gaus(0.50, 50), weight); // we can fill the histogram with a different weight if we wish. If we leave off this argument, the default is 1
    }
        
    TCanvas *c4 = new TCanvas();
    h2->Draw("colz"); //colz creates a colorscale
    c4->Draw();


    // In[9]:


    TCanvas *c5 = new TCanvas();
    h2->Draw("lego2z"); //lego creates a 3d plot
    c5->Draw();


    // ---
    // 
    // // TGraph
    // 
    // 
    // Now that we understand how histograms work, we can quickly mention unbinned data formats. These are less useful to us because they quickly become memory intensive, but are important to note.

    // In[10]:


    TGraph *gr = new TGraph(); // no need to initialize the bins, there aren't any
    gr->SetTitle("An Example Graph; Wow such label; Many science");

    // for i in range(len(randomdata_x)):
    //     gr.SetPoint(i, randomdata_x[i], randomdata_y[i]) //each point has an index as well as the data value
    for (int i = 0; i < 10000; i++)
    {
        gr->SetPoint(i, rng->Gaus(0.50, .50), rng->Gaus(0.50, 50) ); // we can fill the histogram with a different weight if we wish. If we leave off this argument, the default is 1
    }

    TCanvas *c6 = new TCanvas();
    gr->Draw();
    c6->Draw();


    // In[11]:


    //lets just draw the axes (a) and points (p)

    TCanvas *c7 = new TCanvas();
    gr->Draw("ap");
    c7->Draw();


    // ---
    // 
    // // Functions
    // 
    // Now lets create a histogram with gaussian data to show off the power of root fits`

    // In[12]:


    TH1D* h22 = new TH1D("h","Gaussian Fit Example", 100,0,100);
    // for i in range(10000):
    //     h.Fill( np.random.normal(30, 5) )
    for(int i = 0; i < 10000; i++)
    {
        h22->Fill( rng->Gaus(30, 5.0) );
    }


    // In[13]:


    TCanvas *c8 = new TCanvas();
    h22->Draw();
    c8->Draw();


    // ////// Now lets create a gaussian function to fit this using the built in TMath 'gaus' function

    // In[14]:


    TF1* func = new TF1("func", //name of the function
                        "gaus", //a string detailing what the function is. This is parsed by ROOT
                        0,100   //the range in which the function is defined.
                        );


    // In[15]:


    //lets fit the histogram
    TCanvas *c9 = new TCanvas();
    h22->Fit(func);
    h22->Draw();
    c9->Draw();


    // ////// We can also use a TF1 to generate random data using the FillRandom function, this will allow us to show off a more complex fit

    // In[31]:


    // func2 = r.TF1("func2","[0]+[1]*x+[2]*TMath::Sin([3]*x + [4])",0,100)
    TF1* func2 = new TF1("func2","[0]*TMath::Exp(-x/[1])*( 1- [2]*TMath::Sin([3]*x + [4]))",0,100);
    func2->SetParameters(10000,64.4,0.33,2,2);
    func2->SetNpx(5000);
    func2->SetLineColor(3);
    TCanvas *c0 = new TCanvas();
    func2->Draw();
    c0->Draw();


    // In[32]:


    TH1I* h3 = new TH1I("h","Example Integer Histogram with Fancy Fit", 1000,0,100);
    h3->FillRandom("func2", 1000000);


    // In[33]:


    TCanvas *c01 = new TCanvas();
    h3->Draw();
    c01->Draw();


    // In[34]:


    TCanvas *c02 = new TCanvas();
    func2->SetParameters(40000,34.4,0.53,2,2);
    h3->Fit(func2);
    h3->Draw();
    c02->Draw();


    // ////// Why didn't that work? Well maybe we need to use some fitting options...

    // In[35]:


    TCanvas *c03 = new TCanvas();
    h3->Fit(func2,"REMB");
    h3->Draw();
    c03->Draw();


    // ////// Or perhaps just a better initial guess?

    // In[42]:


    TCanvas *c04 = new TCanvas();
    func2->SetParameters(2000,100,0.33,2,2);
    h3->Fit(func2,"REMB");
    h3->Draw();
    c04->Draw();



    return 0;
}