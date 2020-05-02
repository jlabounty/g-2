int getRunNumber(TString & filename)
{
  int underscorePos = filename.Last('_');
  int dotPos = filename.Last('.'); 
  TString runSubrun = filename(underscorePos+1, dotPos-underscorePos-1);
  TString runString = runSubrun(0, runSubrun.Last('.'));
  int run = runString.Atoi();
  // TString subrunString = runSubrun(runSubrun.Last('.')+1, runSubrun.Length());
  // int subrun = subrunString.Atoi();
  return run; 
}

int getSubrunNumber(TString & filename)
{
  int underscorePos = filename.Last('_');
  int dotPos = filename.Last('.'); 
  TString runSubrun = filename(underscorePos+1, dotPos-underscorePos-1);
  TString runString = runSubrun(0, runSubrun.Last('.'));
  int run = runString.Atoi();
  TString subrunString = runSubrun(runSubrun.Last('.')+1, runSubrun.Length());
  int subrun = subrunString.Atoi();
  return subrun; 
}


void extractNearline(TDirectory *dir, ostream & ostr)
{

   TString filename(dir->GetName());
   int run = getRunNumber(filename);
   int subrun = getSubrunNumber(filename);

  TH1 *ctagsByCaloWithDQC = (TH1 *) dir->Get("offNearlineWithDQC/nearlineCTag");
  TH1 *ctagsByCaloNoDQC = (TH1 *) dir->Get("offNearlineNoDQC/nearlineCTag");
  if(!ctagsByCaloWithDQC || !ctagsByCaloNoDQC) {
    ostr << "XXX-ERROR-1 " << run << " " << subrun << endl;
    return;
  }

  TH1 *bunchWithDQC =  (TH1 *) dir->Get("offNearlineWithDQC/bunch");
  TH1 *bunchNoDQC =  (TH1 *) dir->Get("offNearlineNoDQC/bunch");
  if(!bunchWithDQC || !bunchNoDQC) {
    ostr << "XXX-ERROR-2 " << run << " " << subrun << endl;
    return;
  }

  TH1 *t0WithDQC = (TH1 *) dir->Get("offNearlineWithDQC/t0");
  TH1 *t0NoDQC = (TH1 *) dir->Get("offNearlineNoDQC/t0");
  if(!t0WithDQC || !t0NoDQC) {
    ostr << "XXX-ERROR-3 " << run << " " << subrun << endl;
    return;
  }

  TH1 *ibms1xMean = (TH1 *) dir->Get("offNearlineWithDQC/ibms1xMean");
  TH1 *ibms1yMean = (TH1 *) dir->Get("offNearlineWithDQC/ibms1yMean");
  TH1 *ibms2xMean = (TH1 *) dir->Get("offNearlineWithDQC/ibms2xMean");
  TH1 *ibms2yMean = (TH1 *) dir->Get("offNearlineWithDQC/ibms2yMean");
  if(!ibms1xMean || !ibms1yMean || !ibms2xMean || !ibms2yMean) {
    ostr << "XXX-ERROR-4 " << run << " " << subrun << endl;
    return;
  }

  TH1 *ibms1xRMS = (TH1 *) dir->Get("offNearlineWithDQC/ibms1xRMS");
  TH1 *ibms1yRMS = (TH1 *) dir->Get("offNearlineWithDQC/ibms1yRMS");
  TH1 *ibms2xRMS = (TH1 *) dir->Get("offNearlineWithDQC/ibms2xRMS");
  TH1 *ibms2yRMS = (TH1 *) dir->Get("offNearlineWithDQC/ibms2yRMS");
  TH1 *ibmsTotalIntegral = (TH1 *) dir->Get("offNearlineWithDQC/ibmsTotalIntegral");
  if(!ibms1xRMS || !ibms1yRMS || !ibms2xRMS || !ibms2yRMS || !ibmsTotalIntegral) {
    ostr << "XXX-ERROR-5 " << run << " " << subrun << endl;
    return;
  }

  ostr << 
    "INSERT INTO gm2dq.ibms(run, subrun, ibms1xMean, ibms1yMean, ibms2xMean, ibms2yMean, " 
    << "ibms1xRMS, ibms1yRMS, ibms2xRMS, ibms2yRMS, " 
    << "ibms1xIntegral, ibms1yIntegral, ibms2xIntegral, ibms2yIntegral) VALUES (" 
    << run << ", " << subrun << ", " 
    << ibms1xMean->GetMean() << ", " << ibms1yMean->GetMean() << ", " 
    << ibms2xMean->GetMean() << ", " << ibms2yMean->GetMean() << ", "
    << ibms1xRMS->GetMean() << ", " << ibms1yRMS->GetMean() << ", " 
    << ibms2xRMS->GetMean() << ", " << ibms2yRMS->GetMean() << ", "
    << ibmsTotalIntegral->GetBinContent(2) << ", " << ibmsTotalIntegral->GetBinContent(3) << ", "
    << ibmsTotalIntegral->GetBinContent(4) << ", " << ibmsTotalIntegral->GetBinContent(5) << ");" << endl;

  int fills = bunchWithDQC->Integral();
  int ctags = ctagsByCaloWithDQC->Integral();
  double t0Val = t0WithDQC->GetBinContent(1);
  ostr << 
    "INSERT INTO gm2dq.ctagsWithDQC(run, subrun, fills, ctags, t0Val) VALUES (" <<
      run << ", " << subrun << ", " << fills << ", " << ctags << "," << t0Val << ");" << endl;

  int fillsNoDQC = bunchNoDQC->Integral();
  int ctagsNoDQC = ctagsByCaloNoDQC->Integral();
  double t0ValNoDQC = t0NoDQC->GetBinContent(1);
  ostr << 
    "INSERT INTO gm2dq.ctagsNoDQC(run, subrun, fills, ctags, t0Val) VALUES (" <<
      run << ", " << subrun << ", " << fillsNoDQC << ", " << ctagsNoDQC << "," << t0ValNoDQC << ");" << endl;

  // Let's save the crystals for a separate analysis...
  // for(int calo = 1; calo <= 24; calo++) 
  // {
//
 //  
    // now visit each crystal
  //  for(int xtal = 0; xtal < 54; xtal++) 
   // {
//    TH1 *xtalEnergy = (TH1 *) dir->Get(Form("offNearlineWithDQC/calo%d/xtal%dEnergy", calo, xtal));
//    int numHits = xtalEnergy->GetEntries();
//    double energyMean = xtalEnergy->GetMean();
//    double energyRMS = xtalEnergy->GetRMS();
//    TH1 *xtalLaserEnergy = (TH1 *) dir->Get(Form("offNearlineWithDQC/calo%d/xtal%dLaserEnergy", calo, xtal));
//    int numLasers = xtalLaserEnergy->GetEntries();
//    double laserMean = xtalLaserEnergy->GetMean();
//    double laserRMS = xtalLaserEnergy->GetRMS();
//    ostr << 
//      "INSERT INTO gm2dq.xtals(run, subrun, calo, xtal, numHits, energyMean, energyRMS, numLasers, laserMean, laserRMS) VALUES (" <<
//        run << ", " << subrun << ", " << calo << ", " << xtal << ", " << numHits << ", " << energyMean << ", " << energyRMS << ", "
//        << numLasers << ", " << laserMean << ", " << laserRMS << ");" << endl;
//  }
//}

  // get the GPS timing information
  TTree *t = (TTree *) dir->Get("offNearlineNoDQC/timeTree");
  if(!t) {
    ostr << "XXX-ERROR-6 " << run << " " << subrun << endl;
    return;
  }

  double unixTimeRecv;
  double unixTimeFE;

  t->SetBranchAddress("unixTimeRecv", &unixTimeRecv);
  t->SetBranchAddress("unixTimeFE", &unixTimeFE);

  t->GetEntry(0);
  double startTime = unixTimeRecv;

  t->GetEntry(t->GetEntries()-1);
  double endTime = unixTimeRecv;

//  ostr << "UPDATE gm2dq.subrun_time SET start_gps=to_timestamp(" <<
//    std::setprecision(15)  << startTime << "), end_gps=to_timestamp(" << endTime << ")" <<
//    " WHERE run=" << run << " AND subrun=" << subrun << ";" <<  endl;

 
  // the rest of the function deals with muon losses 
  t = (TTree *) dir->Get("testCoincidenceFinder/t");
  if(!t) {
    ostr << "XXX-ERROR-7 " << run << " " << subrun << endl;
    return;
  }


  double singles = t->Draw("clusterTime[0]>>s_after_30(100,30000,630000)", 
     "coincidenceLevel == 1 && clusterTime[0] > 30000", "NODRAW");

  t->Draw("clusterTime[1]-clusterTime[0]>>d_after_30(100, 0, 20)", 
     "coincidenceLevel == 2 && clusterTime[0] > 30000", "NODRAW");
  TH1 *h_d_after_30 = (TH1 *) dir->Get("d_after_30");
  double doubles = 0;
  double background = 0;
  if(h_d_after_30) {
    doubles = h_d_after_30->Integral(1,50); 
    background = h_d_after_30->Integral(51,100); 
  }

  // first, normalized to low-energy singles
  double lossRatio = (doubles - background)/singles;

  double lossRatioErrorNum = 
     (sqrt(doubles + background))/(doubles - background);
  double lossRatioErrorDenom = sqrt(singles) / singles;
  double lossRatioError = lossRatio * 
      sqrt(lossRatioErrorNum*lossRatioErrorNum + 
           lossRatioErrorDenom*lossRatioErrorDenom);

  if(doubles-background == 0 || singles == 0) {
    lossRatio = 0;
    lossRatioError = 0;
  }

  // then, normalized to CTAGS
  double lossRatioCtags = (doubles - background)/ctags;

  double lossRatioCtagsErrorNum = 
     (sqrt(doubles + background))/(doubles - background);
  double lossRatioCtagsErrorDenom = sqrt(ctags) / ctags;
  double lossRatioCtagsError = lossRatioCtags * 
      sqrt(lossRatioCtagsErrorNum*lossRatioCtagsErrorNum + 
           lossRatioCtagsErrorDenom*lossRatioCtagsErrorDenom);

  if(doubles-background == 0 || ctags == 0) {
    lossRatioCtags = 0;
    lossRatioCtagsError = 0;
  }

  ostr << 
    "INSERT INTO gm2dq.losses(run, subrun, singles, doubles, background, ctags, lossRatio, lossRatioError, lossRatioCtags, lossRatioCtagsError) VALUES (" <<
    run << ", " << subrun << ", " << singles << ", " << doubles << ", " <<
    background << ", " << ctags << ", " << lossRatio << ", " << lossRatioError << ", " <<
    lossRatioCtags << ", " << lossRatioCtagsError <<  ");" << endl;

}

