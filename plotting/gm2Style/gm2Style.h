//
//   @file    gm2Style.h         
//   
//            g-2 Style, based on a style file from ATLAS
//
//
//   @author R. Chislett
// 
//   Copyright (C) 2010 Atlas Collaboration
//
//   $Id: gm2Style.h, v0.0   Thu 25 Mar 2010 10:34:20 CET $

#ifndef  __GM2STYLE_H
#define __GM2STYLE_H

#include "TStyle.h"
#include "TCanvas.h"

void SetGm2Style();

TCanvas* g2Canvas( std::string name, int dims );
TCanvas* g2CanvasRect( std::string name, int dimx, int dimy );
TCanvas* g2Canvas2D( std::string name, int dims );
TCanvas* g2Canvas2DRect( std::string name, int dimx, int dimy );
TCanvas* g2Canvas3D( std::string name, int dims );

int initializeColors();
int g2ColorPicker();
int colorTracker;

void g2Print( std::string name, TCanvas* c );

TStyle* gm2Style(); 

//colors selected to be colorblind and printer friendly defined here
TColor *g2Color1 = new TColor(9900, 0/255., 119/255., 187/255.);       //blue
TColor *g2Color2 = new TColor(9901, 51/255., 187/255., 238/255.);      //cyan
TColor *g2Color3 = new TColor(9902, 0/255., 153/255., 136/255.);       //teal
TColor *g2Color4 = new TColor(9903, 238/255., 119/255., 51/255.);      //orange
TColor *g2Color5 = new TColor(9904, 204/255., 51/255., 17/255.);       //red
TColor *g2Color6 = new TColor(9905, 238/255., 51/255., 119/255.);      //magenta
TColor *g2Color7 = new TColor(9906, 187/255., 187/255., 187/255.);     //grey

#endif // __GM2STYLE_H
