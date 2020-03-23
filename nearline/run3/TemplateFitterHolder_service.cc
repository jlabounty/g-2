// TemplateFitterHolder implementation
//
// Aaron Fienberg
// January 2017

#include "TemplateFitterHolder_service.hh"

// artg4 includes
#include "artg4/util/util.hh"

// ROOT includes
#include "TFile.h"
#include "TSpline.h"
#include "TROOT.h"

#include <memory>

#include "tbb/parallel_for.h"

//time testing includes
#include <ctime>
#include <chrono>

namespace gm2calo {

TemplateFitter &CaloFitters::GetFitter(int segmentNum, bool secondary) {
  if (conf_->isSimulation || conf_->useNearlineAverageTemplates) {
    // since all simulation templates are the same, no need to create 54 copies
    segmentNum = 0;
  }

  auto &map = secondary ? fitterMap1_ : fitterMap2_;
  auto mapIter = map.find(segmentNum);

  if (mapIter == map.end()) {
    // fitter not found, we need to construct it
    auto &newFitter = map[segmentNum];

    std::shared_ptr<const TSpline3> tSpline;
    if (conf_->storeSplines) {
      tSpline = GetSpline(segmentNum, secondary);
    } else {
      tSpline = CreateSplineFromFile(segmentNum, secondary);
    }

    newFitter.setPrimaryTemplate(*tSpline);

    newFitter.setMaxIterations(conf_->nIterations);

    // Load the opposite template as the fitter's secondary.
    std::shared_ptr<const TSpline3> tSpline2;

    if (conf_->storeSplines) {
      tSpline2 = GetSpline(segmentNum, !secondary);
    } else {
      tSpline2 = CreateSplineFromFile(segmentNum, !secondary);
    }

    newFitter.setSecondaryTemplate(*tSpline2);

    return newFitter;

  } else {
    // fitter exists
    return mapIter->second;
  }
}


TemplateFitter &CaloFitters::GetAllFitters(bool secondary, int caloNum)
{
	auto &map = secondary ? fitterMap1_ : fitterMap2_;
	if(!(conf_->isSimulation))
	{
		//open the file based on calo number
		std::string fullPath =  GetFilePathCalos(caloNum, secondary);
		std::string fullPathSec =  GetFilePathCalos(caloNum, !secondary);

		std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();
		
		TFile templateFile(fullPath.c_str());
		TFile templateFileSec(fullPathSec.c_str());

		std::chrono::high_resolution_clock::time_point t3 = std::chrono::high_resolution_clock::now();
		std::chrono::duration<double, std::milli> time_span_2 = t3 - t2;
		std::cout << "         " << time_span_2.count() << " milliseconds to open the calo files (" << fullPath << " --- " << secondary << ")." << std::endl;

		if (templateFile.IsZombie()) 
		{
			throw cet::exception("TemplateFitterHolder") << "Failed to open "
									 << fullPath << "!\n";
		}
		//XXXXXXXXXXXXX

		for(unsigned int segmentNum = 0; segmentNum < 54; segmentNum++)
		{
			auto mapIter = map.find(segmentNum);
			if (mapIter == map.end()) 
			{
				// fitter not found, we need to construct it
				auto &newFitter = map[segmentNum];

				std::shared_ptr<const TSpline3> tSpline;
				if (conf_->storeSplines) 
				{
					tSpline = GetSplineCalo(&templateFile, segmentNum, secondary);
				} 
				else 
				{
					tSpline = CreateSplineFromCaloFile( &templateFile, segmentNum, secondary);
					//create the spline from the open file
				}

				newFitter.setPrimaryTemplate(*tSpline);
				newFitter.setMaxIterations(conf_->nIterations);

				// Load the opposite template as the fitter's secondary.
				std::shared_ptr<const TSpline3> tSpline2;

				if (conf_->storeSplines) 
				{
					tSpline2 = GetSplineCalo(&templateFileSec, segmentNum, !secondary);
				} 
				else 
				{
					tSpline2 = CreateSplineFromCaloFile( &templateFileSec, segmentNum, !secondary);
				}

				newFitter.setSecondaryTemplate(*tSpline2);

				//return newFitter;

			} 
			else 
			{
				// fitter exists
				//return mapIter->second;
			}

		}
	}
	
	auto mapIter = map.find(0);
	return mapIter->second;
}

std::shared_ptr<const TSpline3> CaloFitters::GetSpline(int segmentNum,
                                                       bool secondary) {
  if (!conf_->storeSplines) {
    throw cet::exception("TemplateFitterHolder")
        << "Tried to GetSpline(), but TemplateFitterHolder is configured not "
           "to store them! Set storeSplines : true in the fcl file.\n ";
  }

  if (conf_->isSimulation || conf_->useNearlineAverageTemplates) {
    segmentNum = 0;
  }

  auto &splineMap = secondary ? splineMap1_ : splineMap2_;
  auto splineIter = splineMap.find(segmentNum);
  if (splineIter == splineMap.end()) {
    return splineMap[segmentNum] = CreateSplineFromFile(segmentNum, secondary);
  } else {
    return splineIter->second;
  }
}


std::shared_ptr<const TSpline3> CaloFitters::GetSplineCalo(TFile *calofile, int segmentNum,
                                                       bool secondary) {
  if (!conf_->storeSplines) {
    throw cet::exception("TemplateFitterHolder")
        << "Tried to GetSpline(), but TemplateFitterHolder is configured not "
           "to store them! Set storeSplines : true in the fcl file.\n ";
  }

  if (conf_->isSimulation) {
    segmentNum = 0;
  }

  auto &splineMap = secondary ? splineMap1_ : splineMap2_;
  auto splineIter = splineMap.find(segmentNum);
  if (splineIter == splineMap.end()) {
    return splineMap[segmentNum] = CreateSplineFromCaloFile( calofile, segmentNum, secondary);
  } else {
    return splineIter->second;
  }
}

std::shared_ptr<const TSpline3> CaloFitters::CreateSplineFromFile(
    int segmentNum, bool secondary) {
  std::string fullPath;
  if (conf_->isSimulation) {
    fullPath = artg4::basePath("GM2CALO_DIR", "gm2calo") +
               "/runTimeFiles/fitTemplate.root";
  } else if (conf_->useNearlineAverageTemplates) {
    if(secondary) //load laser template
    {
	fullPath = artg4::basePath("GM2CALO_DIR", "gm2calo") + 
               "/runTimeFiles/fitTemplate_NearlineAverageLaser.root";
    }
    else //load positron template
    {
	fullPath = artg4::basePath("GM2CALO_DIR", "gm2calo") + 
               "/runTimeFiles/fitTemplate_NearlineAveragePositron.root";
    }
  } else {
    fullPath = GetFilePath(segmentNum, secondary);
  }


//  std::chrono::high_resolution_clock::time_point t0 = std::chrono::high_resolution_clock::now();
//  std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();

  TFile templateFile(fullPath.c_str());

//  std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();
  if (templateFile.IsZombie()) {
    throw cet::exception("TemplateFitterHolder") << "Failed to open "
                                                 << fullPath << "!\n";
  }

//  std::chrono::duration<double, std::milli> time_span = t2 - t1;
//  std::cout << "It took: " << time_span.count() << " milliseconds to open the file." << std::endl;
//  t2 = std::chrono::high_resolution_clock::now();

  std::shared_ptr<TSpline3> tSpline(
      (TSpline3 *)templateFile.Get("masterSpline"));
  if (!tSpline) {
    throw cet::exception("TemplateFitterHolder")
        << "Could not get masterSpline from " << fullPath << "!\n";
  }

//  std::chrono::high_resolution_clock::time_point t3 = std::chrono::high_resolution_clock::now();
//  std::chrono::duration<double, std::milli> time_span_2 = t3 - t2;
//  std::cout << "         " << time_span_2.count() << " milliseconds to get the spline." << std::endl;

  tSpline->ResetBit(kMustCleanup);

  return tSpline;
}


std::shared_ptr<const TSpline3> CaloFitters::CreateSplineFromCaloFile(
    TFile *templateFile, int segmentNum, bool secondary) {

  std::chrono::high_resolution_clock::time_point t0 = std::chrono::high_resolution_clock::now();

  if (templateFile->IsZombie()) {
    throw cet::exception("TemplateFitterHolder") << "Failed to open ";
  }

  std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();

  std::shared_ptr<TSpline3> tSpline(
      (TSpline3 *)templateFile->Get( ("masterSpline_xtal"+std::to_string(segmentNum)).c_str() ));
  if (!tSpline) {
    throw cet::exception("TemplateFitterHolder")
        << "Could not get masterSpline from " << "!\n";
  }

  std::chrono::high_resolution_clock::time_point t3 = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double, std::milli> time_span_2 = t3 - t2;
  std::cout << "         " << time_span_2.count() << " milliseconds to get the spline from the calo file." << secondary << std::endl;

  tSpline->ResetBit(kMustCleanup);

  return tSpline;
}

std::string CaloFitters::GetFilePath(int segmentNum, bool secondary) {
  std::string basePath = artg4::basePath("GM2CALO_DIR", "gm2calo");
  std::string fullPath = basePath + "/runTimeFiles";

  bool isUserPath = false;
  if (secondary) {
    if (conf_->templatePattern2 != "") {
      if (conf_->prependGm2CaloToPath) {
	fullPath += conf_->templatePattern2;
      } else {
	fullPath = conf_->templatePattern2;
      }
      isUserPath = true;

    } else if (conf_->laserTemplatePattern != "") {
      if (conf_->prependGm2CaloToPath) {
	fullPath += conf_->laserTemplatePattern;
      } else {
	fullPath = conf_->laserTemplatePattern;
      }
      isUserPath = true;

    } else if (conf_->templateSet != ""){//select given Run's laser templates
      fullPath += "/templates" + conf_->templateSet + "/standardLaserTemplates/calo" +
                  std::to_string(caloNum_) + "Templates" + "/template" +
                  std::to_string(segmentNum) + ".root";

    } else {
      // use default path for lasers -- Run 1
      fullPath += "/templatesRun1/standardLaserTemplates/calo" +
                  std::to_string(caloNum_) + "Templates" + "/template" +
                  std::to_string(segmentNum) + ".root";
    }
  } else {
    if (conf_->templatePattern1 != "") {
      if (conf_->prependGm2CaloToPath) {
	fullPath += conf_->templatePattern1;
      } else {
	fullPath = conf_->templatePattern1;
      }
      isUserPath = true;

    } else if (conf_->positronTemplatePattern != "") {
      if (conf_->prependGm2CaloToPath) {
	fullPath += conf_->positronTemplatePattern;
      } else {
	fullPath = conf_->positronTemplatePattern;
      }
      isUserPath = true;

    } else if (conf_->templateSet != ""){//select given Run's beam templates
      fullPath += "/templates" + conf_->templateSet + "/beamTemplates/calo" +
		  std::to_string(caloNum_) + "BeamTemplates" + "/template" +
		  std::to_string(segmentNum) + ".root";

    } else {  // use default for positrons -- Run1 templates
      fullPath += "/templatesRun1/beamTemplates/calo" +
                  std::to_string(caloNum_) + "BeamTemplates" + "/template" +
                  std::to_string(segmentNum) + ".root";
    }
  }

  if (isUserPath) {
    PathReplace(fullPath, "{calo}", caloNum_);
    PathReplace(fullPath, "{seg}", segmentNum);
  }
//  useful for checking that the correct templates are being grabbed
//  std::cout << "The path to templates is : " << fullPath << std::endl;
  return fullPath;
}


std::string CaloFitters::GetFilePathCalos(int caloNum, bool secondary) {
  std::string basePath = artg4::basePath("GM2CALO_DIR", "gm2calo");
  std::string fullPath = basePath + "/runTimeFiles";

  bool isUserPath = false;
  if (secondary) {
    if (conf_->templatePattern2 != "") {
      if (conf_->prependGm2CaloToPath) {
	fullPath += conf_->templatePattern2;
      } else {
	fullPath = conf_->templatePattern2;
      }
      isUserPath = true;

    } else if (conf_->laserTemplatePattern != "") {
      if (conf_->prependGm2CaloToPath) {
	fullPath += conf_->laserTemplatePattern;
      } else {
	fullPath = conf_->laserTemplatePattern;
      }
      isUserPath = true;
    } else if (conf_->templateSet != ""){//select given Run's laser templates
      fullPath += "/templates" + conf_->templateSet + "/standardLaserTemplatesByCalo/calotemplate" +
                  std::to_string(caloNum) + ".root";

    } else {
      // use default path for lasers
      fullPath += "/templatesRun2/standardLaserTemplatesByCalo/calotemplate" +
                  std::to_string(caloNum) + ".root";
    }
  } else {
    if (conf_->templatePattern1 != "") {
      if (conf_->prependGm2CaloToPath) {
	fullPath += conf_->templatePattern1;
      } else {
	fullPath = conf_->templatePattern1;
      }
      isUserPath = true;

    } else if (conf_->positronTemplatePattern != "") {
      if (conf_->prependGm2CaloToPath) {
	fullPath += conf_->positronTemplatePattern;
      } else {
	fullPath = conf_->positronTemplatePattern;
      }
      isUserPath = true;
    } else if (conf_->templateSet != ""){//select given Run's laser templates
      fullPath += "/templates" + conf_->templateSet + "/beamTemplatesByCalo/calotemplate" +
                  std::to_string(caloNum) + ".root";

    } else {  // use default for positrons
      fullPath += "/templatesRun2/beamTemplatesByCalo/calotemplate" +
                  std::to_string(caloNum) + ".root";
    }
  }

  if (isUserPath) {
    PathReplace(fullPath, "{calo}", caloNum_);
    PathReplace(fullPath, "{seg}", caloNum);
  }

  return fullPath;
}

void CaloFitters::PathReplace(std::string &str, const std::string &pattern,
                              int value) {
  auto pos = str.find(pattern);
  if (pos != std::string::npos) {
    auto valuestr = std::to_string(value);
    str.replace(pos, pattern.size(), valuestr);
  }
}

TemplateFitterHolder::TemplateFitterHolder(fhicl::ParameterSet const &p,
                                           art::ActivityRegistry &)
    : caloFittersMap_(),
      conf_(new CaloFittersConfiguration{
          p.get<unsigned int>("templateSamples", 10000),
          p.get<unsigned int>("nIterations", 200), 
	  p.get<bool>("storeSplines"),
          p.get<bool>("isSimulation", false),
	  p.get<bool>("prependGm2CaloToPath", true),
	  p.get<std::string>("templateSet","Run1"),
          p.get<std::string>("templatePattern1", ""),
          p.get<std::string>("templatePattern2", ""),
          p.get<std::string>("laserTemplatePath", ""),
          p.get<std::string>("positronTemplatePath", ""),
          p.get<bool>("useCaloTemplates", false),
          p.get<bool>("useNearlineAverageTemplates", false)}) {
  if (p.get<bool>("preloadAllFitters", false)) {
std::cout << "TEMPLATEFITTERHOLDER: Time Start " << std::time(nullptr) << std::endl;
    for (unsigned int i = 1; i <= 24; ++i) {
      CreateCaloFitters(i);
    }
    const bool useCaloTemplates = p.get<bool>("useCaloTemplates", false) ;
    tbb::parallel_for(size_t(1), size_t(25), [&](size_t caloNum) {
      auto &caloFitters = GetCaloFitters(caloNum);
	if( useCaloTemplates )
	{
	      caloFitters.GetAllFitters(true, caloNum);
	      //caloFitters.GetAllFitters(false, caloNum);
	}
	else
	{
	     for (unsigned int xtalNum = 0; xtalNum < 54; ++xtalNum) {
	        caloFitters.GetFitter(xtalNum, true);
	        caloFitters.GetFitter(xtalNum, false);
	      }
	}
    });
std::cout << "TEMPLATEFITTERHOLDER: Time End " << std::time(nullptr) << std::endl;
  }
}

void TemplateFitterHolder::CreateCaloFitters(int caloNum) {
  auto mapIter = caloFittersMap_.find(caloNum);
  if (mapIter == caloFittersMap_.end()) {
    // caloFitters for this calo doesn't exist, so we create it
    caloFittersMap_.emplace(caloNum, CaloFitters(caloNum, conf_));
  }
}
}

using gm2calo::TemplateFitterHolder;
DEFINE_ART_SERVICE(TemplateFitterHolder)
