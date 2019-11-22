#include <fstream>
#include <string>

void calibrateXtals(std::string fileName = "lostMuonTree/combinedLostMuonTree.root"){
    
    
    int caloLow = 1;
    int caloHigh = 24;
    std::vector<double> laserConstants;
    std::ifstream file("FWConstants.txt");
    if (file) {
        double value;
        
        // read the elements in the file into a vector
        while ( file >> value ) {
            //std::cout<< "value is : " << value <<std::endl;
            laserConstants.push_back(value);
        }
    }
    //return;

    TFile* f1 = new TFile(fileName.c_str());
    gStyle->SetOptStat(0);
    double targetE = 170.0;
    std::vector<double> scales;
    std::vector<TH1D*> runningCalo;
    
    TTree* t1 = (TTree*)f1->Get("lostMuonTree/lostMuonCoincidences");
    
    t1->Draw("xtalEnergy:(caloNum-1)*54 + xtalNum>>energyXtal(1296,-0.5,1295.5,400,0.0,3000.0)","coinNum > 0 && nHit == 1" );
    TH2D* allEnergies = (TH2D*)gDirectory->Get("energyXtal");
    
    
    TH1D* uncalibratedAllXtals = new TH1D("uncalibratedAllXtals","All crystals",75,0.0,750.0);
    
    TH1D* calibratedXtals = new TH1D("calibratedXtals","All crystals; Energy [MeV]; N / 5 MeV",75,0.0,750.0);
    
    double laserFactor = 0.2749;
    std::vector<int> problemXtals = {3*54+6, 3*54 + 1, 5*54+47, 16*54 + 18, 16*54 + 27, 16*54 + 5, 16*54+4, 16*54 + 45, 49, 45 + 54, 3*54 + 49, 8*54+18, 9*54+6, 11*54 + 2, 18*54 + 27, 18*54 + 7, 21*54 + 4, 4*54 + 46, 47 + 54, 48+54, 5*54 + 47, 5*54 + 1};
    std::vector<int> lower = { 400, 375, 200, 450, 425, 350, 500, 350, 450, 150, 420, 350, 500, 450, 420, 420, 400, 200,350, 250, 200, 300};
    std::vector<int> upper = { 600, 575, 600, 450, 620, 600, 650, 550, 640, 850, 675, 600, 650, 750, 575, 600, 600, 400, 650, 550, 600, 600};
    //std::vector<TH2D*> allEnergies;
    /*for(int hit = 0; hit < 3; hit++){
        
        allEnergies.push_back((TH2D*)f1->Get(Form("lostMuonET/lostMuonE%i",hit)));
        
    }*/
    
    TH1D* projHist = allEnergies->ProjectionY(Form("_py%i",1),1,-1,"");
    /*projHist->Add(allEnergies.at(0)->ProjectionY(Form("_py%i",0),1,-1,""));
    projHist->Add(allEnergies.at(2)->ProjectionY(Form("_py%i",2),1,-1,""));*/
    double tempMean = projHist->GetMean();
    double tempSig = projHist->GetRMS();
    int binmax = projHist->GetMaximumBin();
    double peak = projHist->GetXaxis()->GetBinCenter(binmax);
    projHist->Fit("gaus","Q","",peak-75, peak+75);
    
    double avgPeak = peak;
    
    double scaleFactor = targetE / projHist->GetFunction("gaus")->GetParameter(1);
    std::cout << "average calibration constant is : " << Form("%0.3f",scaleFactor)<<std::endl;
    
    for(int k = 1; k <= projHist->GetXaxis()->GetNbins(); k++){
        
        uncalibratedAllXtals->Fill(projHist->GetXaxis()->GetBinCenter(k) * scaleFactor,
            projHist->GetBinContent(k));
        
    }
    
    TCanvas* c2 = new TCanvas("c2","c2",1800,1200);
    
    for(int xIdx = (caloLow-1)*54 + 1; xIdx <= caloHigh*54; xIdx++){//allEnergies.at(0)->GetXaxis()->GetNbins()
        projHist->Clear();
        projHist=allEnergies->ProjectionY(Form("_py%i",xIdx*10+0),xIdx,xIdx,"");
        /*for(int hit = 1; hit < allEnergies.size(); hit++){
            
            projHist->Add(allEnergies.at(hit)->ProjectionY(Form("_py%i",xIdx*10+hit),xIdx,xIdx,""));
            
        }*/
        
        
        //projHist = allEnergies->ProjectionY(Form("_py%i",xIdx),xIdx,xIdx,"");
        //projHist->Rebin(4);
        
        if(projHist->GetEntries() > 10){
            tempMean = projHist->GetMean();
            tempSig = projHist->GetRMS();
            binmax = projHist->GetMaximumBin();
            peak = projHist->GetXaxis()->GetBinCenter(binmax);
            double peakValue = projHist->GetBinContent(binmax);
            while(peakValue < 50){
                projHist->Rebin(2);
                binmax = projHist->GetMaximumBin();
                peak = projHist->GetXaxis()->GetBinCenter(binmax);
                peakValue = projHist->GetBinContent(binmax);
                
            }
            double min = std::min(0.0,peak - 60);
            double max = std::max(3000.0,peak + 60);
            
            if(std::find(problemXtals.begin(),problemXtals.end(),xIdx-1)!=problemXtals.end()){
                int pos = std::find(problemXtals.begin(),problemXtals.end(),xIdx-1) - problemXtals.begin();
                min = lower.at(pos);
                max = upper.at(pos);
            }
            
            projHist->Fit("gaus","Q","",min, max);
            min = std::max(0.0,projHist->GetFunction("gaus")->GetParameter(1) - 1.5*projHist->GetFunction("gaus")->GetParameter(2));
            max = std::min(3000.0,projHist->GetFunction("gaus")->GetParameter(1) + 1.4*projHist->GetFunction("gaus")->GetParameter(2));
            delete projHist->GetFunction("gaus");
            projHist->Fit("gaus","Q","",min, max);
            runningCalo.push_back(projHist);
            scaleFactor = targetE / projHist->GetFunction("gaus")->GetParameter(1);
            scales.push_back(scaleFactor);
            for(int k = 1; k <= projHist->GetXaxis()->GetNbins(); k++){
                
                calibratedXtals->Fill(projHist->GetXaxis()->GetBinCenter(k) * scaleFactor,
                    projHist->GetBinContent(k));
                
            }
        }else{
            //std::cout<<"Not enough events in channel : " << xIdx << std::endl;
            scales.push_back(1.0);
            runningCalo.push_back(projHist);
        }
        TLine* line1;
        if(xIdx%54 == 0){
            c2->Clear();
            c2->Divide(9,6);
            for(int drawdx = 0; drawdx < 54; drawdx++){
                c2->cd(54-drawdx);
                if(runningCalo.at(drawdx)->GetFunction("gaus")){
                    runningCalo.at(drawdx)->GetFunction("gaus")->SetLineWidth(1);
                }
                double peakValue = runningCalo.at(drawdx)->GetBinContent(runningCalo.at(drawdx)->GetMaximumBin());
                //std::cout << "laser factor : " << laserConstants.at(xIdx-54+drawdx) << std::endl;
                double xValue = avgPeak * laserFactor / laserConstants.at(xIdx-54+drawdx) ;
                //std::cout << "xValue is : " << xValue << std::endl;
                line1 = new TLine( xValue, 0, xValue , 1.1*peakValue);
                line1->SetLineColorAlpha(kBlack,0.25);
                runningCalo.at(drawdx)->GetYaxis()->SetRangeUser(0,1.1*peakValue);
                runningCalo.at(drawdx)->GetXaxis()->SetRangeUser(0,2000.0);
                runningCalo.at(drawdx)->SetTitle(Form("xtal %i",drawdx));
                
                runningCalo.at(drawdx)->Draw();
                line1->Draw("same");
                c2->Update();
            }
            c2->Draw();
            c2->SaveAs(Form("caloPlotsTree/notFirstHit_1Xtal_calo%i.pdf",(int)(xIdx/54)));
            c2->Clear();
            runningCalo.clear();
        }
        
    }
    /*calibratedXtals->SetLineColor(kRed);
    TCanvas* c1 = new TCanvas("c1","c1",700,500);
    TLegend* leg1 = new TLegend(0.6,0.6,0.85,0.85);
    leg1->AddEntry(uncalibratedAllXtals,"uncalibrated","l");
    leg1->AddEntry(calibratedXtals,"calibrated","l");
    calibratedXtals->Draw("hist");
    uncalibratedAllXtals->Draw("hist same");
    leg1->Draw();
    c1->SaveAs("calibrationComparison.pdf");*/
    
    TGraph* calibGain = new TGraph();
    for(unsigned int k = 0; k < laserConstants.size(); k++){
        if(k%100 == 0){
            std::cout<< "point "<<k << std::endl;
        }
        //std::cout<< "laser "<<laserConstants.at(k) << std::endl;
        //std::cout<< "calib "<<scales.at(k) << std::endl;
        calibGain->SetPoint(k, 1.0 / laserConstants.at(k), 1.0 / scales.at(k));
        
    }
    
    TCanvas* c3 = new TCanvas("c3","c3",700,500);
    calibGain->SetTitle("gain factor vs. FW constant; FW gain coefficient; calib scale");
    calibGain->SetMarkerStyle(7);
    calibGain->Draw("apz");
    c3->Draw();
    
    
    /*std::cout<<"BEGIN_PROLOG"<<std::endl;
    std::cout<<"absolute_calibration_constants : {"<<std::endl;
    for(int calo = 1; calo <= 24; calo++){
        std::cout<<Form("\tcalo%i : {",calo)<<std::endl;
        for(int xtal = 0; xtal < 54; xtal++){
            
            std::cout<<Form("\t\txtal%i : %0.3f",xtal,scales.at(54*(calo-1)+xtal))<<std::endl;
            
        }
        
        std::cout<<"\t}"<<std::endl;
        
    }
    std::cout<<"}"<<std::endl;
    std::cout<<"END_PROLOG";*/
    
}