void runall(char *dirName, char *sqlFilename, int modulo = -1, int offset = -1)
{
  std::cout << "Running... " << std::endl;
  ofstream sqlFile(sqlFilename, ofstream::out);
  void *dirp = gSystem->OpenDirectory(dirName);
  const char *entry;
  TString str;
  TString dirStr(dirName);
  while((entry = (char*)gSystem->GetDirEntry(dirp))) {
    str = entry;
    if(str.EndsWith(".root")) {

      if(modulo > 0) {
        int subrun = getSubrunNumber(str);
        if(subrun % modulo != offset) continue;
      }

      cout << "Processing "  << str << endl;

      TFile *file = new TFile(dirStr + "/" + str);
      extractNearline(file, sqlFile);
      delete file;
      sqlFile.flush();
    } 
  }
  sqlFile.close();
  //exit(0);
}

void runonce(char* fileName, char* sqlFilename)
{
	ofstream sqlFile(sqlFilename, ofstream::out); 
	//TFile *file = new TFile(fileName); //will this work with xroot?
	TFile *file = TFile::Open(fileName); //will this work with xroot?
	extractNearline(file, sqlFile);  
	delete file;
	sqlFile.flush();  
}

void runDirTree(char *dirName, char *sqlFilename, int firstRun, int lastRun)
{
  ofstream sqlFile(sqlFilename, ofstream::out);

  for(int run = firstRun; run <= lastRun; run++) {
 
    int runThousands = (run/1000) * 1000;

    char dirNameExt[256];
    sprintf(dirNameExt, "%s/runs_%d/%d", dirName, runThousands, run);
 
    void *dirp = gSystem->OpenDirectory(dirNameExt);
    if(!dirp) {
      cout << "Skipping " << dirNameExt << endl;
      continue;
    }

    const char *entry;
    TString str;
    TString dirStr(dirNameExt);

    while((entry = (char*)gSystem->GetDirEntry(dirp))) {
      str = entry;
      if(str.EndsWith(".root")) {
  
     //   if(modulo > 0) {
     //     int subrun = getSubrunNumber(str);
     //     if(subrun % modulo != offset) continue;
     //   }

        cout << "Processing "  << str << endl;

        TFile *file = new TFile(dirStr + "/" + str);
        extractNearline(file, sqlFile);
        delete file;
        sqlFile.flush();
      }
    } 
  }
  sqlFile.close();
}

void runListingFile(char *listfileName, char *sqlFilename, int modulo = -1, int offset = -1)
{
  ofstream sqlFile(sqlFilename, ofstream::out);
  FILE *listfile = fopen(listfileName, "r");

  char filename[256];

  while(!feof(listfile)) {

    fscanf(listfile, "%s ", filename);
    TString str(filename);

    if(modulo > 0) {
     int subrun = getSubrunNumber(str);
     if(subrun % modulo != offset) continue;
    }

    cout << "Processing "  << str << endl;

    TFile *file = new TFile(filename);
    extractNearline(file, sqlFile);
    delete file;
    sqlFile.flush();

  }
  sqlFile.close();
}


void extractNearline_init(char* directory, char* outfile, int v2, int v3)
{
	std::cout<< "Preparing for dqc..." << std::endl;
	//runall(directory,outfile,v2,v3);
	runonce(directory,outfile);
	std::cout << "All done! " <<std::endl;
	exit(0);
}
