#include "gm2Labels.h"

#include "TLatex.h"
#include "TLine.h"
#include "TPave.h"
#include "TPad.h"
#include "TMarker.h"
#include "TImage.h"


void gm2Label(Double_t x,Double_t y,const char* text,Color_t color) 
{
  TLatex l; //l.SetTextAlign(12); l.SetTextSize(tsize); 
  l.SetNDC();
  l.SetTextFont(72);
  l.SetTextColor(color);

  double delx = 0.06*696*gPad->GetWh()/(472*gPad->GetWw());

  l.DrawLatex(x,y,"g-2");
  if (text) {
    TLatex p; 
    p.SetNDC();
    p.SetTextFont(42);
    p.SetTextColor(color);
    p.DrawLatex(x+delx,y,text);
  }
}

void gm2Logo(Double_t x, Double_t y)
{
  TImage *img = TImage::Open("g-2Logo.png");

  TPad *l = new TPad("l", "l", x, y, x+0.2, y+0.2);
  l->Draw();
  l->cd();
  img->Draw();
}
