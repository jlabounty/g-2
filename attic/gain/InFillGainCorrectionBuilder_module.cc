////////////////////////////////////////////////////////////////////////
// Class:       InFillGainCorrectionBuilder
// Plugin Type: producer (art v2_09_02)
// File:        InFillGainCorrectionBuilder_module.cc
//
// Generated at Fri Apr  6 04:18:11 2018 by Matthias Smith using cetskelgen
// from cetlib version v3_01_03.
////////////////////////////////////////////////////////////////////////

#include "art/Framework/Core/EDProducer.h"
#include "art/Framework/Core/ModuleMacros.h"
#include "art/Framework/Principal/Event.h"
#include "art/Framework/Principal/Handle.h"
#include "art/Framework/Principal/Run.h"
#include "art/Framework/Principal/SubRun.h"
#include "canvas/Utilities/InputTag.h"
#include "fhiclcpp/ParameterSet.h"
#include "messagefacility/MessageLogger/MessageLogger.h"

#include <memory>

// gm2 includes
#include "gm2dataproducts/calo/LaserArtRecord.hh"
#include "gm2dataproducts/calo/GainCorrectionArtRecord.hh"
#include "gm2dataproducts/calo/CaloSplashArtRecord.hh"

namespace gm2calo {
  class InFillGainCorrectionBuilder;
}


class gm2calo::InFillGainCorrectionBuilder : public art::EDProducer {
public:
  explicit InFillGainCorrectionBuilder(fhicl::ParameterSet const & p);
  // The compiler-generated destructor is fine for non-base
  // classes without bare pointers or other resource use.

  // Plugins should not be copied or assigned.
  InFillGainCorrectionBuilder(InFillGainCorrectionBuilder const &) = delete;
  InFillGainCorrectionBuilder(InFillGainCorrectionBuilder &&) = delete;
  InFillGainCorrectionBuilder & operator = (InFillGainCorrectionBuilder const &) = delete;
  InFillGainCorrectionBuilder & operator = (InFillGainCorrectionBuilder &&) = delete;

  // Required functions.
  void produce(art::Event &e) override;
  void beginSubRun(art::SubRun &s) override;

private:

  // Utility functions
  int getSequenceIndex(double t);

  // Dataproduct labels
  std::string thisInstanceLabel_;
  std::string syncModuleLabel_;
  std::string syncInstanceLabel_;
  std::string inFillModuleLabel_;
  std::string inFillInstanceLabel_;
  std::string eofModuleLabel_;
  std::string eofInstanceLabel_;
  std::string laserConfigModuleLabel_;
  std::string laserConfigInstanceLabel_;

  std::vector<double> nominalTimes_;
};


gm2calo::InFillGainCorrectionBuilder::InFillGainCorrectionBuilder(fhicl::ParameterSet const & p)
  : thisInstanceLabel_("builder"),
    syncModuleLabel_(
      p.get<std::string>("syncModuleLabel", "laserEventSorter")),
    syncInstanceLabel_(
      p.get<std::string>("syncInstanceLabel", "syncLaser")),
    inFillModuleLabel_(
      p.get<std::string>("inFillModuleLabel", "laserEventSorter")),
    inFillInstanceLabel_(
      p.get<std::string>("inFillInstanceLabel", "inFillLaser")),
    eofModuleLabel_(
      p.get<std::string>("eofModuleLabel", "laserEventSorter")),
    eofInstanceLabel_(
      p.get<std::string>("eofInstanceLabel", "eofLaser")),
    laserConfigModuleLabel_(
      p.get<std::string>("laserConfigModuleLabel", "laserConfigReader")),
    laserConfigInstanceLabel_(
      p.get<std::string>("laserConfigInstanceLabel", "reader"))
{
  produces<InFillArtRecordCollection>(thisInstanceLabel_);
}


void gm2calo::InFillGainCorrectionBuilder::beginSubRun(art::SubRun &s) 
{
  // Try getting the LaserConfig.
  const auto &cfg = 
    *s.getValidHandle<gm2calo::LaserConfigArtRecord>(
      {laserConfigModuleLabel_, laserConfigInstanceLabel_});

  // Set the nominal expected times.
  nominalTimes_.resize(cfg.inFillPulseCount * (cfg.inFillShiftReps + 1));
  double t0 = 0.8 * cfg.inFillPulseDelay; // convert to clock ticks.
  double dt = 0.8 * cfg.inFillShiftTime;
  double pulseOffset = 0.8* cfg.inFillPulsePeriod;

  for (uint n = 0; n < nominalTimes_.size(); ++n) {
    double dt2 = (n / (cfg.inFillShiftReps + 1)) * pulseOffset;
    nominalTimes_[n] = t0 + dt * (n % (cfg.inFillShiftReps + 1)) + dt2;
  }
}


