// Creates and makes available TemplateFitter objects and template TSplines
// This allows us to only create the templates once as needed, regardless of how
// many configured template fitter modules we have
// 
// fcl parameters:
// "templateSamples": <how many points at which to sample template, default 10k>
// "nIterations": <how many iterations fitter tries before giving up, defaults 200>
// "isSimuation": <whether to use simulation template>
// "templateSet": <which set of beam/laser templates to use -- valid options (as of Jan 2019) are Run1 or Run2>
// "templatePath1": <path to laser template files, e.g. ~/calo{calo}seg{seg}Template.root"
// "templatePath2": <same as above, but for positron templates>
// 
// Aaron Fienberg
// January 2017

#ifndef TEMPLATEFITTERHOLDERSERVICE
#define TEMPLATEFITTERHOLDERSERVICE

#include "fhiclcpp/ParameterSet.h"
#include "art/Framework/Services/Registry/ActivityRegistry.h"
#include "messagefacility/MessageLogger/MessageLogger.h"
#include "art/Framework/Services/Registry/ServiceMacros.h"

#include "template_fitter/src/TemplateFitter.hh"
#include "TFile.h"

#include <map>

namespace gm2calo {

struct CaloFittersConfiguration {
  unsigned int templateSamples;
  unsigned int nIterations;
  bool storeSplines;
  bool isSimulation;
  bool prependGm2CaloToPath;
  std::string templateSet;
  std::string templatePattern1;
  std::string templatePattern2;
  std::string laserTemplatePattern;
  std::string positronTemplatePattern;
  bool useCaloTemplates;
  bool useNearlineAverageTemplates;
};

// the set of template fitters for a single calo
// separating this way makes parallelization by calo easier
// also holds TSpline3 objects describing templates
class CaloFitters {
 public:
  CaloFitters(int caloNum,
              const std::shared_ptr<const CaloFittersConfiguration> &confIn)
      : caloNum_(caloNum), conf_(confIn) {}

  // creates fitter if it doesn't already exist
  TemplateFitter &GetFitter(int segmentNum, bool secondary);

  //gets splines from file and fills the fitters
  TemplateFitter &GetAllFitters(bool secondary, int caloNum);

  // get spline from spline map
  // creates spline if it doesn't already exist
  // throws exception if storeSplines_ was configured to false
  std::shared_ptr<const TSpline3> GetSpline(int segmentNum, bool secondary);
  std::shared_ptr<const TSpline3> GetSplineCalo(TFile *templateFile, int segmentNum, bool secondary);

  // clear all the held templates
  void Clear() {
    fitterMap1_.clear();
    fitterMap2_.clear();
    splineMap1_.clear();
    splineMap2_.clear();
  }

 private:
  std::shared_ptr<const TSpline3> 
  CreateSplineFromFile(int segmentNum, bool secondary);

  std::shared_ptr<const TSpline3> 
  CreateSplineFromCaloFile(TFile *templateFile, int segmentNum, bool secondary);

  std::string GetFilePath(int segmentNum, bool secondary);
  std::string GetFilePathCalos(int caloNum, bool secondary);

  // does nothing if the pattern to replace isn't found
  static void PathReplace(std::string &str, const std::string &pattern,
                          int value);

  int caloNum_;

  // maps segment num to a template fitter
  std::map<int, TemplateFitter> fitterMap1_;
  std::map<int, TemplateFitter> fitterMap2_;

  // maps segment num to spline used in a template fitter,
  // but only if storeSplines is configure to true
  std::map<int, std::shared_ptr<const TSpline3>> splineMap1_;
  std::map<int, std::shared_ptr<const TSpline3>> splineMap2_;

  std::shared_ptr<const CaloFittersConfiguration> conf_;
};

class TemplateFitterHolder {
 public:
  TemplateFitterHolder(fhicl::ParameterSet const &, art::ActivityRegistry &);

  // create the caloFitters object for the specified calo
  // if it already exists, this does nothing
  // do not use this from multiple threads
  void CreateCaloFitters(int caloNum);

  // get calo fitter for specified calo
  // if it doesn't exist, this will throw an exception
  // should be ok from multiple threads that all have different calo numbers
  CaloFitters &GetCaloFitters(int caloNum) {
    return caloFittersMap_.at(caloNum);
  }

  void ClearAll() { caloFittersMap_.clear(); }

 private:
  // maps calo num to calo fitters
  std::map<int, CaloFitters> caloFittersMap_;
  std::shared_ptr<const CaloFittersConfiguration> conf_;
};

}  // namespace

using gm2calo::TemplateFitterHolder;
DECLARE_ART_SERVICE(TemplateFitterHolder, LEGACY)

#endif
