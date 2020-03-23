//#include "gm2Style.C"
#include "gm2Labels.C"

int testPlot()
{
	//SetGm2Style();
	//TCanvas *c = new TCanvas();
	TFile *f = TFile::Open("./gm2nearline_hists_run24307_00461.root");
	TTree *t = (TTree*)f->Get("nearlineHistTree/eventTree");
	//t->Print();
	//f->ls();

	TCanvas *c = g2Canvas("hi", 600);
	TF1 *f1 = new TF1("f1","pol1", 0, 700);
	f1->SetLineColor( g2ColorPicker() );
	TH1D *h = new TH1D("h","Sin(x)/x Random; Time [#mus]; N / 1 #mus", 700, 0,700);
	t->Draw("time*1.25/1000.>>h","energy < 6000","goff");
	h->Fit("f1","REMB");
	h->Draw();
	f1->Draw("SAME");
	c->SetLogy();
	gm2Label(0.4,0.7,"Default 1D Plot");
	gm2Logo(0.5,0.76);

	TLegend *leg = new TLegend(0.2,0.2,0.5,0.4);
	leg->AddEntry("h","Nearline Time Spectrum","l");
	leg->AddEntry("f1","Linear Fit","l");
	leg->Draw();

	c->Draw();

	TCanvas *c2 = g2Canvas("hi2", 600);
	initializeColors();
	TF1* tfi_1 = new TF1("tfi_1","pol1", 0, 10);
	TF1* tfi_2 = new TF1("tfi_2","pol1", 0, 10);
	TF1* tfi_3 = new TF1("tfi_3","pol1", 0, 10);
	TF1* tfi_4 = new TF1("tfi_4","pol1", 0, 10);
	TF1* tfi_5 = new TF1("tfi_5","pol1", 0, 10);
	TF1* tfi_6 = new TF1("tfi_6","pol1", 0, 10);
	std::vector<TF1*> colorFunctions = {tfi_1, tfi_2, tfi_3, tfi_4, tfi_5, tfi_6 };
	for(int i = 0; i < 6; i++)
	{
		colorFunctions[i]->SetLineColor( g2ColorPicker() );
		colorFunctions[i]->SetNpx(1000);
		colorFunctions[i]->SetParameter(0,0);
		colorFunctions[i]->SetParameter(1,(i+1)/10.);
		if(i > 0) 
		{
			colorFunctions[i]->Draw("same");
		}
		else
		{
			colorFunctions[i]->Draw();
		}
	}
	gm2Label(0.3,0.2,"Default Line Colors");
	gm2Logo(0.6,0.3);
	gm2Watermark("Preliminary");
	c2->Draw();

	TCanvas *c3 = g2Canvas2D("hi3", 600);
	TH2D *h2 = new TH2D("h2", "Title; x [xtals]; y [xtals]; Energy [MeV]", 
		90,0,9,60,0,6);
	t->Draw("y:x>>h2","energy < 6000 && energy > 1700","goff");
	h2->Draw("colz");
	c3->SetLogz();
	gm2Label(0.05,0.05,"Default 2D Canvas");
	c3->Draw();

	TCanvas *c4 = g2Canvas3D("hi4", 600);
	h2->Draw("lego2");
	c4->SetLogz();
	gm2Label(0.1,0.05,"Default 3D Canvas");
	c4->Draw(); 
	g2Print("ding", c4);

	return 0;
}
