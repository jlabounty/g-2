////////////////////////////////////////////////////////////////////////
// Class:       LongDoublePulsePlotter
// Plugin Type: analyzer (art v2_09_02)
// File:        LongDoublePulsePlotter_module.cc
//
// Generated at Tue Feb 20 10:13:42 2018 by Matthias Smith using cetskelgen
// from cetlib version v3_01_03.
////////////////////////////////////////////////////////////////////////

#include "art/Framework/Core/EDAnalyzer.h"
#include "art/Framework/Core/ModuleMacros.h"
#include "art/Framework/Principal/Event.h"
#include "art/Framework/Principal/Handle.h"
#include "art/Framework/Principal/Run.h"
#include "art/Framework/Principal/SubRun.h"
#include "art/Framework/Services/Optional/TFileService.h"
#include "art/Framework/Services/Registry/ServiceHandle.h"
#include "canvas/Utilities/InputTag.h"
#include "fhiclcpp/ParameterSet.h"
#include "messagefacility/MessageLogger/MessageLogger.h"

#include "TTree.h"
#include "TString.h"
#include "TH1.h"
#include "TH2.h"
#include "TH3.h"

#include "gm2calo/util/CaloForEach.hh"
#include "gm2dataproducts/calo/CrystalHitArtRecord.hh"
#include "gm2dataproducts/daq/MidasEventHeaderArtRecord.hh"


namespace gm2calo {

class LongDoublePulsePlotter;

class LongDoublePulsePlotter : public art::EDAnalyzer {
public:
  explicit LongDoublePulsePlotter(fhicl::ParameterSet const & p);
  // The compiler-generated destructor is fine for non-base
  // classes without bare pointers or other resource use.

  // Plugins should not be copied or assigned.
  LongDoublePulsePlotter(LongDoublePulsePlotter const &) = delete;
  LongDoublePulsePlotter(LongDoublePulsePlotter &&) = delete;
  LongDoublePulsePlotter & operator = (LongDoublePulsePlotter const &) = delete;
  LongDoublePulsePlotter & operator = (LongDoublePulsePlotter &&) = delete;

  // Art functions.
  void analyze(art::Event const & e) override;
  void beginRun(art::Run const &r) override;
  void endRun(art::Run const &r) override;
  void endJob() override;

  void initGainPerRun();
  void fillGainPerRun(art::Event const &e);
  void closeGainPerRun();

  void initGainSummary();
  void fillGainSummary(art::Event const &e);
  void closeGainSummary();

private:

  // Data variables.
  int runNum_;
  std::vector<int> runList_;

  // Output histograms.
  std::map<int, std::map<int, TH1F *>> mapHistMapNormPerXtal_;
  std::map<int, std::map<int, TH1F *>> mapHistMapTimePerXtal_;
  std::map<int, std::map<int, TH1F *>> mapHistMapBurstPerXtal_;
  std::map<int, std::map<int, TH1F *>> mapHistMapProbePerXtal_;

  TH2F *histGainCurveVsTime_;
  TH2F *histGainSagVsLoad_;
  std::map<int, TH2F *> histMapGainVsTime_;

  // fhicl parameters
  std::string fitterModuleLabel_;
  std::string fitterInstanceLabel_;

