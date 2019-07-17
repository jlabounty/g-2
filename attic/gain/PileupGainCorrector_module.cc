////////////////////////////////////////////////////////////////////////
// Class:       PileupGainCorrector
// Plugin Type: producer (art v2_09_02)
// File:        PileupGainCorrector_module.cc
//
// Generated at Thu Apr  5 02:23:45 2018 by Matthias Smith using cetskelgen
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
#include <queue>

// gm2 includes
#include "gm2calo/util/CaloForEach.hh"
#include "gm2dataproducts/calo/CrystalHitArtRecord.hh"
#include "gm2dataproducts/calo/LaserArtRecord.hh"

namespace gm2calo {
  class PileupGainCorrector;
}


class gm2calo::PileupGainCorrector : public art::EDProducer {
public:
  explicit PileupGainCorrector(fhicl::ParameterSet const & p);
  // The compiler-generated destructor is fine for non-base
  // classes without bare pointers or other resource use.

  // Plugins should not be copied or assigned.
  PileupGainCorrector(PileupGainCorrector const &) = delete;
  PileupGainCorrector(PileupGainCorrector &&) = delete;
  PileupGainCorrector & operator = (PileupGainCorrector const &) = delete;
  PileupGainCorrector & operator = (PileupGainCorrector &&) = delete;

  // Required functions.
  void produce(art::Event & e) override;

private:

  void correctGain(CrystalHitArtRecord &hit, 
		   std::queue<CrystalHitArtRecord> &prevHits);

  // Declare member data here.
  std::string thisInstanceLabel_;
  std::string inputModuleLabel_;
  std::string inputInstanceLabel_;

  double maxDeltaTime_;
};


gm2calo::PileupGainCorrector::PileupGainCorrector(fhicl::ParameterSet const & p)
  : thisInstanceLabel_("corrector"),
    inputModuleLabel_(
      p.get<std::string>("inputModuleLabel", "islandFitterDAQ")),
    inputInstanceLabel_(
      p.get<std::string>("inputInstanceLabel", "fitter")),
    maxDeltaTime_(p.get<int>("maxDeltaTime", 80))
{
  produces<CaloCrystalHitArtRecordCollection>(thisInstanceLabel_);
}


void gm2calo::PileupGainCorrector::produce(art::Event & e)
{
  // The art records to store in-fill laser data.
  std::unique_ptr<CaloCrystalHitArtRecordCollection> 
    dataCol(new CaloCrystalHitArtRecordCollection);

  // Get the input xtal hits.
  const auto &xhDataCol = 
    *e.getValidHandle<CaloCrystalHitArtRecordCollection>({
      inputModuleLabel_, inputInstanceLabel_});

  std::map<int, std::queue<CrystalHitArtRecord>> prevHits;

  // Grab the data from this event (fill).
  for (const auto &round : xhDataCol) {

    CaloCrystalHitArtRecord calo_hits;

    for (const auto &calo : round) {

      MatrixCrystalHitArtRecord matrix_hits;
      
      for (const auto &hit : calo) {

	auto h = hit;
	int idx = 100 * hit.caloNum + hit.xtalNum;

	this->correctGain(h, prevHits[idx]);
	prevHits[idx].push(h);

	matrix_hits.crystalHits.push_back(h);
      }
      
      calo_hits.matrixCrystalHits.push_back(matrix_hits);
     }
    
    dataCol->push_back(calo_hits);
  }

  // calo_for_each(xhDataCol, [&](const auto &hit) {
 
  //     auto h = hit;
  //     int idx = 100 * hit.caloNum + hit.xtalNum;

  //     this->correctGain(h, prevHits[idx]);
  //     prevHits[idx].push(h);

  //     dataCol->push_back(h);
  //   });

  // Put the corrected data into the event.
  e.put(std::move(dataCol), thisInstanceLabel_);
}


void gm2calo::PileupGainCorrector::correctGain(CrystalHitArtRecord &hit, 
					       std::queue<CrystalHitArtRecord> &prevHits)
{
  // Return if queue is empty.
  if (prevHits.empty()) {
    return;
  }

  // Else, prune the previous hit queue.
  while (hit.time - prevHits.front().time > maxDeltaTime_) {
    prevHits.pop();
    if (prevHits.empty()) {
      return;
    }
  }
   
  // Now apply the correction for remaining hits, TODO
}


DEFINE_ART_MODULE(gm2calo::PileupGainCorrector)
