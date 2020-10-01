#include <TMath.h>
#include <iostream>
// #include <stringstream>


std::vector<TH1D *> doit(Float_t guess, int whichPoint, 
    TGraph* deltaHist_SM_vs_Combined, TGraph* deltaHist_E821_vs_989, TGraph* deltaHist_SM_vs_989 )
{

    // Create a probabilistic histogram for the:
    // -> SM result
    // -> E821 Result
    // -> E989 result assuming our 'guess' for the central value
    // -> Combined 821 and 989 results
    // And compute their tension (in sigma) with one another. 
    // Create/return histograms with the distributions and fill the TGraphs with the tensions.

    //  First the Standard Model
    TH1D *hSM = new TH1D("SM", "Simulated Function", 150, -500, 1000);
    TF1 *pSM = new TF1("pSM", "gaus(0)", -500, 1000);
    Float_t wSM = 43.;                 //uncertainty in SM
    Float_t cSM = 0;                   // central value of SM; define to be 0
    Float_t aSM = 1.;                  // amp
    pSM->SetParameters(aSM, cSM, wSM); // SM, set at 0, and width x10^-11
    hSM->Eval(pSM);
    hSM->SetXTitle("Relative a_{#mu} [x10^-11]");
    hSM->SetYTitle("Arb. Units");
    pSM->SetNpx(1000);

    // Next E821
    TH1D *h821 = new TH1D("E821", "E821 final", 150, -500, 1000);
    TF1 *p821 = new TF1("p821", "gaus(0)", -500, 1000);
    Float_t w821 = 63.;                    //uncertainty in 821
    Float_t c821 = 279;                    // central value of 821; define to be 0
    Float_t a821 = 0.5;                    // amp
    p821->SetParameters(a821, c821, w821); // 821, set at 0, and width x10^-11
    h821->Eval(p821);
    h821->SetLineColor(2);

    // Next some possible E989 cases
    TH1D *h989 = new TH1D("E989", "E989 final", 150, -500, 1000);
    TF1 *p989 = new TF1("p989", "gaus(0)", -500, 1000);
    Float_t w989 = 54.;                    //uncertainty in 989
    Float_t c989 = guess;                  // central value of 989; define to be 0
    Float_t a989 = 0.5;                    // amp
    p989->SetParameters(a989, c989, w989); // 989, set at 0, and width x10^-11
    h989->Eval(p989);
    h989->SetLineColor(4);

    // Now some differences
    Float_t wwSM = 1.0 / (wSM * wSM);
    Float_t ww821 = 1.0 / (w821 * w821);
    Float_t ww989 = 1.0 / (w989 * w989);
    //    fprintf(stderr,"weightSM %f \n",wwSM);
    //    fprintf(stderr,"weight821 %f \n",ww821);
    //    fprintf(stderr,"weight989 %f \n",ww989);

    Float_t Delta821SM = TMath::Abs(c821 - cSM) / TMath::Sqrt(w821 * w821 + wSM * wSM);
    Float_t Delta989SM = TMath::Abs(c989 - cSM) / TMath::Sqrt(w989 * w989 + wSM * wSM);
    Float_t Delta821989 = TMath::Abs(c821 - c989) / TMath::Sqrt(w821 * w821 + w989 * w989);
    Float_t cNewAvg = (c821 * ww821 + c989 * ww989) / (ww989 + ww821);
    Float_t wNewAvg = sqrt(1.0 / (ww821 + ww989));
    Float_t DeltaNewAvgSM = TMath::Abs(cNewAvg - cSM) / TMath::Sqrt(wNewAvg * wNewAvg + wSM * wSM);

    TH1D *hAvg = new TH1D("Avg", "Avg final", 150, -500, 1000);
    TF1 *pAvg = new TF1("pAvg", "gaus(0)", -500, 1000);
    Float_t aAvg = 1.;                           // amp
    pAvg->SetParameters(aAvg, cNewAvg, wNewAvg); //
    hAvg->Eval(pAvg);
    hAvg->SetLineColor(6);

    
    fprintf(stderr, "Delta: E821 - SM: %f sigma\n", Delta821SM);
    fprintf(stderr, "Delta: E989 - SM: %f sigma\n", Delta989SM);
    fprintf(stderr, "Delta: E821 - E989: %f sigma\n", Delta821989);
    fprintf(stderr, "Average E821 and E989: %f x10-11\n", cNewAvg);
    fprintf(stderr, "Uncerainty New Average: %f x10-11\n", wNewAvg);
    fprintf(stderr, "Delta NewAvg - SM: %f sigma\n", DeltaNewAvgSM);

    deltaHist_SM_vs_Combined->SetPoint(whichPoint, guess, DeltaNewAvgSM);
    deltaHist_E821_vs_989->SetPoint(whichPoint, guess, Delta821989);
    deltaHist_SM_vs_989->SetPoint(whichPoint, guess, Delta989SM);

    std::vector<TH1D*> thisvec =  { hSM, h821, h989, hAvg  }; // return the 4 histograms from this particular 'guess'
    return thisvec;

}


