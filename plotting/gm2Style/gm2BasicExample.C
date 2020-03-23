
#include "TH1F.h"
#include "TPad.h"
#include "TRandom.h"
#include "TCanvas.h"

#include "gm2Labels.h"
#include "gm2Style.h"

#ifdef __CLING__
// these are not headers - do not treat them as such - needed for ROOT6
#include "gm2Labels.C"
#endif

void gm2BasicExample()
{
  SetGm2Style();

  TCanvas* c1 = new TCanvas("c1", "gm2 basic example", 0., 0., 800, 600);

  // generate some random data
  TH1F* h_example  = new TH1F("h_example","Random gaussian plot",100,-4,4);
  gRandom->SetSeed();
  for (Int_t i = 0; i < 25000; i++) {
    h_example->Fill(gRandom->Gaus());
  }
  h_example->GetXaxis()->SetTitle("Variable [unit]");
  h_example->GetYaxis()->SetTitle("Variable [unit]");
  h_example->SetMaximum(1000.);

  // and plot it
  h_example->Draw();

  c1->Print("gm2BasicExample.eps");
  c1->Print("gm2BasicExample.png");
  
  return;
}

#ifndef __CINT__
int main() { 
  gm2BasicExample();
  return 0;
}
#endif
