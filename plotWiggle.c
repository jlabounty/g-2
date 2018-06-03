void plotWiggle(std::string filename){

    TFile *file = new TFile(filename.c_str());
    TTree *tree = (TTree*)file->Get("Events");

    TH1D *energy = new TH1D("energy","energy",100,0,4000);
    TH1D *time = new TH1D("time","time",4700,0,701.24);
    TH1D *energyWithCut = new TH1D("energyWithCut","energyWithCut",100,0,4000);
    TH1D *timeWithCut = new TH1D("timeWithCut","timeWithCut",4700,0,701.24);

    TCut cut("gm2calo::CaloClusterArtRecords_hitClusterDAQ_cluster_reconstruct.obj.energy>1800");

    // time is in ADC clock tick unit [1 c.t. = 1.25 ns], convert it to microsecond for convenience
    tree->Draw("gm2calo::CaloClusterArtRecords_hitClusterDAQ_cluster_reconstruct.obj.energy>>energy","","goff");
    tree->Draw("gm2calo::CaloClusterArtRecords_hitClusterDAQ_cluster_reconstruct.obj.time*1.25/1000>>time","","goff");
    tree->Draw("gm2calo::CaloClusterArtRecords_hitClusterDAQ_cluster_reconstruct.obj.energy>>energyWithCut",cut,"goff");
    tree->Draw("gm2calo::CaloClusterArtRecords_hitClusterDAQ_cluster_reconstruct.obj.time*1.25/1000>>timeWithCut",cut,"goff");

    TCanvas *c1 = new TCanvas("c1","c1",1200,800);
    c1->Divide(2,2);

    c1->cd(1);
    energy->Draw();

    c1->cd(2);
    time->Draw();

    c1->cd(3);
    energyWithCut->Draw();

    c1->cd(4);
    timeWithCut->Draw();


	TCanvas *c2 = new TCanvas();
		c2->cd();
		c2->SetLogy();
	timeWithCut->Draw();
/*
	TF1 *fit1 = new TF1("fit1","[0]*TMath::Exp(-1*x/[1]) * ( -1*[2]*TMath::Cos(2*TMath::Pi()*[3]*x+[4]) + 1 )",0,300);
		fit1->SetParameter(0,10);
		fit1->SetParameter(1,64.4);
		fit1->SetParameter(2,0.4);
		fit1->SetParameter(3,229);
		fit1->SetParameter(4,1);
	timeWithCut->Fit("fit1","R");
*/
	TF1 *fit = new TF1("fit","[0]*exp(-x/[1])*(1+[2]*cos(2*TMath::Pi()*[3]*x+[4]))",40,250);
	fit->SetParameters(20, 64.4,0.4,0.229,0);
	fit->SetNpx(1000);


	timeWithCut->Fit("fit","REML");
	c2->Update();

/*
	TCanvas *c3 = new TCanvas();
	TH1F *hresid = new TH1F("hresid","",nbins,0,timeWithCut->GetMaximum());
	int nbins = timeWithCut->GetSize();
	for(int i = 0; i < nbins; i++)
	{
		float x=timeWithCut->GetBinCenter(i);
		float y=timeWithCut->Eval(x);
		hresid->Fill(y);	
	}
	c3->cd();
	hresid->Draw();
*/
}