void makeHistograms(int startGuess, int endGuess)
{
    // Loop over a series of E989 guesses and plot tensions for each guess.

    // histogram to be able to control the axis of the TGraphs
    TH1D* axisHist = new TH1D("h",";Relative a_{#mu} [x 10^{-11}]; Tension [#sigma]", 10, -501, 1001);
    axisHist->SetLineColor(0);

    //TGraphs to track the relative tensions in a_mu as we vary the E989 result
    // E821 is unchanging wrt SM, so we only need 3.
    TGraph* deltaHist_SM_vs_Combined = new TGraph(); //(e989 + e821) vs. SM
    deltaHist_SM_vs_Combined->GetXaxis()->SetTitle("Relative a_{#mu} [x 10^{-11}]");
    deltaHist_SM_vs_Combined->GetYaxis()->SetTitle("Tension [#sigma]");
    deltaHist_SM_vs_Combined->SetLineColor(6);
    deltaHist_SM_vs_Combined->SetMarkerColor(6);

    TGraph* deltaHist_E821_vs_989 = new TGraph(); // e821 vs. e989
    deltaHist_E821_vs_989->SetLineColor(2);
    deltaHist_E821_vs_989->SetMarkerColor(2);
    
    TGraph* deltaHist_SM_vs_989 = new TGraph(); // e989 vs. SM
    deltaHist_SM_vs_989->SetLineColor(4);
    deltaHist_SM_vs_989->SetMarkerColor(4);
    int whichPoint = 0;

    //Loop over each of our guesses for the result of 989, filling the TGraphs as we go
    std::cout << "Starting creating images..." << std::endl;
    for (int guess = startGuess; guess < endGuess; guess++)
    {

        std::cout << "989 Guess: " << guess << std::endl;
        std::vector<TH1D*> thisvec = doit(guess, whichPoint, deltaHist_SM_vs_Combined, deltaHist_E821_vs_989, deltaHist_SM_vs_989 );
        whichPoint++;
        // std::cout << thisvec << std::endl;

        // For each 989 'guess'  make a plot 
        TCanvas *c = new TCanvas("c","c", 1000,800);
        c->Divide(1,2);
        c->cd(1);
        thisvec[0]->Draw();
        thisvec[1]->Draw("same");
        thisvec[2]->Draw("same");
        thisvec[3]->Draw("same");

        stringstream label;
        label << "E989 (Guess: " << guess << " )";

        TLegend *leg = new TLegend(0.7,0.2,0.9,0.35);
        leg->AddEntry(thisvec[0], "Standard Model", "l");
        leg->AddEntry(thisvec[1], "E821", "l");
        // leg->AddEntry(thisvec[2], "E989", "l");
        leg->AddEntry(thisvec[2], label.str().c_str(), "l");
        leg->AddEntry(thisvec[3], "Average of 989 and 821", "l");
        leg->Draw("SAME");


        c->cd(2);

        axisHist->Draw();
        axisHist->GetYaxis()->SetRangeUser(-1,15);
        axisHist->GetXaxis()->SetRangeUser(-500,1000);

        deltaHist_SM_vs_Combined->Draw("same");
        deltaHist_SM_vs_Combined->GetYaxis()->SetRangeUser(-1,15);
        deltaHist_SM_vs_Combined->GetXaxis()->SetRangeUser(-500,1000);
        deltaHist_E821_vs_989->Draw("same");
        deltaHist_SM_vs_989->Draw("same");

        TLegend *leg2 = new TLegend(0.2,0.7,0.6,0.9);
        leg2->AddEntry(deltaHist_SM_vs_Combined, "Tension: Combined Meas. vs. SM", "l");
        leg2->AddEntry(deltaHist_E821_vs_989, "Tension: E821 vs. E989", "l");
        leg2->AddEntry(deltaHist_SM_vs_989, "Tension: E989 vs. SM", "l");
        leg2->Draw("SAME");

        c->Update();
        c->Draw();

        //Create output file for this guess' canvas.
        stringstream filename;
        filename << "./images/Comparison_E989_E821_Guess_" << guess << ".png";
        c->Print(filename.str().c_str());

        c->Delete();
    }

    std::cout << "All done!" << std::endl;

}
