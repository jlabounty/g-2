#include <stdio.h>
void FWanalysis(std::string fileName = "run2Equalization/run2Iteration4.root", int xtalToPlot = 145, std::string foutName = "sampleFitsMay8.root") {
	//gStyle->SetOptStat(0);
	gStyle->SetOptFit(1111);

	TFile* f = new TFile(fileName.c_str());
	TH1D* gainCoeff = new TH1D("gainCoeff","Gain coefficients",100,0.0,1.0);

	//TFile* fout = new TFile("sampleFits8May.root","RECREATE");
	TFile* fout = new TFile(foutName.c_str(),"RECREATE");

	TGraph* linTermPerChan = new TGraph();
	TGraph* constPerChan = new TGraph();
	TGraph* linErrorPerChan = new TGraph();
	TGraph* quadTermPerChan = new TGraph();
	TGraph* chi2PerChan = new TGraph();
	TGraph* FW8pePerChan = new TGraph();
	TGraph* FW8meanPerChan = new TGraph();
	std::vector<double> FW8means;
	int plotIndex = 0;
	std::vector<TGraph*> problemCrystals;

	std::vector<double> gainValues;

	TF1 *f1 = new TF1("userPol2","[0] + [1]*x + [2]*x*x",0,100000);
	TF1 *f2 = new TF1("userPol1","[0] + [1]*x",0,100000);
	f2->SetLineColor(2);

	f1->SetParLimits(1,0,100000);
	for (unsigned int i = 0; i < 1296; i++) {
		f1->SetParameters(0.0,5.0,0.0);
		std::cout<<"crystal num : "<< i << std::endl;
		TH2D* tempHist;
		f->GetObject(Form("fwAnalysis/laserIntensity%i", i),tempHist);
		TGraphErrors* tempGraph = new TGraphErrors();
		for(unsigned int k = 1; k < tempHist->GetXaxis()->GetNbins()+1; k++){
			if(k!=tempHist->GetXaxis()->GetNbins() + 1){
				TH1D* tempProj = tempHist->ProjectionY(Form("_py%i",i*10 + k),k,k,"");
				//tempProj->Draw();

				if(tempProj->GetEntries() > 100 ){


					if(tempProj->Integral(1,10) > 0)
					//if(tempProj->GetMean() > 1000)
					{
						tempProj->Fit("gaus","RQ","",tempProj->GetMean() - 2*tempProj->GetRMS(), tempProj->GetMean() + 2*tempProj->GetRMS());
					}
					else
					{
						tempProj->Fit("gaus","RQ","",200, 19800);
					}

					/*if(tempProj->GetMean() < 2000){
					  std::cout<<"FOUND it"<<std::endl;
					  }*/


					int pointNum = tempGraph->GetN();
					//std::cout << pointNum << std::endl;
					if(tempProj->GetFunction("gaus") ){

						double tempMean = tempProj->GetFunction("gaus")->GetParameter(1);
						double tempVar = tempProj->GetFunction("gaus")->GetParameter(2);
						tempProj->Fit("gaus","Q","",tempMean-3*tempVar, tempMean+3*tempVar);
						tempGraph->SetPoint(pointNum,tempProj->GetFunction("gaus")->GetParameter(1),
								pow(tempProj->GetFunction("gaus")->GetParameter(2),2));

						tempGraph->SetPointError(pointNum,tempProj->GetFunction("gaus")->GetParError(1),
								2*tempProj->GetFunction("gaus")->GetParameter(2)*tempProj->GetFunction("gaus")->GetParError(2));
					}
					if(k == 2){
						if(tempProj->GetFunction("gaus")){
							FW8means.push_back(tempProj->GetFunction("gaus")->GetParameter(1));
						}else{
							FW8means.push_back(0);
						}
					}
				}else{
					int pointNum = tempGraph->GetN();
					//tempGraph->SetPoint(pointNum, pointNum*0.01, pointNum*0.005);
				}
			}
		}

		if( tempGraph->GetN() > 0){ 
		//if(i != 758){ //758 = dead crystal.
		//if(i != 421 and i !=758){
		//if(i != 422 and i !=758){
			std::cout<<"Entries: " << tempGraph->GetN() << std::endl;
			double xmin = TMath::MinElement(tempGraph->GetN(),tempGraph->GetX());
			double xmax = TMath::MaxElement(tempGraph->GetN(),tempGraph->GetX());

			//if we are not saturating, use the full range. If we are, lets restrict it.
			f2->SetParameters(0,1);
			tempGraph->Fit("userPol1","RQ","",xmax*0.7,xmax*1.7);
			std::cout << "Slope(" << i << "): " << f2->GetParameter(1) << std::endl;
			if(f2->GetParameter(1) < 1)
			{
				tempGraph->Fit("userPol2","RQ","",xmin*0.9,xmax*(.75 + f2->GetParameter(1)*0.01 ) );
			}
			else
			{
				tempGraph->Fit("userPol2","RQ","",xmin*0.9,xmax*1.99);
			}
			std::cout << "    ";
			for(int useless = 0; useless < tempGraph->GetN(); useless++)
			{
				Double_t x,y;
				tempGraph->GetPoint(useless, x, y);
				std::cout << "(" << x << " , " << y << "); ";
			}
			std::cout << std::endl;
			constPerChan->SetPoint(i,i, tempGraph->GetFunction("userPol2")->GetParameter(0));
			linTermPerChan->SetPoint(i,i, std::min(1.1, 1.0 / tempGraph->GetFunction("userPol2")->GetParameter(1)));
			quadTermPerChan->SetPoint(i,i,tempGraph->GetFunction("userPol2")->GetParameter(2));
			linErrorPerChan->SetPoint(i,i,std::min(tempGraph->GetFunction("userPol2")->GetParError(1),5.0));
			chi2PerChan->SetPoint(i,i,tempGraph->GetFunction("userPol2")->GetChisquare());
			//FW8pePerChan->SetPoint(i,i,std::min(FW8means.at(i) / tempGraph->GetFunction("userPol2")->GetParameter(1), 10000.0));
			//FW8meanPerChan->SetPoint(i,i,FW8means.at(i));
			gainValues.push_back(std::min(1.1, 1.0 / tempGraph->GetFunction("userPol2")->GetParameter(1)));
			gainCoeff->Fill(std::min(1.1, 1.0 / tempGraph->GetFunction("userPol2")->GetParameter(1)));
		}else{
			tempGraph->Fit("userPol2","Q","",-1.0,10);
			constPerChan->SetPoint(i,i, 800.0);
			linTermPerChan->SetPoint(i,i, 1.0);
			quadTermPerChan->SetPoint(i,i, 0.0);
			linErrorPerChan->SetPoint(i,i, 5.0);
			chi2PerChan->SetPoint(i,i, 500.0);
			//FW8pePerChan->SetPoint(i,i,std::min(FW8means.at(i) / tempGraph->GetFunction("userPol2")->GetParameter(1), 10000.0));
			//FW8meanPerChan->SetPoint(i,i,FW8means.at(i));
			gainValues.push_back(1.1);
			gainCoeff->Fill(1.1);
		}


		if(true){//i == xtalToPlot){
			if(i == xtalToPlot){
				plotIndex = problemCrystals.size();
			}
			/*std::cout << "Look at channel : " << std::to_string(i) << std::endl;
			  std::cout << "chi2 is : " << std::to_string(tempGraph->GetFunction("userPol2")->GetChisquare()) << std::endl;
			  std::cout << "linear term is : " << std::to_string(tempGraph->GetFunction("userPol2")->GetParameter(1)) << std::endl;
			  std::cout << "error on linear term is : " << std::to_string(tempGraph->GetFunction("userPol2")->GetParError(1)) << std::endl;
			  std::cout << "quadratic term is : " << std::to_string(tempGraph->GetFunction("userPol2")->GetParameter(2)) << std::endl;
			  tempGraph->SetTitle(Form("channel %i; mean; var",i));*/

			problemCrystals.push_back(tempGraph);
			problemCrystals.at(i)->SetTitle(Form("Calo %i, crystal %i; fitted mean; variance",(int)i/54 + 1, i%54));
		}

		}

		TCanvas* c1 = new TCanvas("c1","c1",700,500);
		//linTermPerChan->GetXaxis()->SetRangeUser(-1,1296);
		//linTermPerChan->SetTitle("gain coefficient vs. channel; channel number [(caloNum - 1) * 54 + xtalNum]; pe / mean");
		//linTermPerChan->SetMarkerColor(kBlue+2);
		//linTermPerChan->SetMarkerStyle(8);
		//problemCrystals.at(plotIndex)->SetTitle(Form("Calo %i, crystal %i; fitted mean; variance",(int)xtalToPlot/54 + 1, xtalToPlot%54));
		problemCrystals.at(plotIndex)->Draw("APZ");
		//linTermPerChan->Draw("APZ");
		//c1->SaveAs("evenOddPerChan.pdf");

		TCanvas* c2 = new TCanvas("c2","c2",700,500);
		  linErrorPerChan->GetXaxis()->SetRangeUser(-1,1296);
		  linErrorPerChan->SetTitle("Fitted error on lin FW term vs. channel; channel number [(caloNum - 1) * 54 + xtalNum]; Fitted error");
		  linErrorPerChan->SetMarkerColor(kRed+2);
		  linErrorPerChan->SetMarkerStyle(8);
		//problemCrystals.at(1)->Draw("APZ");
		linErrorPerChan->Draw("APZ");
		//c2->SaveAs("fitErrorPerChan.pdf");

		TCanvas* c3 = new TCanvas("c3","c3",700,500);
		chi2PerChan->GetXaxis()->SetRangeUser(-1,1296);
		chi2PerChan->SetTitle("Fit chi2 vs. channel; channel number [(caloNum - 1) * 54 + xtalNum]; Chi2");
		chi2PerChan->SetMarkerColor(kViolet+2);
		chi2PerChan->SetMarkerStyle(8);
		//problemCrystals.at(plotIndex)->Draw("APZ");
		chi2PerChan->Draw("APZ");
		//c3->SaveAs("chi2PerChan.pdf");

		TCanvas* c4 = new TCanvas("c4","c4",700,500);

		quadTermPerChan->GetXaxis()->SetRangeUser(-1,1296);
		quadTermPerChan->SetTitle("Quadratic FW term vs. channel; channel number [(caloNum - 1) * 54 + xtalNum]; quadratic term");
		quadTermPerChan->SetMarkerColor(kOrange+2);
		quadTermPerChan->SetMarkerStyle(8);
		//problemCrystals.at(3)->Draw("APZ");
		quadTermPerChan->Draw("APZ");
		//c3->SaveAs("chi2PerChan.pdf");

		TCanvas* c5 = new TCanvas("c5","c5",700,500);

		FW8pePerChan->GetXaxis()->SetRangeUser(-1,1296);
		FW8pePerChan->SetTitle("N pe vs. channel; channel number [(caloNum - 1) * 54 + xtalNum]; N pe");
		//FW8meanPerChan->SetTitle("mean at FW8 vs. chan; channel number [(caloNum - 1) * 54 + xtalNum]; mean");
		FW8pePerChan->SetMarkerColor(kMagenta+2);
		FW8pePerChan->SetMarkerStyle(8);
		FW8meanPerChan->SetMarkerColor(kGreen+2);
		FW8meanPerChan->SetMarkerStyle(8);
		constPerChan->GetXaxis()->SetRangeUser(-1,1296);
		constPerChan->SetTitle("Constant FW term vs. channel; channel number [(caloNum - 1) * 54 + xtalNum]; const term");
		constPerChan->SetMarkerStyle(8);
		constPerChan->SetMarkerColor(kCyan+2);
		constPerChan->Draw("APZ");
		//problemCrystals.at(plotIndex)->Draw("APZ");
		//FW8pePerChan->Draw("APZ");
		//FW8meanPerChan->Draw("APZ");
		//c3->SaveAs("chi2PerChan.pdf");

		//TCanvas* c6 = new TCanvas("c6","c6",700,500);
		//FW8pePerChan->Draw("APZ");
		

		TCanvas* c7 = new TCanvas("c7","c7",700,500);
		//problemCrystals.at(plotIndex)->Draw("APZ");
		gStyle->SetOptStat(0);
		gStyle->SetOptFit(1111);
		gainCoeff->SetTitle("Gain coefficients: 8 May; calculated gain coefficient; N");
		gainCoeff->Fit("gaus","","",gainCoeff->GetMean() - 2*gainCoeff->GetRMS(),gainCoeff->GetMean()+2*gainCoeff->GetRMS());
		gainCoeff->Draw();

		std::cout << "BEGIN_PROLOG\n";
		std::cout << "gain_coefficients : {\n";
		for(unsigned int p = 0; p < 1296; p++){
			if(p%54 == 0){
				std::cout << "  calo"<<std::to_string((int)(p/54) + 1)<<" : {\n";
			}
			std::cout<<"    xtal"<<std::to_string(p%54)<<" : "<<Form("%0.3f",gainValues.at(p));
			if(p%54 == 53 && p != 1295){
				std::cout<<"\n     }\n";
				//std::cout<<"  },\n";
			}else if(p == 1295){
				std::cout<<"\n    }\n";
				//std::cout<<"  }\n";
			}else{
				std::cout<<"\n";
			}
			//std::cout<<Form("%0.3f",gainValues.at(p))<<std::endl;
		}
		std::cout<<"}\n";
		std::cout<<"END_PROLOG";

		fout->cd();
		  for(unsigned int k = 0; k < problemCrystals.size(); k++){
		  problemCrystals.at(k)->Write(Form("calo%ixtal%i",(int)k/54 + 1, k%54));
		  }
		fout->Close();


	}
