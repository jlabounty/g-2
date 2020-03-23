#include <iostream>
#include <cmath>

#include "Rtypes.h"

#include "gm2Style.h"
#include "gm2Labels.h"

#ifdef __CLING__
// these are not headers - do not treat them as such - needed for ROOT6
#include "gm2Labels.C"
#endif

#include "TCanvas.h"
#include "TFile.h"
#include "TROOT.h"
#include "TH1F.h"
#include "TRandom.h"
#include "TGraphErrors.h"
#include "TLegend.h"
#include "TF1.h"


using namespace std;

void gm2Example(){

  
 #ifdef __CINT__
    gROOT->LoadMacro("gm2Labels.C");
  #endif

  SetGm2Style();
    
  TFile* f = new TFile("example.root", "r");

  // set up canvas
  TCanvas* c1 = new TCanvas("c1", "vertical position example", 0., 0., 800, 600);

  // set up Legend
  TLegend* legend = new TLegend(0.7, 0.7, 0.85, 0.85);
  legend->SetBorderSize(0);
  legend->SetFillColor(0);
  legend->SetTextSize(0.04);
  
  TF1* f1 = new TF1("f1","gaus", -20, 20);
  f1->SetLineColor(2);
    
  TH1F* h_data = (TH1F*)f->Get("h_VertPos_data");
  TH1F* h_MC = (TH1F*)f->Get("h_VertPos_MC");

  h_data->Rebin(5);
  h_MC->Rebin(5);

  h_data->SetMarkerStyle(20);
  h_data->SetMarkerColor(1);
  h_data->Fit("f1", "R");
    
  h_MC->SetLineColor(1);
  h_MC->SetMarkerStyle(0);
  h_MC->SetFillColor(kViolet-4);
  gStyle->SetErrorX(0.5);
  h_MC->SetTitle("Vertical Position [mm]");
  h_MC->SetXTitle("Vertical Position [mm]");
  h_MC->SetYTitle("Extrapolated Tracks / 5mm");
  
  h_data->GetXaxis()->SetRangeUser(-100, 100);
  h_MC->GetXaxis()->SetRangeUser(-100, 100);
  
  legend->AddEntry(h_data,"Data: Run I","P");
  legend->AddEntry(f1,"Gaussian fit","L");
  legend->AddEntry(h_MC,"MC","LF");
  
  h_MC->DrawCopy("E2");
  h_data->Draw("EP SAME");
  h_MC->SetFillColor(0);
  h_MC->DrawCopy("][ SAME");
  
  h_MC->SetFillColor(kViolet-4);
  legend->Draw();
  
  gm2Label(0.2,0.85,"Preliminary");
  gm2Logo(0.2, 0.6);
  
  c1->Print("gm2Example.eps");
  c1->Print("gm2Example.png");

  return;
  
}

#ifndef __CINT__
int main() { 
  gm2Example();
  return 0;
}
#endif
