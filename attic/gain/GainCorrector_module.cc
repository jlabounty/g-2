////////////////////////////////////////////////////////////////////////
// Class:       GainCorrector
// Module Type: producer
// File:        GainCorrector_module.cc
//
// This module should not really be used in any real context...
// It basically does nothing. Was originally created as a placeholder/example
// Aaron Fienberg, May 2018
//
//
// Generated at Sat Jan 26 10:30:03 2016 by Kim Siang Khaw using artmod
// from cetpkgsupport v1_08_04.
////////////////////////////////////////////////////////////////////////

// art includes
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

// data product includes
#include "gm2dataproducts/calo/CrystalHitArtRecord.hh"
#include "gm2dataproducts/calo/CaloCalibrationConstant.hh"

// ROOT includes
#include <iostream>
#include <algorithm>

#include "gm2calo/util/CaloDataProductTransformers.hh"

// gm2calo namespace
using namespace gm2calo;

namespace gm2calo {
class GainCorrector;
}

class gm2calo::GainCorrector : public art::EDProducer {
 public:
  explicit GainCorrector(fhicl::ParameterSet const& p);

  // Required functions.
  void produce(art::Event& event) override;

 private:
  std::string correctorInstanceLabel_;
  std::string constantType_;
  std::string calibratorModuleLabel_;
  std::string calibratorInstanceLabel_;

  double gainCorrection_;
  std::vector<double> correctionConstants_;

  // message facility
  mf::LogInfo info_;
};

gm2calo::GainCorrector::GainCorrector(fhicl::ParameterSet const& p)
    : correctorInstanceLabel_(
          p.get<std::string>("correctorInstanceLabel", "corrector")),
      constantType_(p.get<std::string>("constantType", "gainCorrector")),
      calibratorModuleLabel_(
          p.get<std::string>("calibratorModuleLabel", "energyCalibrator")),
      calibratorInstanceLabel_(
          p.get<std::string>("calibratorInstanceLabel", "calibrator")),
      gainCorrection_(p.get<double>("gainCorrection", 1.0)),
      info_("GainCorrector") {
  produces<CrystalHitArtRecordCollection>(correctorInstanceLabel_);
  produces<CaloCrystalHitViewArtRecordCollection>(correctorInstanceLabel_);
  produces<CaloCalibrationConstantCollection>(correctorInstanceLabel_);

  correctionConstants_ = std::vector<double>(54, gainCorrection_);
}

void gm2calo::GainCorrector::produce(art::Event& event) {
  mf::LogVerbatim("gm2calo::GainCorrector")
      << "Enter gm2calo::GainCorrector for " << event.id();

  // get the data
  const auto& oldCaloHits =
      *event.getValidHandle<CaloCrystalHitViewArtRecordCollection>(
          {calibratorModuleLabel_, calibratorInstanceLabel_});

  // prepare output correction constants collection
  std::unique_ptr<CaloCalibrationConstantCollection> correctionCollection(
      new CaloCalibrationConstantCollection);

  for (const auto& caloView : oldCaloHits) {
    gm2calo::CaloCalibrationConstant caloConstant(
        constantType_, event.run(), caloView.caloNum, correctionConstants_);
  }

  // apply gain correction and put new data into the event
  transformAndPutCaloCollection(
      event, oldCaloHits, this, correctorInstanceLabel_,
      [this](auto& hit, const auto& oldPtr) {
        hit.uncalibratedHit = oldPtr;

        unsigned int xtalIndex = hit.xtalNum;
        if (xtalIndex < correctionConstants_.size()) {
          hit.energy *= correctionConstants_[xtalIndex];
        }
      });

  // put the correction constants into the event
  event.put(std::move(correctionCollection), correctorInstanceLabel_);

  mf::LogVerbatim("gm2calo::GainCorrector")
      << "Exit gm2calo::GainCorrector for " << event.id();
}

DEFINE_ART_MODULE(gm2calo::GainCorrector)
