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

void gm2Watermark( const char* text )
{
	TLatex w; 
	w.SetNDC();
	w.SetTextFont(42);
	w.SetTextColorAlpha(17, 0.2);
	w.SetTextSize(0.2);
	w.SetTextAngle(30);
	w.SetLineWidth(2);
	w.DrawLatex(0.2,0.2,text);

}

void gm2Logo(Double_t x, Double_t y, Double_t width)
{
  TVirtualPad* startPad = gPad;
  
  double heightWidthRatio = float(startPad->GetWh()) / startPad->GetWw();
  double height = width * 406./572. * heightWidthRatio; // Image is 572 x 406 pixels

  TImage *img = TImage::Open("./g-2Logo.png");
  
  TPad *l = new TPad("l", "l", x, y, x+width, y+height); 
  l->SetLeftMargin(0.0);
  l->SetRightMargin(0.0);
  l->SetTopMargin(0.0);
  l->SetBottomMargin(0.0);
  l->SetBorderSize(1);
  l->Draw();
  l->cd();
  img->Draw();

  startPad->cd();
  
}


void gm2Text(Double_t x, Double_t y, const char* text, Double_t textSize, Color_t color) 
{
  TLatex l;
  l.SetTextSize(textSize); 
  l.SetNDC();
  l.SetTextFont(42);
  l.SetTextColor(color);
  l.DrawLatex(x,y,text);
}
