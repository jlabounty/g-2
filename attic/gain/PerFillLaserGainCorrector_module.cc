////////////////////////////////////////////////////////////////////////
// Class:       PerFillLaserGainCorrector
// Module Type: producer
// File:        PerFillLaserGainCorrector_module.cc
//
// Generated at Sat Jan 26 10:30:03 2016 by Kim Siang Khaw using artmod
// from cetpkgsupport v1_08_04.
////////////////////////////////////////////////////////////////////////

// This module calculates the mean laser pulse E in a fill, then compares this
// to a baseline
// run (typically the same one used for energy calibration) and uses the ratio
// and a gain
// correction factor. The electron pulses are then corrected by this factor.
// This compensates for drift in SiPM gain between calibration runs.
// Tom Stuttard (12th June 2016)
//

// also does a correction based on the pins (source monitors)
// like the SiPM pulse correction, the pin correction is completed
// based on comparison to a baseline run or set of runs
// Aaron Fienberg

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
#include "gm2dataproducts/calo/LaserArtRecord.hh"

// ROOT includes
#include <iostream>
#include <algorithm>

// temporary for slac analysis
constexpr int pin1channel = 2;
constexpr int pin2channel = 4;

// gm2calo namespace
using namespace gm2calo;

namespace gm2calo {
class PerFillLaserGainCorrector;
}

class gm2calo::PerFillLaserGainCorrector : public art::EDProducer {
 public:
  explicit PerFillLaserGainCorrector(fhicl::ParameterSet const& p);

  // Required functions.
  void produce(art::Event& event) override;

 private:
  // Producer labels
  std::string correctorInstanceLabel_;
  std::string fitterModuleLabel_;
  std::string fitterInstanceLabel_;
  std::string calibratorModuleLabel_;
  std::string calibratorInstanceLabel_;
  std::string laserModuleLabel_;
  std::string laserInstanceLabel_;

  double laserPulseTimeThreshold_;
  std::map<int, long double> xtalHitBaselineMeanLaserEnergy_;

  bool usePinCorrection_;
  double pinBaselineMeanEnergy_;
  double pinThreshold_;

  // message facility
  mf::LogInfo info_;
};

gm2calo::PerFillLaserGainCorrector::PerFillLaserGainCorrector(
    fhicl::ParameterSet const& p)
    : correctorInstanceLabel_(
          p.get<std::string>("correctorInstanceLabel", "corrector")),
      fitterModuleLabel_(
          p.get<std::string>("fitterModuleLabel", "islandFitter")),
      fitterInstanceLabel_(p.get<std::string>("fitterInstanceLabel", "fitter")),
      calibratorModuleLabel_(
          p.get<std::string>("calibratorModuleLabel", "energyCalibrator")),
      calibratorInstanceLabel_(
          p.get<std::string>("calibratorInstanceLabel", "calibrator")),
      laserModuleLabel_(
          p.get<std::string>("laserModuleLabel", "monitorProcessor")),
      laserInstanceLabel_(
          p.get<std::string>("laserInstanceLabel", "laserProcessor")),
      laserPulseTimeThreshold_(p.get<double>("laserPulseTimeThreshold", 3000.)),
      usePinCorrection_(p.get<bool>("usePinCorrection")),
      pinBaselineMeanEnergy_(0.0),
      pinThreshold_(p.get<double>("pinThreshold", 500.0)),
      info_("PerFillLaserGainCorrector") {
  produces<CaloCrystalHitArtRecordCollection>(correctorInstanceLabel_);

  // Parse constants
  for (int i_xtal = 0; i_xtal < 54; ++i_xtal) {
    xtalHitBaselineMeanLaserEnergy_[i_xtal] =
        p.get<long double>("constants.xtal" + std::to_string(i_xtal));
  }
  if (usePinCorrection_) {
    pinBaselineMeanEnergy_ = p.get<double>("constants.pinAvg");
  }
}

