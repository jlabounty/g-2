R__ADD_INCLUDE_PATH(/usr/local/include/eigen3)
#include "TFile.h"
#include "TH1.h"
#include "TH3.h"
#include "TFile.h"
#include "TF1.h"
#include <iostream>
#include <Eigen/Dense>
#include <Eigen/SVD>

void calculateDeltaTConstants(){
    std::vector<std::string> fileName = {"data/calibratedDeltaT_TQ01.root","data/calibratedDeltaT_TQ01.root"};
    std::vector<std::vector<double>> constants;
    constants.resize(fileName.size());
    for(unsigned int fIdx = 0 ; fIdx < fileName.size(); fIdx++){
    std:cout<<"File number: "<<std::to_string(fIdx+1)<<std::endl;
    TFile* f1 = new TFile(fileName.at(fIdx).c_str());
    
    //std::vector<double> lastOffsets = {-0.000, -0.104, 0.768, 0.356, 0.201, 0.181, 0.553, 0.443, 0.382, 0.060, -0.102, -0.046, 0.272, 0.207, 0.132, 0.570, 0.412, 0.361, -0.041, -0.077, -0.179, 0.185, 0.204, 0.030, 0.448, 0.356, 0.319, 0.114, -0.085, -0.128, 0.321, 0.211, 0.087, 0.454, 0.496, 0.324, 0.005, -0.066, -0.093, 0.183, 0.195, 0.124, 0.443, 0.353, 0.344, 0.071, 0.009, -0.069, 0.297, 0.229, 0.177, 0.514, 0.467, 0.418 };
    std::vector<int> xtalsToFix = {0};//, 8, 24, 45, 53};
    std::vector<TGraph*> constantsPlots;
    constantsPlots.resize(xtalsToFix.size());
    std::vector<double> caloOffsets = {2.040,2.259,2.131,2.063,0.634,0.260,0.422,0.677,1.626,1.523,1.805,1.768,-0.205,-0.089,0.178,0.030,1.117,1.332,1.305,1.251,0.237,0.000,0.074,-0.108};
    int nCalos = 24;
    int whichCalo = 1;
    int nXtals = 54;
        
        constants.at(fIdx).resize(nCalos*nXtals);
    int matrixHeight = 1;
    int matrixHeight15 = 2;
    int matrixHeight22 = 2;
    for(int xIdx = 0; xIdx < nXtals; xIdx++){
        
        if(xIdx > 8){
            matrixHeight++;
        }
        if(xIdx%9 != 0){
            matrixHeight++;
        }
        
    }
    /*TH1D* beforeOffsets = new TH1D("beforeOffsets","Difference between crystal hit times, before/after offsets; delta t [ct]; N",40,-0.5,0.5);
    TH1D* afterOffsets = new TH1D("afterOffsets","Difference between crystal hit times, before/after offsets",100,-0.5,0.5);*/
    for(int xIdx = 0; xIdx < nXtals; xIdx++){
        
        if(xIdx > 8 && (xIdx - 9 != 2)){
            matrixHeight15++;
        }
        if(xIdx%9 != 0 && xIdx != 2 && (xIdx - 1 != 2)){
            matrixHeight15++;
        }
        
    }
    for(int xIdx = 0; xIdx < nXtals; xIdx++){
        
        if(xIdx > 8 && (xIdx - 9 != 33)){
            matrixHeight22++;
        }
        if(xIdx%9 != 0 && xIdx != 33 && (xIdx - 1 != 33)){
            matrixHeight22++;
        }
        
    }
    // std::cout<<"BEGIN_PROLOG"<<std::endl;
    // std::cout<<"timing_alignment_constants : {"<<std::endl;
    // //std::cout<<"matrix should be "<<matrixHeight<<" rows"<<std::endl;
    Eigen::MatrixXf m_; //matrix to decompose with SVD -- coefficients of equations
    Eigen::VectorXf rhs_; //right hand side of Ax = b -- calculated delta Ts
    
    TCanvas *c1 = new TCanvas("c1","c1",700,500);
    gStyle->SetOptStat(0);
    for(int cIdx = whichCalo; cIdx < whichCalo + nCalos; cIdx++){
        std::cout<<"Calo number : " << std::to_string(cIdx) << std::endl;
        
    for(int loopdx = 0; loopdx < xtalsToFix.size(); loopdx++){
    constantsPlots.at(loopdx) = new TGraph();
    int fixedXtal = xtalsToFix.at(loopdx);
    
        
        // std::cout<<"\tcalo"<<(cIdx)<<" : {"<<std::endl;
        // std::cout<<Form("\tglobal: %0.3f",caloOffsets.at(cIdx-1))<<std::endl;
        if(cIdx == 15){
            m_.resize(matrixHeight15,nXtals);
            rhs_.resize(matrixHeight15);
        }else if(cIdx != 15 && fIdx == 1){
            m_.resize(matrixHeight - 3,nXtals);
            rhs_.resize(matrixHeight - 3);
        }else{
            m_.resize(matrixHeight,nXtals);
            rhs_.resize(matrixHeight);
        }
        TH3D* caloTimePlot = (TH3D*)f1->Get(Form("neighboringCrystalsDeltaT/hitDeltaT%i",cIdx-1));
        int eqnCounter = 0;
        for(int xIdx = 0; xIdx < nXtals; xIdx++){
            //std::cout << "xtal index : " << xIdx << std::endl;
            if(xIdx == fixedXtal ){//lock xtal k to t=0 and xtal2 in calo 15
                for(int colIdx = 0; colIdx < nXtals; colIdx++){
                    if(colIdx == xIdx){
                        m_(eqnCounter,colIdx) = 1000; // weight for constraint
                    }else{
                        m_(eqnCounter,colIdx) = 0.0;
                    }
                }
                rhs_(eqnCounter) = 0.0;
                eqnCounter++;
            }
            
            if((xIdx == 2 && cIdx == 15) || (xIdx == 33 && cIdx != 15 && fIdx == 1)){//} || (xIdx == 6 && cIdx == 5) || (xIdx == 33 && cIdx == 22)){ // dead crystal locked to 0
                for(int colIdx = 0; colIdx < nXtals; colIdx++){
                    if(colIdx == xIdx){
                        m_(eqnCounter,colIdx) = 1000;
                    }else{
                        m_(eqnCounter,colIdx) = 0.0;
                    }
                }
                rhs_(eqnCounter) = 0.0;
                eqnCounter++;
            }

            
            if((xIdx > 8) && !(xIdx == 33 && cIdx != 15 && fIdx == 1) && !(xIdx == 42 && cIdx != 15 && fIdx == 1)){
                TH1D* tempHist = caloTimePlot->ProjectionZ(Form("_pz%i",xIdx+1),xIdx+1,xIdx+1,xIdx+1-9,xIdx+1-9,"");
                tempHist->Rebin(2);
                //std::cout<<"number of entries : " << tempHist->GetEntries() << std::endl;
                if(tempHist->GetEntries() > 50){
                    double mean = tempHist->GetMean();
                    double sig = tempHist->GetRMS();
                    tempHist->Fit("gaus","Q","",mean-1.5*sig,mean+1.5*sig);

                    if(tempHist->GetFunction("gaus")){
                        mean = tempHist->GetFunction("gaus")->GetParameter(1);
                        sig = tempHist->GetFunction("gaus")->GetParameter(2);
                    
                        tempHist->Fit("gaus","Q","", mean-2.0*sig, mean + 2.0*sig);
                    
                        mean = tempHist->GetFunction("gaus")->GetParameter(1);
                        sig = tempHist->GetFunction("gaus")->GetParError(1);
                    }else{
                        //std::cout<<"How are we here if it is converging ......"<<std::endl;
                        tempHist->Fit("gaus","","",mean-1.5*sig,mean+1.5*sig);
                    }
                    
                    /*beforeOffsets->Fill(fittedMean);
                    afterOffsets->Fill(fittedMean+lastOffsets.at(xIdx)-lastOffsets.at(xIdx-9));*/
                    if(sig == 0){
                        //std::cout << "what the fuck" << std::endl;
                    }
                    rhs_(eqnCounter) = mean/sig;
                    
                    for(int colIdx = 0; colIdx < nXtals; colIdx++){
                        if(colIdx == xIdx){
                            m_(eqnCounter,colIdx) = 1.0/sig;
                        }else if(colIdx == xIdx - 9){
                            m_(eqnCounter,colIdx) = -1.0/sig;
                        }else{
                            m_(eqnCounter,colIdx) = 0.0;
                        }
                    }
                    eqnCounter++;
                }else{
                    //std::cout<<"not calculating a constant for xtals " << xIdx-9 << " and " << xIdx << std::endl;
                }
            }
            if(xIdx%9 != 0 && !(xIdx == 33 && cIdx != 15 && fIdx == 1) && !(xIdx == 34 && cIdx != 15 && fIdx == 1)){
                TH1D* tempHist = caloTimePlot->ProjectionZ(Form("_pz%i",xIdx+1),xIdx+1,xIdx+1,xIdx-1+1,xIdx-1+1,"");
                 tempHist->Rebin(2);
                //std::cout<<"number of entries : " << tempHist->GetEntries() << std::endl;
                if(tempHist->GetEntries() > 50){
                    double mean = tempHist->GetMean();
                    double sig = tempHist->GetRMS();
                    tempHist->Fit("gaus","Q","",mean-1.5*sig,mean+1.5*sig);
                    if(tempHist->GetFunction("gaus")){
                        mean = tempHist->GetFunction("gaus")->GetParameter(1);
                        sig = tempHist->GetFunction("gaus")->GetParameter(2);
                        tempHist->Fit("gaus","Q","",mean-2.0*sig,mean+2.0*sig);
                        mean = tempHist->GetFunction("gaus")->GetParameter(1);
                        sig = tempHist->GetFunction("gaus")->GetParError(1);
                    }else{
                        tempHist->Fit("gaus","","",mean-1.5*sig,mean+1.5*sig);
                    }
                    
                    /*beforeOffsets->Fill(fittedMean);
                    afterOffsets->Fill(fittedMean+lastOffsets.at(xIdx)-lastOffsets.at(xIdx-1));*/

                    rhs_(eqnCounter) = mean/sig;
                    
                    for(int colIdx = 0; colIdx < nXtals; colIdx++){
                        if(colIdx == xIdx){
                            m_(eqnCounter,colIdx) = 1.0/sig;
                        }else if(colIdx == xIdx - 1){
                            m_(eqnCounter,colIdx) = -1.0/sig;
                        }else{
                            m_(eqnCounter,colIdx) = 0.0;
                        }
                    }
                    eqnCounter++;
                }else{
                    //std::cout<<"not calculating a constant for xtals " << xIdx << " and " << xIdx-1 << std::endl;
                }
            }

            
        }
        //std::cout<<"number of equations is : "<<eqnCounter<<std::endl;
        
        Eigen::JacobiSVD<Eigen::MatrixXf> svd(m_, Eigen::ComputeThinU | Eigen::ComputeThinV);
        
        Eigen::VectorXf x_ = svd.solve(rhs_);
        //std::cout<<"[";
        //std::cout<<"{";
        for(int tempIdx = 0; tempIdx < nXtals && tempIdx < x_.size(); tempIdx++){
            //std::cout << Form("%0.3f",0.0-x_(tempIdx)) << ", " ;
            constants.at(fIdx).at((cIdx-1)*54 + tempIdx) = 0.0-x_(tempIdx);
            //std::cout<<"\t\txtal"<<tempIdx<<" : "<<Form("%0.3f",0.0-x_(tempIdx)) << std::endl;
            // //std::cout<<Form("%0.3f",0.0-x_(tempIdx))<<",";
        }
        // //std::cout<<"]"<<std::endl;
        //std::cout<<"\t}"<<std::endl;
        //std::cout<<"}"<<std::endl;
        for(int tempIdx = 0; tempIdx < nXtals && tempIdx < x_.size(); tempIdx++){
            //constantsPlots.at(loopdx)->SetPoint(tempIdx, tempIdx, 0.0-x_(tempIdx));
            if(tempIdx == 7){
                //std::cout << "\noffset 7 - offset 0 = "<<x_(tempIdx)-x_(0)<<" ct while fixing xtal "<<fixedXtal<<std::endl;
            }
        }

        m_.resize(1,1);
        m_(0,0) = 0;
        x_.resize(1);
        x_(0) = 0;
        rhs_.resize(1);
        rhs_(0) = 0;
        caloTimePlot = NULL;

        
    }
        /*c1->Clear();
        TLegend *leg1 = new TLegend(0.67,0.12,0.87, 0.25);
        constantsPlots.at(0)->SetTitle(Form("Calculated offsets: calo %i; xtal number; offset [ct]",cIdx));
        constantsPlots.at(0)->SetMarkerStyle(7);
        constantsPlots.at(0)->GetYaxis()->SetRangeUser(-1.0,0.75);
        leg1->AddEntry(constantsPlots.at(0),Form("xtal %i fixed", xtalsToFix.at(0)),"p");
        constantsPlots.at(0)->Draw("apz");
        for(int k = 1; k < constantsPlots.size(); k++){
            constantsPlots.at(k)->SetMarkerStyle(7);
            if( k >= 4){
                constantsPlots.at(k)->SetMarkerColor(k+2);
            }else{
                constantsPlots.at(k)->SetMarkerColor(k+1);
            }
            leg1->AddEntry(constantsPlots.at(k),Form("xtal %i fixed", xtalsToFix.at(k)),"p");
            constantsPlots.at(k)->Draw("pz same");
            c1->Update();
        }
        
        leg1->Draw("same");
        c1->Draw();
        c1->SaveAs(Form("changingFixedXtal_calo%i.pdf",cIdx));*/
    }
    }

    TGraph *constantsCompLine = new TGraph();
    TH1D *constantsCompHist = new TH1D("constantsCompHist","Difference of channel time constants",100,-0.05,0.05);
    if(constants.size() < 2 || constants.at(0).size() != constants.at(1).size()){
        std::cout<<"Sizes are wrong for comparison!"<<std::endl;
        return;
    }
    for(unsigned int k = 0 ; k < constants.at(0).size(); k++){
        //if((int)k/54 != 7){
            constantsCompLine->SetPoint(k,constants.at(0).at(k),constants.at(1).at(k));
            constantsCompHist->Fill(constants.at(0).at(k)-constants.at(1).at(k));
        //}
        if(abs(constants.at(0).at(k)-constants.at(1).at(k)) > 0.03){
            std::cout << "look at calo : " << std::to_string((int)k/54 + 1) << " , xtal : " << std::to_string(k%54) <<std::endl;
            std::cout << "correction 1 : " << std::to_string(constants.at(0).at(k)) << " ct , correction 2 : " << std::to_string(constants.at(1).at(k)) << " ct" << std::endl;
        }
    }
    
    TCanvas *c1 = new TCanvas("c1","c1",700,500);
    constantsCompLine->Draw("apz");
    constantsCompLine->SetTitle("Channel time corrections: without xtal 33 vs. with xtal 33; with xtal 33 constants [ct]; without xtal 33 constants [ct]");
    c1->Draw();
    c1->SaveAs("comparisonScatterWithWithout33.pdf");
    
    TCanvas *c2 = new TCanvas("c2","c2",700,500);
    constantsCompHist->SetTitle("Difference with xtal 33 and without xtal 33; with 33 - without 33 [ct];");
    constantsCompHist->Draw();
    c2->Draw();
    c2->SaveAs("comparisonHistWithWithout33.pdf");
    
    /*beforeOffsets->GetYaxis()->SetRangeUser(0,40);
    beforeOffsets->SetFillColorAlpha(kBlue,0.9);
    beforeOffsets->Draw();
    afterOffsets->SetLineColor(kRed+2);
    afterOffsets->SetFillColorAlpha(kRed+2,0.5);
    afterOffsets->Draw("same");
    leg1->AddEntry(constantsPlots.at(0),"no offsets applied","l");
    leg1->AddEntry(afterOffsets,"after applying offets","l");*/
    

    
    // //std::cout<<"out of the loop!"<<std::endl;
    // std::cout<<"}"<<std::endl;
    // std::cout<<"END_PROLOG";
}
