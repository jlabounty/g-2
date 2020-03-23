////////////////////////////////////////////////////////////////////////
// Class:       CaloFarlineHistograms
// Plugin Type: analyzer (art v2_03_00)
// File:        CaloFarlineHistograms_module.cc
//
// Calo oriented histograms to be generated after every run
//
// Generated at Mon Mar 27 16:42:59 2017 by Aaron Fienberg using cetskelgen
// from cetlib version v1_19_01.
// 
// Modified to rip out the GPU information from the nearline code on 8/20/18 by Josh LaBounty
//    so that the script could be run on production data.
////////////////////////////////////////////////////////////////////////

#include "art/Framework/Core/EDAnalyzer.h"
#include "art/Framework/Core/ModuleMacros.h"
#include "art/Framework/Principal/Event.h"
#include "art/Framework/Principal/Handle.h"
#include "art/Framework/Principal/Run.h"
#include "art/Framework/Principal/SubRun.h"
#include "canvas/Utilities/InputTag.h"
#include "fhiclcpp/ParameterSet.h"
#include "messagefacility/MessageLogger/MessageLogger.h"

#include "art/Framework/Services/Optional/TFileService.h"
#include "art/Framework/Services/Registry/ServiceHandle.h"

// Database service
#include "gm2util/database/Database_service.hh"

#include "gm2dataproducts/daq/MidasEventHeaderArtRecord.hh"
#include "gm2dataproducts/calo/IslandArtRecord.hh"
#include "gm2dataproducts/calo/CrystalHitArtRecord.hh"
#include "gm2dataproducts/calo/ClusterArtRecord.hh"
#include "gm2dataproducts/calo/GpuCTagArtRecord.hh"
#include "gm2dataproducts/daq/CCCArtRecord.hh"
#include "gm2dataproducts/aux/IBMSBeamProfileArtRecord.hh"

#include "gm2calo/util/CaloForEach.hh"
#include "gm2aux/T0/util/T0Helpers.hh"

#include "TH1.h"
#include "TH2.h"
#include "TTree.h"

namespace gm2calo {
	class CaloFarlineHistograms;
}

class gm2calo::CaloFarlineHistograms : public art::EDAnalyzer {
	public:
		explicit CaloFarlineHistograms(fhicl::ParameterSet const &p);
		// The compiler-generated destructor is fine for non-base
		// classes without bare pointers or other resource use.

		// Plugins should not be copied or assigned.
		CaloFarlineHistograms(CaloFarlineHistograms const &) = delete;
		CaloFarlineHistograms(CaloFarlineHistograms &&) = delete;
		CaloFarlineHistograms &operator=(CaloFarlineHistograms const &) = delete;
		CaloFarlineHistograms &operator=(CaloFarlineHistograms &&) = delete;

		void endJob() override;
		// Required functions.
		void analyze(art::Event const &e) override;

	private:
		// TTrees
		TTree *eventTree_;

		// mainly for the eventTree
		int runNum_;
		int subRunNum_;
		int eventNum_;
		int firstEvent_;
		int lastEvent_;
		int midasSerialNum_;
		double clockCounter_;
		int trigNum_;
		int bunchNum_;
		unsigned int runStartUnixTimeSeconds_;

		// T0
		double t0Int_[3];

		// IBMS
		std::vector<double> ibms1xMean_;   
		std::vector<double> ibms1yMean_;   
		std::vector<double> ibms2xMean_;   
		std::vector<double> ibms2yMean_;   
		std::vector<double> ibms1xTotalIntegral_;   
		std::vector<double> ibms1yTotalIntegral_;   
		std::vector<double> ibms2xTotalIntegral_;   
		std::vector<double> ibms2yTotalIntegral_;   

		// Calo
		int totalCaloIslands_;
		int ctag_;
		double ctagCorrectionFactor_;
		std::vector<int> caloNum_;
		std::vector<double> energy_;
		std::vector<double> time_;
		std::vector<double> x_;
		std::vector<double> y_;

		int nCalos_;
		int nXtals_;
		double positionThreshold_;
		double ctagTimeCut_;
		double ctagECutLow_;
		double ctagECutHigh_;
		double eHistMax_;
		double hitThreshold_;
		double nTimeBin_;

		bool useDatabase_;
		bool excludeLaser_;

		std::vector< int > excludeRuns_;

