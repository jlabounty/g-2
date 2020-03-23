TRandom3* initializeRNG( int seed )
{
  globalSeed += 1;
  TRandom3* rng = new TRandom3(seed);
  return rng;
}

double testfunc( double decayTime )
{

    TRandom3* rng = new TRandom3(globalSeed);
    globalSeed += 1;

    double w0 = 2.6094;
    double A = 2.80;
    double tauA = 56.6;
    double B = 6.18;
    double tauB = 6.32;
    
      double time = decayTime;

      //time = 8.0 * 1000.0;
      double wCBO =  (w0 - (A/(tauA)) * exp(-time/(1000.0*tauA)) - (B/(tauB)) * exp(-time/(tauB*1000.0)) ); //MHz
      double wa =  TMath::TwoPi() * 0.2291; //MHZ
      double wc =  TMath::TwoPi() / 0.14919; //MHz

      double factor = 1.0;
      double wY = factor * (wCBO) * sqrt( (2 * wc / (factor * wCBO)) -1.0 ) ;
      double wVW = wc - (2.0 * wY);

      double TCBO = TMath::TwoPi() / wCBO;
      double Ta = TMath::TwoPi() / wa;
      double TVW = TMath::TwoPi() / wVW;
      double TY = TMath::TwoPi() / wY;
      double Tc = TMath::TwoPi() / wc;

      // Omega-a and omega-CBO beat frequencies
      double T_diff= TMath::TwoPi()/(wCBO-wa);
      //      double T_sum = TMath::TwoPi()/(wCBO+wa);

      // cout << "fC: "   << wc / TMath::TwoPi()   << " MHz, period:  " << Tc   << " us " << "\n";
      // cout << "fa: "   << wa / TMath::TwoPi()   << " MHz, period:  " << Ta   << " us " << "\n";
      // cout << "fCBO: " << wCBO / TMath::TwoPi() << " MHz, period:  " << TCBO << " us " << "\n";
      // cout << "fY: "   << wY / TMath::TwoPi()   << " MHz, period:  " << TY   << " us " << "\n";
      // cout << "fVW: "  << wVW / TMath::TwoPi()  << " MHz, period:  " << TVW  << " us " << "\n";
      // cout << "f_diff: " << (wCBO-wa) / TMath::TwoPi()   << " MHz, period:  " << T_diff   << " us " << "\n";
      // cout << "f_sum: " << (wCBO+wa) / TMath::TwoPi()   << " MHz, period:  " << T_sum   << " us " << "\n";
      // return;

      time += (rng->Uniform()-0.5)*(Ta*1000.0);// w_a 4365
      time += (rng->Uniform()-0.5)*(TCBO*1000.0);// w_CBO 2703
      time += (rng->Uniform()-0.5)*(TVW*1000.0);// w_VW 433
      time += (rng->Uniform()-0.5)*(TY*1000.0);// w_Y
      time += (rng->Uniform()-0.5)*(Tc*1000.0);// w_c
      time += (rng->Uniform()-0.5)*(T_diff*1000);// Beat between w_a and w_CBO (diff)
      //      time += (rng->Uniform()-0.5)*(T_sum*1000);// Beat between w_a and w_CBO (sum) - this seems to add an oscillation in!

    rng->Delete(); //not sure why this is, but not having this line causes memory leak.
    return time;
}