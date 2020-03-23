#include <iostream>
#include "TH3F.h"
#include "TH2F.h"
#include "TH1F.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TGraph.h"
#include "TGraphErrors.h"
#include "TStyle.h"
#include "TTree.h"
#include "TMath.h"
#include "TRandom3.h"
#include "TrackerAcceptance.h"

using namespace::std;


void convolution(string inputFileName, string phaseFileName, int datasetNum, string app = ""){

  double w0   = 2.3376; //rad us-1
  double A    = 2.79; //rad
  double tauA = 61.1; //us
  double B    = 5.63; //rad
  double tauB = 6.07; //us

  if (datasetNum == 2){
    w0 = 2.6094;
    A = 2.80;
    tauA = 56.6;
    B = 6.18;
    tauB = 6.32;
  }

  if (datasetNum == 3){
    w0 = 2.6137;
    A = 2.88;
    tauA = 49.2;
    B = 6.27;
    tauB = 6.18;
  }

  if (datasetNum == 4){
    w0 = 2.3354;
    A = 6.82;
    tauA = 78.3;
    B = 5.42;
    tauB = 6.54;
  }

  //double t = 35.0;
  //double omega1 = w0 + (A/tauA) * exp(-t/tauA) + (B/tauB) * exp(-t/tauB);
  //t = 500.0;
  //double omega2 = w0 + (A/tauA) * exp(-t/tauA) + (B/tauB) * exp(-t/tauB);
  //cout << "omega 1: " << omega1 << " omega2; " << omega2 << "\n";
  //return;
      


  TFile *phaseFile  = new TFile(phaseFileName.c_str());
  TCanvas* phaseMap = (TCanvas*) phaseFile->Get("c34a"); 
  gStyle->SetOptStat(0);

  phaseMap->SaveAs("Images/phaseMapOrig.png");
  TIter tmp(gPad->GetListOfPrimitives());

  TH2D* phase = NULL;
  while (TObject *obj = tmp.Next()) {
    cout << "new object of class " << obj->ClassName() << "\n";
    if (obj->InheritsFrom(TH2::Class())){
      cout << "found TH2 \n";
      phase = (TH2D*)obj->Clone("phase");
    }
  }

  int nBinsX = phase->GetNbinsX();
  double binWidthX = phase->GetXaxis()->GetBinWidth(nBinsX-1);
  int nBinsY = phase->GetNbinsX();
  double binWidthY = phase->GetYaxis()->GetBinWidth(nBinsY-1);
  cout << "nBins X : " << nBinsX << " width: " << binWidthX << "\n";
  cout << "nBins Y : " << nBinsY << " width: " << binWidthY << "\n";

  //make symmetric about y : can't fill phase itself as it goes weird!!
  TH2F* pMap = new TH2F("pMap", "; radial position [mm]; vertical position [mm]", nBinsX, -45, 45, nBinsY, -45, 45);

  for (int xbin(1); xbin < nBinsX+1; xbin++){
    vector<double> negYCont;
    for (int ybin(1); ybin < nBinsY+1; ybin++){
      double x = phase->GetXaxis()->GetBinCenter(xbin);
      double y = phase->GetYaxis()->GetBinCenter(ybin);
      double cont = phase->GetBinContent(xbin, ybin);
      if (y < 0) {
	negYCont.push_back(cont);
	pMap->SetBinContent(xbin, ybin, cont);
      }
      //cout << "xbin: " << xbin << " ybin: " << ybin << " x: " << x << " y: " << y << " cont: " << cont << "\n";
      
      if (y > 0 && negYCont.size() > 0) {
	double newCont = negYCont.back();
	//cout << "previously empty bin will be filled with :" << newCont << " size: " << negYCont.size() <<  "\n";
	negYCont.pop_back();
	pMap->SetBinContent(xbin, ybin, newCont);
	//break;
      }
      //cout << "AFTER xbin: " << xbin << " ybin: " << ybin << " x: " << x << " y: " << y << " cont: " << phase->GetBinContent(xbin, ybin) << "\n\n";
    }
  }

  //cout << "\n\n\n\n";
  //for (int xbin(1); xbin < nBinsX+1; xbin++){
  //  for (int ybin(1); ybin < nBinsY+1; ybin++){
  //    double x = pMap->GetXaxis()->GetBinCenter(xbin);
  //    double y = pMap->GetYaxis()->GetBinCenter(ybin);
  //    double cont = phase->GetBinContent(xbin, ybin);
  //    cout << "xbin: " << xbin << " ybin: " << ybin << " x: " << x << " y: " << y << " cont: " << cont << "\n";
  //  }
  //}

  TCanvas* c1 = new TCanvas("c1", "", 800, 600);
  pMap->GetYaxis()->SetRangeUser(-45, 45);
  pMap->Draw("COLZ");
  c1->SaveAs("Images/phaseMap.png");

  //////////////////////////////////////////

  gStyle->SetPalette(55);
  gStyle->SetTitleX(0.08);
  gStyle->SetTitleY(0.95);
  gStyle->SetTitleH(0.05);
  gStyle->SetTitleAlign(12);

  TFile *file  = new TFile(inputFileName.c_str());
  TTree *tree = (TTree*)file->Get("QualityVertices");

  int64_t nEntries = tree->GetEntries();
  //nEntries = 1E6;// 60h = 18051105
  cout << "\n\tEntries = " << nEntries << ";\n" << endl;

  float decayTime, x, y, z;
  int station;
  bool passCandQuality, passTrackQuality, passVertexQuality;
  tree->SetBranchAddress("decayTime",&decayTime);
  tree->SetBranchAddress("decayVertexPosX",&x);
  tree->SetBranchAddress("decayVertexPosY",&y);
  tree->SetBranchAddress("decayVertexPosZ",&z);
  tree->SetBranchAddress("station",&station);
  tree->SetBranchAddress("passCandidateQuality",&passCandQuality);
  tree->SetBranchAddress("passTrackQuality",&passTrackQuality);
  tree->SetBranchAddress("passVertexQuality",&passVertexQuality);
  
  //TH3F* hBeamSpot = new TH3F("hBeamSpot", "All Tracks;Time [us];Entries", 160, -80, 80, 160, -80, 80, 670,0,670*0.14919);
  double binEdgesX[19];
  double binEdgesY[19];
  binEdgesX[0] = -45.0;
  binEdgesY[0] = -45.0;
  for (int i(1); i < 19; i++){
    binEdgesX[i] = binEdgesX[i-1] + 5.0;
    binEdgesY[i] = binEdgesY[i-1] + 5.0;
  }

  double binEdgesZ[69];
  binEdgesZ[0] = 0.0;
  for (int i(1); i < 69; i++ ){
    binEdgesZ[i] = binEdgesZ[i-1] + 1.0/(exp(-1 * binEdgesZ[i-1] / 64.4));
    //cout << i << " : " << binEdges[i] << "\n";
  }
  //return;

  TH3F* hBeamSpot12 = new TH3F("hBeamSpot12", "All Tracks;Time [us];Entries", 18, -45, 45, 18, -45, 45, 2*260, 0, 2600*0.14919);
  TH3F* hBeamSpot18 = new TH3F("hBeamSpot18", "All Tracks;Time [us];Entries", 18, -45, 45, 18, -45, 45, 2*260, 0, 2600*0.14919);
  TH3F* hBeamSpot12_reco = new TH3F("hBeamSpot12_reco", "All Tracks;Time [us];Entries", 18, -45, 45, 18, -45, 45, 2*260, 0, 2600*0.14919);
  TH3F* hBeamSpot18_reco = new TH3F("hBeamSpot18_reco", "All Tracks;Time [us];Entries", 18, -45, 45, 18, -45, 45, 2*260, 0, 2600*0.14919);
  
  // //fancy binning at late times
  // TH3F* hBeamSpot12 = new TH3F("hBeamSpot12", "All Tracks;Time [us];Entries", 18, binEdgesX, 18, binEdgesY, 68, binEdgesZ);
  // TH3F* hBeamSpot18 = new TH3F("hBeamSpot18", "All Tracks;Time [us];Entries", 18, binEdgesX, 18, binEdgesY, 68, binEdgesZ);

  // //no acceptance applied
  // TH3F* hBeamSpot12_reco = new TH3F("hBeamSpot12_reco", "All Tracks;Time [us];Entries", 18, binEdgesX, 18, binEdgesY, 68, binEdgesZ);
  // TH3F* hBeamSpot18_reco = new TH3F("hBeamSpot18_reco", "All Tracks;Time [us];Entries", 18, binEdgesX, 18, binEdgesY, 68, binEdgesZ);

  TRandom3* rng = new TRandom3(12345);

  double targetPerc = 0;
  for(int64_t entry = 0; entry < nEntries; entry++){

    if(100*float(entry) / nEntries > targetPerc){
      cout << Form("Processed %.1f%%", 100*float(entry)/nEntries) << endl;
      targetPerc += 10;
    }

    tree->GetEntry(entry);

    if(passCandQuality && passTrackQuality && passVertexQuality){

      double rReco = sqrt(x*x + z*z) - 7112.1;
      double r = GetTrueRFromReco(rReco);
      
      double weight = GetAcceptanceWeight(r, y);

      // Randomise out all the wiggling!
      double time = decayTime;

      //time = 8.0 * 1000.0;
      double wCBO =  (w0 - (A/(tauA)) * exp(-time/(1000.0*tauA)) - (B/(tauB)) * exp(-time/(tauB*1000.0)) ); //MHz
      double wa =  TMath::TwoPi() * 0.2291; //MHZ
      double wc =  TMath::TwoPi() / 0.14919; //MHz

      double factor = 1.0;
      double wY = factor * (wCBO) * sqrt( (2 * wc / (factor * wCBO)) -1.0 ) ;
      double wVW = wc - (2.0 * wY);

      double TCBO = TMath::TwoPi() / wCBO;
      double Ta = TMath::TwoPi() / wa;
      double TVW = TMath::TwoPi() / wVW;
      double TY = TMath::TwoPi() / wY;
      double Tc = TMath::TwoPi() / wc;

      // Omega-a and omega-CBO beat frequencies
      double T_diff= TMath::TwoPi()/(wCBO-wa);
      //      double T_sum = TMath::TwoPi()/(wCBO+wa);

      // cout << "fC: "   << wc / TMath::TwoPi()   << " MHz, period:  " << Tc   << " us " << "\n";
      // cout << "fa: "   << wa / TMath::TwoPi()   << " MHz, period:  " << Ta   << " us " << "\n";
      // cout << "fCBO: " << wCBO / TMath::TwoPi() << " MHz, period:  " << TCBO << " us " << "\n";
      // cout << "fY: "   << wY / TMath::TwoPi()   << " MHz, period:  " << TY   << " us " << "\n";
      // cout << "fVW: "  << wVW / TMath::TwoPi()  << " MHz, period:  " << TVW  << " us " << "\n";
      // cout << "f_diff: " << (wCBO-wa) / TMath::TwoPi()   << " MHz, period:  " << T_diff   << " us " << "\n";
      // cout << "f_sum: " << (wCBO+wa) / TMath::TwoPi()   << " MHz, period:  " << T_sum   << " us " << "\n";
      // return;

      time += (rng->Uniform()-0.5)*(Ta*1000.0);// w_a 4365
      time += (rng->Uniform()-0.5)*(TCBO*1000.0);// w_CBO 2703
      time += (rng->Uniform()-0.5)*(TVW*1000.0);// w_VW 433
      time += (rng->Uniform()-0.5)*(TY*1000.0);// w_Y
      time += (rng->Uniform()-0.5)*(Tc*1000.0);// w_c
      time += (rng->Uniform()-0.5)*(T_diff*1000);// Beat between w_a and w_CBO (diff)
      //      time += (rng->Uniform()-0.5)*(T_sum*1000);// Beat between w_a and w_CBO (sum) - this seems to add an oscillation in!

      if(station == 12)	{
	//y += .175;
	hBeamSpot12->Fill(r,y,time/1000, weight);
	hBeamSpot12_reco->Fill(rReco,y,time/1000);
      }
      if(station == 18)	{
	//y += -.175;
	hBeamSpot18->Fill(r,y,time/1000, weight);
	hBeamSpot18_reco->Fill(rReco,y,time/1000);
      }

    } // quality

  } //entry

  TFile* outFile = new TFile(Form("out%s.root", app.c_str()), "RECREATE");
  int ii = 0;
  int stationList[4] = {12, 18, 12, 18};

  TDirectory* stat12Dir = outFile->mkdir("Station12"); 
  TDirectory* stat18Dir = outFile->mkdir("Station18"); 
  TDirectory* uncorr12 = stat12Dir->mkdir("Uncorrected"); 
  TDirectory* uncorr18 = stat18Dir->mkdir("Uncorrected"); 

  TDirectory* outdir[4] = {stat12Dir, stat18Dir, uncorr12, uncorr18};
  for (auto& hBeamSpot : {hBeamSpot12, hBeamSpot18, hBeamSpot12_reco, hBeamSpot18_reco}){
    station = stationList[ii];

    // TGraphs for radial mean/width
    TGraphErrors* tgMean  = new TGraphErrors();
    TGraphErrors* tgRMS   = new TGraphErrors();
    TGraphErrors* tgVMean = new TGraphErrors();
    TGraphErrors* tgVRMS  = new TGraphErrors();
    TGraphErrors* tgPhase = new TGraphErrors();
    tgMean->SetTitle(";Time [us];Mean Rad. Pos. [mm]");
    tgRMS->SetTitle(";Time [us];RMS of Rad. Pos. [mm]");
    tgVMean->SetTitle(";Time [us];Mean Ver. Pos. [mm]");
    tgVRMS->SetTitle(";Time [us];RMS of Ver. Pos. [mm]");
    tgPhase->SetTitle(";Time [us]; average phase [mrad]");
    tgMean->SetMarkerStyle(20);
    tgMean->SetMarkerSize(0.4);
    tgRMS->SetMarkerStyle(20);
    tgRMS->SetMarkerSize(0.4);
    tgPhase->SetMarkerStyle(20);
    tgPhase->SetMarkerSize(0.4);
    tgMean->GetYaxis()->SetTitleSize(0.08);
    tgMean->GetYaxis()->SetTitleOffset(0.5);
    tgMean->GetYaxis()->SetLabelSize(0.08);
    tgMean->GetYaxis()->SetNdivisions(505);
    tgRMS->GetYaxis()->SetTitleSize(0.08);
    tgRMS->GetYaxis()->SetTitleOffset(0.5);
    tgRMS->GetYaxis()->SetLabelSize(0.08);
    tgRMS->GetXaxis()->SetTitleSize(0.08);
    tgRMS->GetXaxis()->SetTitleOffset(0.9);
    tgRMS->GetXaxis()->SetLabelSize(0.08);  
    
    // Square canvas for beam spot
    TCanvas* cBeamSpot = new TCanvas("cBeamSpot","cBeamSpot",618,600);
    cBeamSpot->SetRightMargin(0.12);
    cBeamSpot->SetTopMargin(0.08);
    cBeamSpot->SetBottomMargin(0.08);
    
    // Rectangle canvas for Mean & RMS
    TCanvas* cRadial = new TCanvas("cRadial", "cRadial", 618, 600);
    cRadial->SetRightMargin(0.08);
    cRadial->SetLeftMargin(0.12);
    cRadial->SetTopMargin(0.08);
    cRadial->SetBottomMargin(0.08);
    
    TCanvas* cMeanRMS = new TCanvas("cMeanRMS", "cMeanRMS", 618, 600);
    cMeanRMS->Divide(1,2,1e-5,1e-5);
    cMeanRMS->cd(1);
    gPad->SetTopMargin(0.16);
    gPad->SetBottomMargin(1e-5);
    gPad->SetRightMargin(0.05);
    cMeanRMS->cd(2);
    gPad->SetTopMargin(1e-5);
    gPad->SetBottomMargin(0.16);
    gPad->SetRightMargin(0.05);
    gPad->SetTickx();
    
    TCanvas* cPhase = new TCanvas("cPhase", "cPhase", 800, 600);

    // Loop over z-axis (time)
    for(int i = 1; i <= hBeamSpot->GetNbinsZ(); i ++){

      double time = hBeamSpot->GetZaxis()->GetBinCenter(i);
      
      if(time < 4.9 or time > 500.0) continue;
      
      // Beam Spot (2D) plot
      hBeamSpot->GetZaxis()->SetRange(i,i);
      TH2D* hProj = (TH2D*)hBeamSpot->Project3D(Form("yx_%d",i));  // You'd've thought this should be xy but this gives the right pictures!
      cBeamSpot->cd();
      hProj->SetTitle(Form("Time since injection: %.1f us;Radial Position [mm]; Vertical Position [mm]",time));
      hProj->GetXaxis()->SetTitleOffset(1);
      hProj->GetYaxis()->SetTitleOffset(1);
      hProj->GetZaxis()->SetRangeUser(0, 100*exp(-(time-5)/64.4));  // Scale with exponential decay (set as 100 as 5 us)
      hProj->SetStats(0);
      
      //hProj->Draw("COLZ");
      //cBeamSpot->SaveAs(Form("Images/BeamSpot_Slice%03d.png",i));
      
      //convolute current beam spot with phase to get average phase
      double avgPhase = 0.0;
      double nTracksTot = 0.0;
      for (int xbin(1); xbin < nBinsX+1; xbin++){
	for (int ybin(1); ybin < nBinsY+1; ybin++){
	  double x = hProj->GetXaxis()->GetBinCenter(xbin);
	  double y = hProj->GetYaxis()->GetBinCenter(ybin);
	  
	  double nTracks = hProj->GetBinContent(xbin, ybin);
	  double phase = pMap->GetBinContent(xbin, ybin);
	  
	  //cout << "x: " << x << " y: " << y << " phase: " << phase << " tracks: " << nTracks << "\n";
	  
	  avgPhase += nTracks * phase;
	  nTracksTot += nTracks;
	}
      }


      if (nTracksTot > 0){

	int n = tgPhase->GetN();
	double timeErr = 0.0;
	avgPhase = avgPhase / nTracksTot;
	
	tgPhase->SetPoint(n, time, avgPhase);

	//reloop over to calculate error (needs the average)
	double avgPhaseErr = 0.0;
	for (int xbin(1); xbin < nBinsX+1; xbin++){
	  for (int ybin(1); ybin < nBinsY+1; ybin++){
	    double x = hProj->GetXaxis()->GetBinCenter(xbin);
	    double y = hProj->GetYaxis()->GetBinCenter(ybin);

	    double nTracks = hProj->GetBinContent(xbin, ybin);
	    double phase = pMap->GetBinContent(xbin, ybin);
	    
	    avgPhaseErr += nTracks * ( (phase * phase) + (avgPhase * avgPhase) - 2*phase * avgPhase );
	  }
	}
	avgPhaseErr /= (nTracksTot*nTracksTot);
	avgPhaseErr = sqrt(avgPhaseErr);
	tgPhase->SetPointError(n, timeErr, avgPhaseErr);
      }

      // Radial projection (update of current video)
      cRadial->cd();
      TH1D* hRadial = hProj->ProjectionX(Form("px_%d",i));
      hRadial->SetTitle(Form("Time since injection: %.1f us;Radial Position [mm]; Entries",time));

      // Radial Mean & RMS
      tgMean->SetPoint(tgMean->GetN(), time, hRadial->GetMean());
      tgRMS->SetPoint(tgRMS->GetN(), time, hRadial->GetRMS());
      
      tgMean->SetPointError(tgMean->GetN()-1, 0.0, hRadial->GetMeanError());
      tgRMS->SetPointError(tgRMS->GetN()-1, 0.0, hRadial->GetRMSError());
      
      TH1D* hVertical = hProj->ProjectionY(Form("py_%d",i));
      hVertical->SetTitle(Form("Time since injection: %.1f us;Vertical Position [mm]; Entries",time));
      
      // Radial Mean & RMS
      tgVMean->SetPoint(tgVMean->GetN(), time, hVertical->GetMean());
      tgVRMS->SetPoint(tgVRMS->GetN(), time, hVertical->GetRMS());
      
      tgVMean->SetPointError(tgVMean->GetN()-1, 0.0, hVertical->GetMeanError());
      tgVRMS->SetPointError(tgVRMS->GetN()-1, 0.0, hVertical->GetRMSError());

    }

    cPhase->cd();
    tgPhase->Draw("AP");
    cPhase->SaveAs(Form("Images/MeanPhase_stat%i%s.png", station, app.c_str()));

    outdir[ii]->cd();
    tgMean->SetName("tgRadMean");
    tgRMS->SetName( "tgRadRMS");
    tgVMean->SetName("tgVerMean");
    tgVRMS->SetName( "tgVerRMS");
    tgPhase->SetName("tgPhase");
    tgMean->Write();
    tgRMS->Write();
    tgVMean->Write();
    tgVRMS->Write();
    tgPhase->Write();
    
    ii++;
  } //loop over stations
  outFile->Close();

}

//hard coded default to run all run 1
//must be on gm2ucl to run this
void convolution(){
  //  convolution("/gm2/data/users/glukicov/Run1_QualityTrees/60h_in1File/60h_all_quality_tracks.root", "phase.root", 1, "_60hr");
  //  convolution("/home/gm2/Trees/gm2_9day.root", "phase.root", 2, "_9day");
  //  convolution("/home/gm2/Trees/gm2_HK.root", "phase.root", 3, "_HK");
  convolution("/home/gm2/Trees/gm2_EndGame.root", "phase.root", 4, "_EG");
}

