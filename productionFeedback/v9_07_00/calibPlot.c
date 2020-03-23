void calibPlot(std::string filename){

  TFile *file = new TFile(filename.c_str());

  TTree *event = (TTree*)file->Get("Events");
  event->Print();

  TCanvas *c1 = new TCanvas("c1","c1",1200,800);

  TH1D *hist = new TH1D("hist","hist",100,0,2);
  TCut cut("gm2calo::CaloCalibrationConstants_longTermGainCorrectionDAQ_corrector_fullwithDQC.obj.caloNum==24");
  event->Draw("gm2calo::CaloCalibrationConstants_longTermGainCorrectionDAQ_corrector_fullwithDQC.obj.constants>>hist",cut);

  hist->Draw();

  c1->Print("test.pdf");
}