void gm2calo::InFillGainCorrectionBuilder::produce(art::Event & e)
{
  // The art records to store in-fill laser data.
  std::unique_ptr<InFillArtRecordCollection>
    dataCol(new InFillArtRecordCollection);

  // Try getting the splash integrals.
  std::map<int, long> splashMap;

  art::Handle<gm2calo::CaloSplashArtRecordCollection> sHandle;
  if (e.getByLabel({"splashFinder", ""}, sHandle)) {

    for (auto it = (*sHandle).begin(); it != (*sHandle).end(); ++it) {

      splashMap[it->caloNum] = it->integral;
    }
  }

  // Load the art records for LaserEvents for sync/inFill/eof.
  const auto &syncDataCol = 
    *e.getValidHandle<LaserEventArtRecordCollection>(
      {syncModuleLabel_, syncInstanceLabel_});

  const auto &inFillDataCol = 
    *e.getValidHandle<LaserEventArtRecordCollection>(
      {inFillModuleLabel_, inFillInstanceLabel_});

  const auto &eofDataCol = 
    *e.getValidHandle<LaserEventArtRecordCollection>(
      {eofModuleLabel_, eofInstanceLabel_});

  // Variables to track sync/eof over multiple events.
  static std::map<int, std::vector<double>> mapSyncEnergy;
  static std::map<int, std::vector<double>> mapEofEnergy;
  
  // Accumulate sync/eof energies.
  for (const auto &rec: syncDataCol) {
    int idx = 100 * rec.sipm->caloNum + rec.sipm->xtalNum;
    mapSyncEnergy[idx].push_back(rec.sipm->energy);
  }

  for (const auto &rec: eofDataCol) {
    int idx = 100 * rec.sipm->caloNum + rec.sipm->xtalNum;
    mapEofEnergy[idx].push_back(rec.sipm->energy);
  }

  // If the event has in-fill data, combine all data and ship.
  std::map<int, InFillArtRecord> mapInFill;
  for (const auto &rec: inFillDataCol) {

    int idx = 100 * rec.sipm->caloNum + rec.sipm->xtalNum;

    auto d = mapInFill[idx];
    d.gpsTimeStamp = rec.fill->gpsTimeStamp;
    d.splashIntegral = splashMap[rec.sipm->caloNum];
    d.bunchNum = rec.fill->bunchNum;
    d.caloNum = rec.sipm->caloNum;
    d.xtalNum = rec.sipm->xtalNum;

    int N;
    double x1, x2;

    // Calculate mean/sigma for sync energy.
    N = mapSyncEnergy[idx].size();
    x1 = 0.0;
    x2 = 0.0;
    
    for (auto &val : mapSyncEnergy[idx]) {
      x1 += val;
      x2 += val * val;
    }

    d.meanSyncEnergy = x1 / N;
    d.sigmaSyncEnergy = sqrt((x1 / N) * (x1 / N) - x2 / N);
    
    // Calculate mean/sigma for eof energy.
    N = mapEofEnergy[idx].size();
    x1 = 0.0;
    x2 = 0.0;
    
    for (auto &val : mapEofEnergy[idx]) {
      x1 += val;
      x2 += val * val;
    }

    d.meanEofEnergy = x1 / N;
    d.sigmaEofEnergy = sqrt((x1 / N) * (x1 / N) - x2 / N);
    
    // Add in-fill pulses.
    d.index.push_back(getSequenceIndex(rec.sipm->time));
    d.energy.push_back(rec.sipm->energy);
    d.time.push_back(rec.sipm->time);
    d.chi2.push_back(rec.sipm->chi2);

    mapInFill[idx] = d;
  }  

  // Now add the in-fill correction data from the map.
  for (auto &entry : mapInFill) {
    dataCol->push_back(entry.second);

    // Empty accumulation vectors.
    int idx = 100 * entry.second.caloNum + entry.second.xtalNum;
    mapEofEnergy[idx].resize(0);
    mapSyncEnergy[idx].resize(0);
  }

  e.put(std::move(dataCol), thisInstanceLabel_);
}


int gm2calo::InFillGainCorrectionBuilder::getSequenceIndex(double t)
{
  if (t < nominalTimes_[0]) {
    return 0;
  }

  uint i = 0;
  for (i = 0; i < nominalTimes_.size(); ++i) {
    if (nominalTimes_[i] > t) {
      break;
    }
  }

  double dt1 = t - nominalTimes_[i-1];
  double dt2 = nominalTimes_[i] - t;
  
  return dt1 < dt2 ? i-1 : i;
}


DEFINE_ART_MODULE(gm2calo::InFillGainCorrectionBuilder)