  double burstRangeMin_;
  double burstRangeMax_;
  double probeRangeMin_;
  double probeRangeMax_;
  bool writeGainPerRun_;
  bool writeGainSummary_;
};


LongDoublePulsePlotter::LongDoublePulsePlotter(fhicl::ParameterSet const & p)
  :
  EDAnalyzer(p),
  fitterModuleLabel_(
    p.get<std::string>("fitterModuleLabel", "islandFitterDAQ")), 
  fitterInstanceLabel_(
    p.get<std::string>("fitterInstanceLabel", "fitter")),
  burstRangeMin_(p.get<double>("burstRangeMin", 10.0)),
  burstRangeMax_(p.get<double>("burstRangeMax", 35.0)),
  probeRangeMin_(p.get<double>("probeRangeMin", 35.0)),
  probeRangeMax_(p.get<double>("probeRangeMax", 700.0)),
  writeGainPerRun_(p.get<bool>("writeGainPerRun", true)),
  writeGainSummary_(p.get<bool>("writeGainSummary", true)) {}


void LongDoublePulsePlotter::beginRun(art::Run const &r)
{
  static std::map<int, bool> _mapRunsInitialized;

  // Set the current run number.
  runNum_ = r.run();

  if (_mapRunsInitialized[runNum_]) {

    return;

  } else {

    initGainSummary(); // want aggregate folder at top
    initGainPerRun();

    runList_.push_back(runNum_);
    _mapRunsInitialized[runNum_] = true;
  }
}


void LongDoublePulsePlotter::analyze(art::Event const &e)
{
  fillGainPerRun(e);
  fillGainSummary(e);
}


void LongDoublePulsePlotter::endRun(art::Run const &r)
{
  closeGainPerRun();
  closeGainSummary();
}


void LongDoublePulsePlotter::endJob()
{
  // Summarize the data in a tree.
  art::ServiceHandle<art::TFileService> tfs;
  TTree *tree = tfs->make<TTree>("tree", "Long Double Pulse Gain Data");

  int runNum; tree->Branch("runNum", &runNum);
  int caloNum; tree->Branch("caloNum", &caloNum);
  int xtalNum; tree->Branch("xtalNum", &xtalNum);
  double timeAvg; tree->Branch("timeAvg", &timeAvg);
  double timeRms; tree->Branch("timeRms", &timeRms);
  double normAvg; tree->Branch("normAvg", &normAvg);
  double normRms; tree->Branch("normRms", &normRms);
  double burstAvg; tree->Branch("burstAvg", &burstAvg);
  double burstRms; tree->Branch("burstRms", &burstRms);
  double probeAvg; tree->Branch("probeAvg", &probeAvg);
  double probeRms; tree->Branch("probeRms", &probeRms);

  for (int &rn : runList_) {
    for (int cn = 1; cn < 25; ++cn) {
      for (int xi = 0; xi < 54; ++xi) {

	int idx = 100 * cn + xi;
	auto htime = mapHistMapTimePerXtal_[rn][idx];
	auto hnorm = mapHistMapNormPerXtal_[rn][idx];
	auto hburst = mapHistMapBurstPerXtal_[rn][idx];
	auto hprobe = mapHistMapProbePerXtal_[rn][idx];

	runNum = rn;
	caloNum = cn;
	xtalNum = xi+1;
	timeAvg = htime->GetMean();
	normAvg = hnorm->GetMean();
	burstAvg = hburst->GetMean();
	probeAvg = hprobe->GetMean();
	timeRms = htime->GetRMS();
	normRms = hnorm->GetRMS();
	burstRms = hburst->GetRMS();
	probeRms = hprobe->GetRMS();
	
	// Fill if the hists weren't empty.
	if (probeAvg > 100.0) {
	  tree->Fill();
	}
      }
    }
  }

  tree->Write();
}


void LongDoublePulsePlotter::initGainPerRun()
{
  // Make sure we want the plots.
  if (!writeGainPerRun_) {
    return;
  }

  // Grab the TFS file.
  TString hname;
  TString title;
  TString xunit;
  TString yunit;
  art::ServiceHandle<art::TFileService> tfs;
  auto dir0 = tfs->mkdir("RunHists");
  TString runDir = TString::Format("Run%05i", runNum_);
  auto dir1 = dir0.mkdir(runDir.Data());

  // Initialize the calo/xtal raw histograms.
  for (int cn = 1; cn < 25; ++cn) {

    TString dirname(TString::Format("calo%02i", cn));
    auto dir2 = dir1.mkdir(dirname.Data());

    for (int xi = 0; xi < 54; ++xi) {

      int idx = 100 * cn + xi;
      int bins = 50;
      hname = TString::Format("h1_xtal%02i_probe_energy", xi+1);
      title = TString::Format("C%02i.X%02i - Probe Pulse Energy;", cn, xi+1);
      xunit = TString::Format("energy [p.e.];");
      auto ph1 = dir2.make<TH1F>(hname, title + xunit, bins, 0, 0);
      mapHistMapProbePerXtal_[runNum_][idx] = ph1;

      hname = TString::Format("h1_xtal%02i_probe_time", xi+1);
      title = TString::Format("C%02i.X%02i - Probe Pulse Time;", cn, xi+1);
      xunit = TString::Format("#delta t [#mu s];");
      auto ph2 = dir2.make<TH1F>(hname, title + xunit, bins, 0, 0);
      mapHistMapTimePerXtal_[runNum_][idx] = ph2;

      hname = TString::Format("h1_xtal%02i_burst_energy", xi+1);
      title = TString::Format("C%02i.X%02i - Burst Pulse Energy;", cn, xi+1);
      xunit = TString::Format("total energy [p.e.];");
      auto ph3 = dir2.make<TH1F>(hname, title + xunit, bins, 0, 0);
      mapHistMapBurstPerXtal_[runNum_][idx] = ph3;

      hname = TString::Format("h1_xtal%02i_norm_energy", xi+1);
      title = TString::Format("C%02i.X%02i - Normalization Energy;", cn, xi+1);
      xunit = TString::Format("energy [p.e.];");
      auto ph4 = dir2.make<TH1F>(hname, title + xunit, bins, 0, 0);
      mapHistMapNormPerXtal_[runNum_][idx] = ph4;
    }
  }
}


void LongDoublePulsePlotter::fillGainPerRun(art::Event const &e)
{
  // Make sure we want the plots.
  if (!writeGainPerRun_) {
    return;
  }

  // Grab our data.
  const auto &caloCrystalHitCol =
    *e.getValidHandle<CaloCrystalHitArtRecordCollection>(
      {fitterModuleLabel_, fitterInstanceLabel_});

  // Convert the ranges to clock ticks.
  int burstCount = 0;
  double burstRangeMin = burstRangeMin_ / 1.25e-3;
  double burstRangeMax = burstRangeMax_ / 1.25e-3;
  double probeRangeMin = probeRangeMin_ / 1.25e-3;
  double probeRangeMax = probeRangeMax_ / 1.25e-3;
  std::map<int, double> mapBurstSum;
  std::map<int, double> mapBurstTime;

  // Loop over the crystals
  calo_for_each(caloCrystalHitCol, [&](const auto &hit) {

      if (hit.laserHit == 1) {
	int idx = 100*hit.caloNum + hit.xtalNum;
	
	if ((hit.time > burstRangeMin) && (hit.time < burstRangeMax)) {
	  mapBurstSum[idx] += hit.energy;
	  mapBurstTime[idx] = hit.time * 1.25e-3; // use last pulse
	  burstCount += 1;
	}
      }
    });

  // Loop over the crystals
  calo_for_each(caloCrystalHitCol, [&](const auto &hit) {

      if (hit.laserHit == 1) {
	int idx = 100*hit.caloNum + hit.xtalNum;
	
	if ((hit.time > probeRangeMin) && (hit.time < probeRangeMax)) {

	  if ((burstCount > 100) && (hit.energy > 100)) {

	    double dt = hit.time * 1.25e-3;// - mapBurstTime[idx];
	    mapHistMapTimePerXtal_[runNum_][idx]->Fill(dt);
	    mapHistMapProbePerXtal_[runNum_][idx]->Fill(hit.energy);
	    mapHistMapBurstPerXtal_[runNum_][idx]->Fill(mapBurstSum[idx]);

	  } else if (hit.energy > 10) {
	    
	    mapHistMapNormPerXtal_[runNum_][idx]->Fill(hit.energy);
	  }	    
	}
      }
    });
}


void LongDoublePulsePlotter::closeGainPerRun()
{
  if (!writeGainPerRun_) {
    return;
  }
}


void LongDoublePulsePlotter::initGainSummary()
{
  if (!writeGainSummary_) {
    return;
  }

  static bool initialized = false;
  
  if (!initialized) {
    // Grab the TFS file.
    TString hname;
    TString title;
    TString xunit;
    TString yunit;
    art::ServiceHandle<art::TFileService> tfs;
    auto dir1 = tfs->mkdir("Aggregate");
    auto dir2 = dir1.mkdir("summary");

    // Allocate the histograms.
    hname = TString("h2_gain_curve_vs_time");
    title = TString("Gain Curve All Xtals;");
    xunit = TString("time [#mu s];");
    yunit = TString("gain;");
    histGainCurveVsTime_ = dir2.make<TH2F>(hname, title + xunit + yunit,
					   201, 0, 200,
					   101, 0, 2);

    hname = TString("h2_gain_sag_vs_load");
    title = TString("Gain Sag vs Load;");
    xunit = TString("integrated p.e.;");
    yunit = TString("gain;");
    histGainSagVsLoad_ = dir2.make<TH2F>(hname, title + xunit + yunit,
					 100, 0, 10000,
					 101, 0, 2);

    // Initialize the calo/xtal raw histograms.
    for (int cn = 1; cn < 25; ++cn) {

      TString dirname(TString::Format("calo%02i", cn));
      auto dir2 = dir1.mkdir(dirname.Data());

      for (int xi = 0; xi < 54; ++xi) {

	int idx = 100 * cn + xi;
     	hname = TString::Format("h2_gain_xtal%02i", xi+1);
     	title = TString::Format("Gain C%02i.X%02i;", cn, xi+1);
	xunit = TString("#delta t [#mu s];");
	yunit = TString("gain;");
     	auto ph = dir2.make<TH2F>(hname, title + xunit + yunit, 
     				  255, 0, 255,   // x: test load
     				  100, 0, 2);    // y: gain sag
	
     	histMapGainVsTime_[idx] = ph;
       }
     }

    initialized = true;
  }
}


void LongDoublePulsePlotter::fillGainSummary(art::Event const &e)
{
  if (!writeGainSummary_) {
    return;
  }
  
  static bool hasNorm;
  static bool hasTest;
  static std::map<int, double> mapBurstSumPerXtal;
  static std::map<int, double> mapProbeValPerXtal;
  static std::map<int, double> mapBurstTimePerXtal;
  static std::map<int, double> mapProbeTimePerXtal;
  static std::map<int, double> mapNormValPerXtal;

  // Grab our data.
  const auto &caloCrystalHitCol =
    *e.getValidHandle<CaloCrystalHitArtRecordCollection>(
      {fitterModuleLabel_, fitterInstanceLabel_});

  // Convert the ranges to clock ticks.
  double burstRangeMin = burstRangeMin_ / 1.25e-3;
  double burstRangeMax = burstRangeMax_ / 1.25e-3;
  double probeRangeMin = probeRangeMin_ / 1.25e-3;
  double probeRangeMax = probeRangeMax_ / 1.25e-3;
  int burstCount = 0;

  // Loop over the crystals
  calo_for_each(caloCrystalHitCol, [&](const auto &hit) {

      if (hit.laserHit == 1) {
	int idx = 100*hit.caloNum + hit.xtalNum;
	
	if ((hit.time > burstRangeMin) && (hit.time < burstRangeMax)) {
	  mapBurstSumPerXtal[idx] += hit.energy;
	  mapBurstTimePerXtal[idx] = hit.time * 1.25e-3;
	  burstCount += 1;
	}
      }
    });

  if (burstCount > 100) {
    hasTest = true;
  } else {
    hasNorm = true;
  }

  // Loop over the crystals
  calo_for_each(caloCrystalHitCol, [&](const auto &hit) {

      if (hit.laserHit == 1) {
	int idx = 100*hit.caloNum + hit.xtalNum;

	if ((hit.time > probeRangeMin) && (hit.time < probeRangeMax)) {

	  if (burstCount > 10) {
	    mapProbeValPerXtal[idx] = hit.energy;
	    mapProbeTimePerXtal[idx] = hit.time * 1.25e-3;
	  } else {
	    mapNormValPerXtal[idx] = hit.energy;
	  }	    
	}
      }
    });

  // Bail if we don't have both fills yet.
  if (!(hasTest && hasNorm)) {
    return;
  }

  // Fill the histos if we have a test and norm fill.
  for (int cn = 1; cn <= 24; ++cn) {
    for (int xi = 0; xi < 54; ++xi) {

      int idx = 100 * cn + xi;
      double norm = mapNormValPerXtal[idx];	    
      double burstSum = mapBurstSumPerXtal[idx];
      double probeVal = mapProbeValPerXtal[idx];
      double burstTime = mapBurstTimePerXtal[idx];
      double probeTime = mapProbeTimePerXtal[idx];

      if (probeVal > 10) {
	histGainCurveVsTime_->Fill(probeTime - burstTime, probeVal / norm);
	histGainSagVsLoad_->Fill(burstSum, probeVal / norm);
	histMapGainVsTime_[idx]->Fill(probeTime - burstTime, probeVal / norm);
      }

      mapNormValPerXtal[idx] = 0;
      mapBurstSumPerXtal[idx] = 0;
      mapProbeValPerXtal[idx] = 0;
      mapBurstTimePerXtal[idx] = 0;
      mapProbeTimePerXtal[idx] = 0;
    }
  }

  // Reset flags.
  hasNorm = false;
  hasTest = false;
}


void LongDoublePulsePlotter::closeGainSummary()
{
  if (!writeGainSummary_) {
    return;
  }
}


DEFINE_ART_MODULE(LongDoublePulsePlotter)

}

