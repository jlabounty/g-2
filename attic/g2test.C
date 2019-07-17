using namespace std;
#include <iostream>
#include "TFile.h"
#include "TCanvas.h"
#include "TGraph.h"
#include "TH1F.h"
#include "TF1.h"
#include "TNtuple.h"
#include <vector>

int g2test()
{

	//open file
	TFile *f1 = new TFile("./gminus2_g4beamline_400k-evts.root");	

	//Get the two NTuples
	TNtuple *electrons = (TNtuple*)f1->Get("Electrons");
	TNtuple *muons = (TNtuple*)f1->Get("Muons");
	

	TCanvas *c1 = new TCanvas();
	TH1F *h1 = new TH1F("h1","Muon Decay Time",1000,0,500000);
	for(int i = 0; i < muons->GetEntries(); i++)
	{
		muons->GetEvent(i);
		h1->Fill(muons->GetLeaf("t")->GetValue());
	}
	h1->Draw();
	TF1 *fit = new TF1("decay","
	
	
/*
	const int size = muons->GetEntries();
	vector<double> electron_px, electron_py;

	for(int i = 0; i < muons->GetEntries(); i++)
	{
		muons->GetEvent(i);
		electrons->GetEvent(i);
		electron_px.push_back( electrons->GetLeaf("Px")->GetValue() );
		electron_py.push_back( electrons->GetLeaf("Py")->GetValue() );

	}

	TCanvas *c = new TCanvas();
		c->cd();
	TGraph *gr = new TGraph(size,&electron_px[0],&electron_py[0]);
	gr->Draw();
*/

	return 0;
}