		std::string unpackerModuleLabel_;
		std::string unpackerInstanceLabel_;
		std::string t0IntegralModuleLabel_;    
		std::string t0IntegralInstanceLabel_;    
		std::string beamModuleLabel_;
		std::string beamInstanceLabel_;
		std::string xtalhitModuleLabel_;
		std::string xtalhitInstanceLabel_;
		std::string clusterModuleLabel_;
		std::string clusterInstanceLabel_;
		std::string fc7ModuleLabel_;
		std::string fc7InstanceLabel_;

		// histograms
		TH1D *allEnergies_;
		TH1D *allWiggle_;
		TH1D *allTimes_;
		TH1D *gpuCTag_;
		TH1D *farlineCTag_;
		TH1D *allProcessedEventHist_;

		std::vector<TH1D *> caloEnergies_;
		std::vector<TH1D *> caloWiggles_;
		std::vector<TH1D *> caloTimes_;
		std::vector<TH2D *> hitPositions_;
		std::vector<TH2D *> nXtalHits_;
		std::vector<std::vector<TH1D *>> xtalEnergies_;
		std::vector<std::vector<TH1D *>> timeCutCaloEnergies_;
		std::vector<std::vector<TH2D *>> energyCutCaloEnergies_;
		std::vector<TH1D *> laserSyncEnergies_;
};

