//
// g-2 Style, based on a style file from ATLAS
//

#include <iostream>

#include "gm2Style.h"

#include "TROOT.h"
#include "TCanvas.h"
#include "TColor.h"

void SetGm2Style ()
{
  static TStyle* Gm2Style = 0;
  std::cout << "\nApplying g-2 style settings...\n" << std::endl ;
  if ( Gm2Style==0 ) Gm2Style = gm2Style();
  gROOT->SetStyle("gm2");
  gROOT->ForceStyle();
  colorTracker = initializeColors();
}

TCanvas* g2Canvas( std::string name, int dims)
{
	const char *constName = name.c_str();
	TCanvas *c = new TCanvas(constName, constName, dims, dims);
	return c;
}


TCanvas* g2CanvasRect( std::string name, int dimx, int dimy)
{
	const char *constName = name.c_str();
	TCanvas *c = new TCanvas(constName, constName, dimx, dimy);
	return c;
}

TCanvas* g2Canvas2D( std::string name, int dims)
{
	const char *constName = name.c_str();
	double aspectDiff = 1.2;
	TCanvas *c = new TCanvas(constName, constName, dims*aspectDiff, dims);
	c->SetRightMargin(aspectDiff - 1.0 );
	return c;
}

TCanvas* g2Canvas2DRect( std::string name, int dimx, int dimy)
{
	const char *constName = name.c_str();
	TCanvas *c = new TCanvas(constName, constName, dimx, dimy);
	c->SetRightMargin(0.16);
	return c;
}

TCanvas* g2Canvas3D( std::string name, int dims)
{
	const char *constName = name.c_str();
	double aspectDiff = 1.0;
	TCanvas *c = new TCanvas(constName, constName, dims*aspectDiff, dims);
	//c->SetRightMargin(aspectDiff - 1.0);
	return c;
}

//define the colors to be used for lines. These have been chosed to be both print and colorblind friendly
int initializeColors()
{
	colorTracker = 0;
	return 0;
}


//this function cycles through recommended colors. This can be used in a loop to automatically
//	assign good, readable colors to functions / histograms.
int g2ColorPicker()
{
	int thisColor = 1; //default to black
	std::vector<int> goodColors = {9904, 9900, 9901, 9902, 9903, 9905, 9906};
	thisColor = goodColors[ colorTracker % goodColors.size() ];
	colorTracker++;

	return thisColor;
}

//Automatically save each plot in png/eps/root format for easy portability
void g2Print(std::string name, TCanvas *c)
{
	std::cout << "Printing canvas with name " << name << std::endl;

	c->Print( (name+".png").c_str() );
	c->Print( (name+".eps").c_str() );
	c->Print( (name+".root").c_str() );

	std::cout << "Done!" << std::endl;
}

TStyle* gm2Style() 
{
  TStyle *gm2Style = new TStyle("gm2","gm2 style");

  // use plain black on white colors
  Int_t icol=0; // WHITE
  gm2Style->SetFrameBorderMode(icol);
  gm2Style->SetFrameFillColor(icol);
  gm2Style->SetCanvasBorderMode(icol);
  gm2Style->SetCanvasColor(icol);
  gm2Style->SetPadBorderMode(icol);
  gm2Style->SetPadColor(icol);
  gm2Style->SetStatColor(icol);
  gm2Style->SetLegendBorderSize(0);

  // set the paper & margin sizes
  gm2Style->SetPaperSize(20,26);

  // set margin sizes
  gm2Style->SetPadTopMargin(0.05);
  gm2Style->SetPadRightMargin(0.05);
  gm2Style->SetPadBottomMargin(0.16);
  gm2Style->SetPadLeftMargin(0.16);

  // set title offsets (for axis label)
  gm2Style->SetTitleXOffset(1.4);
  gm2Style->SetTitleYOffset(1.4);
  gm2Style->SetTitleOffset(1.4,"z");

  // use large fonts
  //Int_t font=72; // Helvetica italics
  Int_t font=42; // Helvetica
  Double_t tsize=0.05;
  gm2Style->SetTextFont(font);

  gm2Style->SetTextSize(tsize);
  gm2Style->SetLabelFont(font,"x");
  gm2Style->SetTitleFont(font,"x");
  gm2Style->SetLabelFont(font,"y");
  gm2Style->SetTitleFont(font,"y");
  gm2Style->SetLabelFont(font,"z");
  gm2Style->SetTitleFont(font,"z");
  
  gm2Style->SetLabelSize(tsize,"x");
  gm2Style->SetTitleSize(tsize,"x");
  gm2Style->SetLabelSize(tsize,"y");
  gm2Style->SetTitleSize(tsize,"y");
  gm2Style->SetLabelSize(tsize,"z");
  gm2Style->SetTitleSize(tsize,"z");

  // use bold lines and markers
  gm2Style->SetMarkerStyle(20);
  gm2Style->SetMarkerSize(1.2);
  gm2Style->SetHistLineWidth(2.);
  gm2Style->SetLineStyleString(2,"[12 12]"); // postscript dashes

  // get rid of X error bars (as recommended in ATLAS figure guidelines)
  gm2Style->SetErrorX(0.0001);
  // get rid of error bar caps
  gm2Style->SetEndErrorSize(0.);

  // do not display any of the standard histogram decorations
  gm2Style->SetOptTitle(0);
  gm2Style->SetOptStat(0);
  gm2Style->SetOptFit(0);

  // put tick marks on top and RHS of plots
  gm2Style->SetPadTickX(1);
  gm2Style->SetPadTickY(1);

  //in the case of 2D histograms, default to the kViridis color palette
  gm2Style->SetPalette(112); //kViridis
  gm2Style->SetNumberContours(80);

  return gm2Style;

}

