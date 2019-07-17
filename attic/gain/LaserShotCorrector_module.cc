////////////////////////////////////////////////////////////////////////
// Class:       LaserShotCorrector
// Plugin Type: producer (art v2_09_02)
// File:        LaserShotCorrector_module.cc
//
// Generated at Thu Apr  5 03:47:41 2018 by Matthias Smith using cetskelgen
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
#include "gm2calo/util/CaloForEach.hh"
#include "gm2dataproducts/calo/LaserArtRecord.hh"

namespace gm2calo {
  class LaserShotCorrector;
}


class gm2calo::LaserShotCorrector : public art::EDProducer {
public:
  explicit LaserShotCorrector(fhicl::ParameterSet const & p);
  // The compiler-generated destructor is fine for non-base
  // classes without bare pointers or other resource use.

  // Plugins should not be copied or assigned.
  LaserShotCorrector(LaserShotCorrector const &) = delete;
  LaserShotCorrector(LaserShotCorrector &&) = delete;
  LaserShotCorrector & operator = (LaserShotCorrector const &) = delete;
  LaserShotCorrector & operator = (LaserShotCorrector &&) = delete;

  // Required functions.
  void produce(art::Event & e) override;

private:

  void correctGain(LaserEventArtRecord &hit);

  std::string thisInstanceLabel_;
  std::string inputModuleLabel_;
  std::string inputInstanceLabel_;
};


gm2calo::LaserShotCorrector::LaserShotCorrector(fhicl::ParameterSet const & p)
  : thisInstanceLabel_("corrector"),
    inputModuleLabel_(
      p.get<std::string>("inputModuleLabel", "laserAggregator")),
    inputInstanceLabel_(
      p.get<std::string>("inputInstanceLabel", "aggregator"))
{
  produces<LaserEventArtRecordCollection>(thisInstanceLabel_);
}


void gm2calo::LaserShotCorrector::produce(art::Event &e)
{
  // The art records to store in-fill laser data.
  std::unique_ptr<LaserEventArtRecordCollection> 
    data(new LaserEventArtRecordCollection);

  // Get the input xtal hits.
  const auto &inputDataCol = 
    *e.getValidHandle<LaserEventArtRecordCollection>(
      {inputModuleLabel_, inputInstanceLabel_});

    // Grab the data from this event (fill).
  for (const auto &rec : inputDataCol) {
    auto datum = rec;
    correctGain(datum);
    data->push_back(datum);
  }

  // Put the corrected data into the event.
  e.put(std::move(data), thisInstanceLabel_);
}


void gm2calo::LaserShotCorrector::correctGain(LaserEventArtRecord &hit)
{
  // TODO
}


DEFINE_ART_MODULE(gm2calo::LaserShotCorrector)