gm2calo::CaloFarlineHistograms::CaloFarlineHistograms(
		fhicl::ParameterSet const &p)
	: EDAnalyzer(p),
	runNum_(-1),
	subRunNum_(-1),
	eventNum_(-1),
	firstEvent_(-1),
	lastEvent_(-1),
	midasSerialNum_(-1),
	clockCounter_(-1),
	trigNum_(-1),
	bunchNum_(-1),
	t0Int_(),
	totalCaloIslands_(0),
	ctag_(-1),
	ctagCorrectionFactor_(p.get<double>("ctagCorrectionFactor",1)),
	nCalos_(p.get<int>("nCalos", 24)),
	nXtals_(p.get<int>("nXtals", 54)),
	positionThreshold_(p.get<double>("positionThreshold", 1800)),
	ctagTimeCut_(p.get<double>("ctagTimeCut", 50000)),
	ctagECutLow_(p.get<double>("ctagEnergyCutLow", 1800)),
	ctagECutHigh_(p.get<double>("ctagEnergyCutHigh", 9300)),
	eHistMax_(p.get<double>("eHistMax", 4000)),
	hitThreshold_(p.get<double>("hitThreshold", 150)),
	nTimeBin_(p.get<double>("nTimeBin", 4700)),
	useDatabase_(p.get<bool>("useDatabase", false)),
	excludeLaser_(p.get<bool>("excludeLaser", false)),
	excludeRuns_(p.get<std::vector<int>>("excludeRuns", {0,0})),
	unpackerModuleLabel_(p.get<std::string>("unpackerModuleLabel", "islandUnpacker")),
	unpackerInstanceLabel_(p.get<std::string>("unpackerInstanceLabel", "unpacker")),
	t0IntegralModuleLabel_(p.get<std::string>("t0IntegralModuleLabel", "t0PulseProcessor")),
	t0IntegralInstanceLabel_(p.get<std::string>("t0IntegralInstanceLabel", "")),
	beamModuleLabel_(p.get<std::string>("beamModuleLabel","ibmsProcessor")),     
	beamInstanceLabel_(p.get<std::string>("beamInstanceLabel","ibmsProcessor")),
	xtalhitModuleLabel_(p.get<std::string>("xtalhitModuleLabel", "energyCalibratorDAQ")),
	xtalhitInstanceLabel_(p.get<std::string>("xtalhitInstanceLabel", "calibrator")),
	clusterModuleLabel_(p.get<std::string>("clusterModuleLabel", "hitClusterDAQ")),
	clusterInstanceLabel_(p.get<std::string>("clusterInstanceLabel", "cluster")) ,
	fc7ModuleLabel_(p.get<std::string>("fc7ModuleLabel", "cccUnpacker")),
	fc7InstanceLabel_(p.get<std::string>("fc7InstanceLabel", "unpacker")) {
		art::TFileDirectory allCaloDir = *art::ServiceHandle<art::TFileService>();

		// TTrees
		eventTree_ = allCaloDir.make<TTree>("eventTree", "eventTree");
		eventTree_->Branch("runNum", &runNum_, "runNum/i");
		eventTree_->Branch("subRunNum", &subRunNum_, "subRunNum/i");
		eventTree_->Branch("eventNum", &eventNum_, "eventNum/i");
		eventTree_->Branch("midasSerialNum", &midasSerialNum_, "midasSerialNum/i");
		eventTree_->Branch("clockCounter", &clockCounter_, "clockCounter/D");
		eventTree_->Branch("trigNum", &trigNum_, "trigNum/i");
		eventTree_->Branch("bunchNum", &bunchNum_, "bunchNum/i");
		eventTree_->Branch("runStartUnixTimeSeconds", &runStartUnixTimeSeconds_, "runStartUnixTimeSeconds/i");
		eventTree_->Branch("ctag", &ctag_, "ctag/i");
		eventTree_->Branch("caloNum", &caloNum_);        
		eventTree_->Branch("energy", &energy_);        
		eventTree_->Branch("time", &time_);        
		eventTree_->Branch("x", &x_);        
		eventTree_->Branch("y", &y_);        

		// THists
		allEnergies_ = allCaloDir.make<TH1D>(
				"allCaloEnergies", "all energies; energy [p.e.]; N;", 250, 0, eHistMax_);
		allWiggle_ = allCaloDir.make<TH1D>(
				"allCaloWiggle", "T Method, all calos; time [clock ticks]; N;", nTimeBin_, 0,
				560000);
		allTimes_ = allCaloDir.make<TH1D>(
				"allCaloTimes", "hit times, all calos; time [clock ticks]; N;", nTimeBin_, 0,
				560000);
		farlineCTag_ = allCaloDir.make<TH1D>(
				"farlineCTag", "farlineCTag; calo num; N", nCalos_, 1, nCalos_ + 1);
		allProcessedEventHist_ = allCaloDir.make<TH1D>(
				"allProcessedEventHist", "All Processed Events; Event; N", 2, 1, 2);

		caloEnergies_.resize(nCalos_);
		caloWiggles_.resize(nCalos_);
		caloTimes_.resize(nCalos_);
		hitPositions_.resize(nCalos_);
		xtalEnergies_.resize(nCalos_);
		nXtalHits_.resize(nCalos_);
		laserSyncEnergies_.resize(nCalos_);
		timeCutCaloEnergies_.resize(nCalos_);
		energyCutCaloEnergies_.resize(nCalos_);
		for (int iCalo = 0; iCalo < nCalos_; ++iCalo) {
			auto thisCaloDir = allCaloDir.mkdir("calo" + std::to_string(iCalo + 1));
			caloEnergies_[iCalo] = thisCaloDir.make<TH1D>(
					"energy", Form("calo %i energies; energy [p.e.]; N", iCalo + 1), 250, 0,
					eHistMax_);

			caloWiggles_[iCalo] = thisCaloDir.make<TH1D>(
					"wiggle", Form("calo %i T Method; time; N", iCalo + 1), nTimeBin_, 0,
					560000);
			caloTimes_[iCalo] = thisCaloDir.make<TH1D>(
					"times", Form("calo %i hit times; time; N", iCalo + 1), nTimeBin_, 0,
					560000);

			hitPositions_[iCalo] = thisCaloDir.make<TH2D>(
					"hitPositions",
					Form("calo %i hit positions;column num; row num;", iCalo + 1), 900, 0,
					9, 600, 0, 6);

			nXtalHits_[iCalo] = thisCaloDir.make<TH2D>(
					"nXtalHits",
					Form("calo %i n xtal hits;column num; row num;", iCalo + 1), 9, 0, 9, 6,
					0, 6);

			laserSyncEnergies_[iCalo] = thisCaloDir.make<TH1D>(
					"laserSyncEnergies", Form("Calo %i Energies; Energy [MeV]; Counts", iCalo + 1), 10000, 50000,
					150000);

			xtalEnergies_[iCalo].resize(nXtals_);
			for (int iXtal = 0; iXtal < nXtals_; ++iXtal) {
				xtalEnergies_[iCalo][iXtal] = thisCaloDir.make<TH1D>(
						Form("xtal%iEnergy", iXtal),
						Form("Calo %i, Crystal %i energy; ADC Counts; N", iCalo + 1, iXtal), 600, 0, 6000);
			}

			timeCutCaloEnergies_[iCalo].resize(16);
			for (int iXtal = 0; iXtal < 16; ++iXtal) {
				timeCutCaloEnergies_[iCalo][iXtal] = thisCaloDir.make<TH1D>(
						Form("calo%iTimeCut%iEnergy", iCalo + 1, iXtal),
						Form("Calo %i, Time Cut %i Energy; Energy [MeV]; Counts", iCalo + 1, iXtal), 600, 0, 6000);
			}

			energyCutCaloEnergies_[iCalo].resize(8);
			for (int iXtal = 0; iXtal < 8; ++iXtal) {
				energyCutCaloEnergies_[iCalo][iXtal] = thisCaloDir.make<TH2D>(
						Form("calo%iEnergyCut%iEnergy", iCalo + 1, iXtal),
						Form("Calo %i, Energy Cut %i Energy; x [xtals]; y [xtals]", iCalo + 1, iXtal), 90, 0, 9, 60, 0, 6);
			}

		}
	}