void gm2calo::PerFillLaserGainCorrector::produce(art::Event& event) {
  std::cout << "Enter gm2calo::PerFillLaserGainCorrector::produce" << std::endl;

  // get the fit result data
  art::Handle<gm2calo::CaloCrystalHitArtRecordCollection>
      calofitresultDataHandle;
  event.getByLabel(fitterModuleLabel_, fitterInstanceLabel_,
                   calofitresultDataHandle);
  const auto& calofitresultData = *calofitresultDataHandle;

  // get the xtal data
  art::Handle<gm2calo::CaloCrystalHitArtRecordCollection> dataHandle;
  event.getByLabel(calibratorModuleLabel_, calibratorInstanceLabel_,
                   dataHandle);
  const auto& caloUncorrectedData = *dataHandle;

  // create a new collection of crystal hit art record from uncorrected crystal
  // hit art
  // records that will be added to the event
  std::unique_ptr<CaloCrystalHitArtRecordCollection> calo_crystalhit_collection(
      new CaloCrystalHitArtRecordCollection);

  //-----------------------------------------------------------------------------
  // find mean laser E deposit in each crystal
  //-----------------------------------------------------------------------------

  // use fit results collection here (independent then of energy calibration)

  std::map<int, unsigned long> laserNumFitResults;
  std::map<int, long double> laserFitResultMeanEnergy;
  for (unsigned int i_xtal = 0; i_xtal < 54; i_xtal++) {
    laserNumFitResults[i_xtal] = 0;
    laserFitResultMeanEnergy[i_xtal] = 0;
  }

  // loop over the calorimeters
  for (const auto& caloFitResult : calofitresultData) {
    // loop over the fitresultmatrices
    for (const auto& matrixFitResult : caloFitResult.matrixCrystalHits) {
      // loop over the fitresults
      for (const auto& fitResult : matrixFitResult.crystalHits) {
        // Record E sum if from laser (cut by time, only applicable to SLAC) and
        // if passes fit quality check
        if ((fitResult.time > laserPulseTimeThreshold_ ||
             fitResult.time < 1000) &&
            fitResult.chi2 > 0) {
          if (fitResult.energy > 1000) {
            laserNumFitResults[fitResult.xtalNum]++;
            laserFitResultMeanEnergy[fitResult.xtalNum] +=
                fitResult.energy;  // sum E to start with, calc mean later
          }
        }

      }  // end loop over the fitResults
    }
  }

  // check didn't find weird xtal numbers
  if (laserFitResultMeanEnergy.size() != 54) {
    throw cet::exception("PerFillLaserGainCorrector")
        << "Unexpected xtal numbers found\n";
    return;
  }

  // calculate mean laser pulse E in each crystal for this fill and
  // corresponding gain correction
  std::map<int, long double> gainCorrection;
  for (unsigned int i_xtal = 0; i_xtal < 54; i_xtal++) {
    laserFitResultMeanEnergy[i_xtal] /=
        static_cast<double>(laserNumFitResults[i_xtal]);
    gainCorrection[i_xtal] = laserNumFitResults[i_xtal] > 0
                                 ? xtalHitBaselineMeanLaserEnergy_[i_xtal] /
                                       laserFitResultMeanEnergy[i_xtal]
                                 : 1.;  // No correction if no laser is fill
  }

  // do pin correction if needed

  art::Handle<gm2calo::LaserMonitorArtRecordCollection> monitorHandle;
  double sourceMonitorCorrection = 1.0;

  if (usePinCorrection_) {
    bool success = event.getByLabel(laserModuleLabel_, laserInstanceLabel_,
                                    monitorHandle);
    if (!success) {
      // throw cet::exception("SLACAnalyzer_module") << "There is no
      // LaserMonitorArtRecordCollection\n";
      // throw cet::exception("PerFillLaserGainCorrector") << "pin correction
      // requested but monitor art record not found!\n";
      std::cout << "gm2calo::PerFillLaserGainCorrector: Pin correction "
                   "requested but monitor art record not found!" << std::endl;
      usePinCorrection_ = false;
    }
  }

  if (usePinCorrection_) {
    const auto& monitorRecord = *monitorHandle;
    double runningPinSum = 0.0;
    int nPinPulses = 0;
    for (const auto& monitor : monitorRecord) {
      if ((monitor.chanNum == pin1channel ||
           monitor.chanNum == pin2channel) &&
          monitor.amplitude > pinThreshold_) {
        ++nPinPulses;
        runningPinSum += monitor.amplitude;
      }
    }
    // laser fills will have no pin pulses for now
    sourceMonitorCorrection =
        nPinPulses > 0 ? runningPinSum / nPinPulses / pinBaselineMeanEnergy_
                       : 1.0;
  }

  //-----------------------------------------------------------------------------
  // loop over calo crystalhit,  then matrix, then single crystalhit
  //-----------------------------------------------------------------------------

  // Apply correction to xtal hits

  // loop over the calorimeters
  for (const auto& caloCrystalHit : caloUncorrectedData) {
    //  create crystalhit collection
    gm2calo::MatrixCrystalHitArtRecordCollection matrix_crystalhit_collection;

    // loop over the crystalhitmatrices
    for (const auto& matrixCrystalHit : caloCrystalHit.matrixCrystalHits) {
      //  create crystalhit collection
      gm2calo::CrystalHitArtRecordCollection crystalhit_collection;

      // loop over the crystalhits
      for (const auto& crystalHit : matrixCrystalHit.crystalHits) {
        // store the fit results and copy over some parameters
        gm2calo::CrystalHitArtRecord crystalhit;
        crystalhit.amcHeader = crystalHit.amcHeader;
        crystalhit.riderChannelHeader = crystalHit.riderChannelHeader;
        crystalhit.riderWaveformHeader = crystalHit.riderWaveformHeader;
        crystalhit.fillNum = crystalHit.fillNum;
        crystalhit.caloNum = crystalHit.caloNum;
        crystalhit.islandNum = crystalHit.islandNum;
        crystalhit.xtalNum = crystalHit.xtalNum;
        crystalhit.time = crystalHit.time;
        crystalhit.energy = crystalHit.energy *
                            gainCorrection[crystalHit.xtalNum] *
                            sourceMonitorCorrection;

        crystalhit_collection.push_back(crystalhit);

      }  // end loop over the crystalhits

      gm2calo::MatrixCrystalHitArtRecord matrix_crystalhit(
          matrixCrystalHit.fillNum, matrixCrystalHit.caloNum,
          matrixCrystalHit.islandNum, crystalhit_collection);

      // fill in MatrixCrystalHitArtRecordCollection
      matrix_crystalhit_collection.push_back(matrix_crystalhit);

    }  // end loop over the crystalhit matrices

    gm2calo::CaloCrystalHitArtRecord calo_crystalhit(
        caloCrystalHit.fillNum, caloCrystalHit.caloNum,
        matrix_crystalhit_collection);

    // fill in CaloCrystalHitArtRecordCollection
    calo_crystalhit_collection->emplace_back(calo_crystalhit);

  }  // end loop over the calos

  // store the collection of crystal hits to the event
  event.put(
      std::move(calo_crystalhit_collection),
      correctorInstanceLabel_);  // putting events to CaloCrystalHitArtRecord.hh

  std::cout << "Exit gm2calo::PerFillLaserGainCorrector::produce" << std::endl;
}

DEFINE_ART_MODULE(gm2calo::PerFillLaserGainCorrector)
