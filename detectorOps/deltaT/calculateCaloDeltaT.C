#include <Eigen/Dense>
#include <Eigen/SVD>

void calculateCaloDeltaT(std::string fileName = "data/lostMuonsCombined.root"){

    TFile* f1 = new TFile(fileName.c_str());
    
    TH2D* deltaTCalos = (TH2D*)f1->Get("lostMuonET/deltaTCalos");
    
    Eigen::MatrixXf m_;
    Eigen::VectorXf rhs_;
    
    m_.resize(25,25);
    rhs_.resize(25);
    int eqnCounter = 0;
    
    std::vector<TH1D*> plots;
    
    TF1 *fit1 = new TF1("para","[0] + [2]*(x-[1])*(x-[1]) + [3]*(x-[1])",1,10);
    fit1->SetParameters(25000,5.0,-2.0,1.0);
    
    std::cout<<"[";
    for(int cIdx = 1; cIdx <= 24; cIdx++){
        
        TH1D* tempProj = deltaTCalos->ProjectionY(Form("_py%i",cIdx),cIdx,cIdx,"");
        double tempMean = tempProj->GetMean();
        double tempSig = tempProj->GetRMS();
        
        int binmax = tempProj->GetMaximumBin();
        double peak = tempProj->GetXaxis()->GetBinCenter(binmax);
        tempProj->Fit("gaus","Q","",peak -0.2*tempSig, peak + 0.2*tempSig);
        peak = tempProj->GetFunction("gaus")->GetParameter(1);
        double sigma = tempProj->GetFunction("gaus")->GetParameter(2);
        tempProj->Fit("gaus","Q","",peak-1.0*sigma,peak+1.0*sigma);
        plots.push_back(tempProj);
        double mean = tempProj->GetFunction("gaus")->GetParameter(1);
        double error = tempProj->GetFunction("gaus")->GetParError(1);
        std::cout<<mean<<",";
        
        for(int colIdx = 1; colIdx < 25; colIdx++){
            if(colIdx == cIdx){
                m_(eqnCounter,colIdx-1) = 1.0;
            }else if(cIdx > 1 && colIdx == cIdx - 1){
                m_(eqnCounter,colIdx-1) = -1.0;
            }else if(cIdx == 1 && colIdx == 24){
                m_(eqnCounter,colIdx-1) = -1.0;
            }else{
                m_(eqnCounter, colIdx-1) = 0.0;
            }
        }
        m_(eqnCounter,24) = 1.0;
        rhs_(eqnCounter) = mean;
        eqnCounter++;
        
        if(cIdx == 22){
            
            for(int colIdx = 1; colIdx < 26; colIdx++){
                if(colIdx == cIdx){
                    m_(eqnCounter,colIdx-1) = 1;
                }else{
                    m_(eqnCounter,colIdx-1) = 0.0;
                }
            }
            
            rhs_(eqnCounter) = 0.0;
            
            eqnCounter++;
        }
        
        
    }
    //std::cout<<"]"<<std::endl;
    
    std::cout << "Here is A:\n"<<m_<<std::endl;
    std::cout<< "here is b:\n"<<rhs_<<std::endl;
    
    //Eigen::JacobiSVD<Eigen::MatrixXf> svd(m_, Eigen::ComputeThinU | Eigen::ComputeThinV);
    
    Eigen::VectorXf x_ = m_.completeOrthogonalDecomposition().solve(rhs_);//svd.solve(rhs_);
    std::cout<<"results : {";
    for(int tempIdx = 0; tempIdx < x_.size(); tempIdx++){
        std::cout<<Form("%0.3f",0.0-x_(tempIdx)) << ",";
    }
    std::cout<<"}"<<std::endl;
    
    TCanvas* c1 = new TCanvas("c1","c1",700,500);
    gPad->SetLogy();
    c1->Divide(6,4);
    c1->Update();
    for(int i = 0; i < 24; i++){
        c1->cd(i+1);
        gPad->SetLogy();
        plots.at(i)->Draw();
        c1->Update();
    }
    c1->SaveAs("deltaTFits.pdf");
    

}