void gm2calo::CaloFarlineHistograms::analyze(art::Event const &e) {

	// reset ctag each fill
	ctag_ = 0;

	// reset cluster vectors each fill
	caloNum_.clear();
	energy_.clear();
	time_.clear();
	x_.clear();
	y_.clear();

	// get event info
	runNum_ = e.run();
	subRunNum_ = e.subRun();
	eventNum_ = e.event();
	lastEvent_ = e.event();

	bool skipEvent = false;
	for(unsigned int i = 0; i < excludeRuns_.size()/2; i++)
	{
		if(runNum_ == excludeRuns_[i*2] && subRunNum_ == int(excludeRuns_[i*2+1])) skipEvent = true;
	}
	if(skipEvent) return;

	if(firstEvent_ == -1)
	{
		firstEvent_ = e.event();
	}

	if(!skipEvent)
	{

		//Keeps a count of all of the events processed by this module. In histogram to be easily written to file
		//      (and will be preserved even if TTree is removed to save space)
		allProcessedEventHist_->Fill(1);

		// get sequence and trigger indices from fc7
		const auto &encodercol = *e.getValidHandle<gm2ccc::EncoderFC7ArtRecordCollection>(
				{fc7ModuleLabel_, fc7InstanceLabel_});

		bunchNum_ = encodercol.size() ? encodercol.front().sequenceIndex : -1;

		// get time stamp from midas event header
		art::Handle<gm2midastoart::MidasEventHeaderArtRecordCollection > midasEventHeaderHandle;
		e.getByLabel("MidasBankInput", "", midasEventHeaderHandle);
		const auto & midasEventHeaderCollection = *midasEventHeaderHandle;

		if( midasEventHeaderCollection.size() == 0 ) {
			throw cet::exception("getMidasEventHeader") << "Empty MIDAS event header collection\n";
		}

		else if( midasEventHeaderCollection.size() > 1 ) {
			throw cet::exception("getMidasEventHeader") << "> 1 MIDAS event headers in event, something has gone wrong\n";
		}

		else {  
			for (const auto &rec :  midasEventHeaderCollection){
				runStartUnixTimeSeconds_ = rec.timeStamp;
				midasSerialNum_ = rec.eventNumber;
			}
		}

		// T0 based information
		// 0 is tube A, 1 is tube B, 2 is sipm
		for(int i=0;i<3;i++){
			if (auto beamOpt = gm2aux::getLargestT0PulseOpt(e,
						{t0IntegralModuleLabel_, t0IntegralInstanceLabel_},i))
			{
				t0Int_[i] += beamOpt->integral;
			} else {
				t0Int_[i] += 0;	
			} 
		} 

		// IBMS based information
		// get processed ibms info
		const auto &ibmsBeamCol =
			*e.getValidHandle<gm2aux::IBMSBeamProfileArtRecordCollection>(
					{beamModuleLabel_, beamInstanceLabel_});

		for(auto &ibms : ibmsBeamCol){
			if(ibms.ibmsNum==1&&ibms.profile=="x"){
				ibms1xMean_.push_back(ibms.meanPosition);
				ibms1xTotalIntegral_.push_back(ibms.totalIntegral);
			}

			if(ibms.ibmsNum==1&&ibms.profile=="y"){
				ibms1yMean_.push_back(ibms.meanPosition);
				ibms1yTotalIntegral_.push_back(ibms.totalIntegral);
			}

			if(ibms.ibmsNum==2&&ibms.profile=="x"){
				ibms2xMean_.push_back(ibms.meanPosition);
				ibms2xTotalIntegral_.push_back(ibms.totalIntegral);
			}

			if(ibms.ibmsNum==2&&ibms.profile=="y"){
				ibms2yMean_.push_back(ibms.meanPosition);
				ibms2yTotalIntegral_.push_back(ibms.totalIntegral);
			}
		} 

		// Calo island based plots

		const auto& caloIslandData =
			*e.getValidHandle<CaloIslandViewArtRecordCollection>(
					{unpackerModuleLabel_, unpackerInstanceLabel_});

		for (auto& caloIsland : caloIslandData) {
			if (caloIsland.caloNum > 24) {
				mf::LogInfo("PedestalOffsetCorrection") << "Skip non-calo crates!";
				continue;
			}
			totalCaloIslands_ += caloIsland.matrixIslandViews.size();   
		}


		// cluster based plots
		const auto &clusterCol = *e.getValidHandle<ClusterArtRecordCollection>(
				{clusterModuleLabel_, clusterInstanceLabel_});

		if (clusterCol.size() && clusterCol[0].crystalHits.size()){
			trigNum_ = clusterCol[0].crystalHits[0]->amcHeader->triggerNum;
			clockCounter_ = clusterCol[0].crystalHits[0]->amcHeader->clockCounter*25e-9;
		}

		for (const auto& cluster : clusterCol) {
			int caloIndex = cluster.caloNum - 1;
			if (caloIndex > nCalos_) {
				throw cet::exception("CaloFarlineHistograms")
					<< "Found cluster with calo num " << cluster.caloNum
					<< ", but n calos set to " << nCalos_ << "!\n";
			} else if (caloIndex < 0) {
				throw cet::exception("CaloFarlineHistograms")
					<< "Found cluster with calo num " << cluster.caloNum << "!\n";
			}

			caloNum_.push_back(cluster.caloNum);
			energy_.push_back(cluster.energy);
			time_.push_back(cluster.time);
			x_.push_back(cluster.x);
			y_.push_back(cluster.y);

			allTimes_->Fill(cluster.time);
			caloTimes_[caloIndex]->Fill(cluster.time);

			allEnergies_->Fill(cluster.energy);
			caloEnergies_[caloIndex]->Fill(cluster.energy);

			if (cluster.energy > ctagECutLow_ && cluster.energy < ctagECutHigh_) {
				allWiggle_->Fill(cluster.time);
				caloWiggles_[caloIndex]->Fill(cluster.time);
				if(cluster.time > ctagTimeCut_){
					farlineCTag_->Fill(caloIndex + 1.5);
					ctag_++;	    
				}
			}

			if (cluster.energy > positionThreshold_) {
				hitPositions_[caloIndex]->Fill(cluster.x, cluster.y);
			}


			if (cluster.energy > 40000 && cluster.time < 0 )
			{
				laserSyncEnergies_[caloIndex]->Fill(cluster.energy);
			}

			//fill the calo energy breakdown histograms based on the time bin they fall into
			double tStart = 0; 	//us
			double tEnd = 700; 	//us
			double tDiv = 43.7;	//us
			int nDivs = int( std::ceil( (tEnd - tStart) / tDiv ) );

			for(int div = 0; div < nDivs; div++)
			{
				double ti = (tDiv * div) * 1000 / 1.25; 	//ct
				double tf = (tDiv * (div+1)) * 1000 / 1.25;	//ct

				if(cluster.time > ti && cluster.time < tf)
				{
					timeCutCaloEnergies_[caloIndex][div]->Fill(cluster.energy);
				}
			}

			//fill the calo energy maps based on the energy cuts
			double minEnergy = 0; 		//MeV
			double maxEnergy = 3000; 	//MeV
			nDivs = 8; 			//how many divisions should be break this into
			double Ebin = (maxEnergy - minEnergy) / nDivs;
			
			for(int div = 0; div < nDivs; div++)
			{
				double Ei = (Ebin * div);
				double Ef = (Ebin * (div+1));

				if(cluster.energy > Ei && cluster.energy < Ef)
				{
					energyCutCaloEnergies_[caloIndex][div]->Fill(cluster.x, cluster.y);
				}
			}


		}

		// xtal hit based plots
		const auto &xtalHitCol = *e.getValidHandle<CrystalHitArtRecordCollection>(
				{xtalhitModuleLabel_, xtalhitInstanceLabel_});

		for (const auto& xtalhit : xtalHitCol) {
			int caloIndex = xtalhit.caloNum - 1;
			if (caloIndex > nCalos_) {
				throw cet::exception("CaloFarlineHistograms")
					<< "Found xtal hit with calo num " << xtalhit.caloNum
					<< ", but n calos set to " << nCalos_ << "!\n";
			}

			if (xtalhit.energy > hitThreshold_) {
				nXtalHits_[caloIndex]->Fill(8.5 - xtalhit.xtalNum % 9,
						0.5 + xtalhit.xtalNum / 9);
			}

			if (xtalhit.xtalNum > nXtals_) {
				throw cet::exception("CaloFarlineHistograms")
					<< "Found xtal hit with xtal num " << xtalhit.xtalNum
					<< ", but n xtals set to " << nXtals_ << "!\n";
			}

			if(excludeLaser_) { 
				if(xtalhit.time > ctagTimeCut_) {
					xtalEnergies_[caloIndex][xtalhit.xtalNum]->Fill(xtalhit.energy);
				}
			}
			else { xtalEnergies_[caloIndex][xtalhit.xtalNum]->Fill(xtalhit.energy);
			}

		}


		// fill in the eventTree
		eventTree_->Fill();
	}

}

