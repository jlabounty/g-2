//
//   @file    gm2Labels.h
//   
//   @author R. Chislett
// 

#ifndef __GM2LABELS_H
#define __GM2LABELS_H

#include "Rtypes.h"

void gm2Label(Double_t x, Double_t y,const char* text=NULL,Color_t color=1); 
void gm2Logo(Double_t x, Double_t y, Double_t width=0.2);
void gm2Text(Double_t x, Double_t y, const char* text, Double_t textSize=0.05, Color_t color=1); 
void gm2Watermark( const char* text );

#endif // __GM2LABELS_H