void gm2calo::CaloFarlineHistograms::endJob() {
	if (useDatabase_) {
		art::ServiceHandle<gm2util::Database> databaseHandle;

		databaseHandle->checkDate();

		int nctag = farlineCTag_->GetEntries();

		double ibms1xCentroid=-1;
		double ibms1yCentroid=-1;
		double ibms2xCentroid=-1;
		double ibms2yCentroid=-1;

		if(ibms1xMean_.size()>0) 
			ibms1xCentroid = std::accumulate( ibms1xMean_.begin(),
					ibms1xMean_.end(), 0.0)/ibms1xMean_.size(); 
		if(ibms1xMean_.size()>0) 
			ibms1yCentroid = std::accumulate( ibms1yMean_.begin(),
					ibms1yMean_.end(), 0.0)/ibms1yMean_.size(); 
		if(ibms1xMean_.size()>0) 
			ibms2xCentroid = std::accumulate( ibms2xMean_.begin(),
					ibms2xMean_.end(), 0.0)/ibms2xMean_.size(); 
		if(ibms1xMean_.size()>0) 
			ibms2yCentroid = std::accumulate( ibms2yMean_.begin(),
					ibms2yMean_.end(), 0.0)/ibms2yMean_.size(); 

		double ibms1xIntegral = std::accumulate(ibms1xTotalIntegral_.begin(),
				ibms1xTotalIntegral_.end(), 0.0);
		double ibms1yIntegral = std::accumulate(ibms1yTotalIntegral_.begin(),
				ibms1yTotalIntegral_.end(), 0.0);
		double ibms2xIntegral = std::accumulate(ibms2xTotalIntegral_.begin(),
				ibms2xTotalIntegral_.end(), 0.0);
		double ibms2yIntegral = std::accumulate(ibms2yTotalIntegral_.begin(),
				ibms2yTotalIntegral_.end(), 0.0);

		std::string query = "UPDATE farline_processing";
		query += " SET farline_ctag = " + std::to_string(nctag);
		query += ", ctag_correction_factor = " + std::to_string(ctagCorrectionFactor_);
		query += ", correctedfordrift = true";
		query += ", total_calo_islands = " + std::to_string(totalCaloIslands_);
		query += ", start_event_number = " + std::to_string(firstEvent_);
		query += ", end_event_number = " + std::to_string(lastEvent_);
		query += ", ibms1x_centroid = " + std::to_string(ibms1xCentroid);
		query += ", ibms1y_centroid = " + std::to_string(ibms1yCentroid);
		query += ", ibms2x_centroid = " + std::to_string(ibms2xCentroid);
		query += ", ibms2y_centroid = " + std::to_string(ibms2yCentroid);
		query += ", ibms1x_total_integral = " + std::to_string(ibms1xIntegral);
		query += ", ibms1y_total_integral = " + std::to_string(ibms1yIntegral);
		query += ", ibms2x_total_integral = " + std::to_string(ibms2xIntegral);
		query += ", ibms2y_total_integral = " + std::to_string(ibms2yIntegral);
		query += ", t0_tubea_total_integral = " + std::to_string(t0Int_[0]);
		query += ", t0_tubeb_total_integral = " + std::to_string(t0Int_[1]);
		query += ", t0_sipm_total_integral = " + std::to_string(t0Int_[2]);
		query += " WHERE run_number = " + std::to_string(runNum_);
		query += " AND subrun_number = " + std::to_string(subRunNum_) + ";";

		//  Insert into database table
		databaseHandle->customQuery(query);
		std::cout << query << std::endl;
	}
}

using gm2calo::CaloFarlineHistograms;
DEFINE_ART_MODULE(CaloFarlineHistograms)
