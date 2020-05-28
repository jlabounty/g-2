#!/bin/env python

"""

  ConDBJsonFileWriter.py
	Script designed to convert fhicl files to json files.

  author: T. Walton (twalton@fnal.gov)

  July 2019

  updated by G. Lukicov (g.lukicov@ucl.ac.uk) 4 Sep 2019
  --added tracker alignment functionality 

  
  Oct 2019 - J. Hempstead (hempste2@uw.edu)
  Adding options for WFD5 pedestal constants

  Dec 2019 - J. Hempstead (hempste2@uw.edu)
  Adding options for RW calo timing and calibration constants

  Apr 2020 - J. Hempstead (hempste2@uw.edu)
  Adding options for channel status table

"""


import os, sys, math, subprocess, re
import numpy as np

from optparse import OptionParser

"""
helper classes
"""
_parser = OptionParser()



"""
script option parser
"""
def JsonParserHelpOpts() :
    _parser.add_option("--fcl", dest="fcl", default=None, type="string", help="The input FHiCL file to convert to json file. [Required]")
    _parser.add_option("--file", dest="file", default="filename", type="string", help="The based name of the output json file name.")
    _parser.add_option("--path", dest="path", default="outfilePath", type="string", help="The path of the output json files.")
    _parser.add_option("--scratch", dest="scratch", default=False, action="store_true", help="Write to /pnfs scratch area and overwrite path directory.")
    _parser.add_option("--iov", dest="iov", default=None, type="string", help="The interval of validity. [Required]")
    _parser.add_option("--ana", dest="ana", default=None, type="string", help="The type of analysis. [Required]")    


"""
make string
"""
def MakeString(lst) :
    lstring = ""
    for l in lst :
        lstring += "\"%s\"," % l
    return lstring[:-1]

"""
get the filename 
"""
def GetFilename(opts,identifier) :
    jsonFilename = opts["file"].replace(".json","")
    topDir       = opts["path"]

    if opts["scratch"] :
      subdir = ""
      iovs   = opts["iov"].split(":")
      for iov in iovs :
          subdir += iov.capitalize()

      user   = str(os.environ.get('USER'))
      topDir = "/pnfs/GM2/scratch/users/%s/JSONFiles/%s/ID%s" % (user,subdir,identifier)

    if not os.path.exists(topDir) : 
       os.makedirs(topDir)

    jsonFilename = "%s/%s%s.json" % (topDir,jsonFilename,identifier)
    return jsonFilename 


"""
create a json per IOV
"""
def CreateJsonFile(opts,run) :
    
    # chose identider based on iov type 
    if opts["iov"] == "run" :
      identifier   = int(run)
    elif opts["iov"] == "run_range" :
      identifier   = str(run[0])+"_"+str(run[1])
      
    jsonFilename = GetFilename(opts,identifier) 
    jsonFile     = open(jsonFilename,'w')
    jsonFile.write("{\n")
       
    #write to the json file based on the iov type 
    if opts["iov"] == "run" :
      jsonFile.write("\"interval_of_validity\" : { \"run\" : %s },\n\n" % run)
    elif opts["iov"] == "run_range" :
       jsonFile.write( " \"interval_of_validity\" : { \"run_start\" : "+str(run[0])+", \"run_end\" : "+str(run[1])+" },\n\n " )
    else :
      sys.exit("The input interval of validity is not implemented.  Please add your iov")

    return jsonFile

"""
create json file header
"""
def CreateJsonFileHeader(jsonFile,folderName,columnString,typeString) :
    jsonFile.write("\"%s\" : \n" % folderName)
    jsonFile.write("{\n")
    jsonFile.write("\t\"columns\" : [ %s ],\n" % columnString)
    jsonFile.write("\t\"types\" : [ %s ],\n" % typeString)


"""
write the json file constants
"""
def WriteJsonFileConstants(jsonFile,values,writeComma=True) :
    if not jsonFile.closed :

       for idx, value in enumerate(values) :
           svalue      = [str(i) for i in value]
           deliminator = "," if idx != len(values)-1 else " ]\n"
           if idx == 0 :
              jsonFile.write("\t\"values\" : [ [%s]%s\n" % (','.join(svalue),deliminator))   
           else :
              jsonFile.write("\t\t[%s]%s\n" % (','.join(svalue),deliminator)) 

       if writeComma :
          jsonFile.write("},\n\n")
       else :
          jsonFile.write("}\n\n")


"""
write the json file constants as an array
Input: 2D array 
"""
def WriteJsonFileConstants2DArray(jsonFile,values,writeComma=True) :
    if not jsonFile.closed :
       jsonFile.write(" \t\"values\" : [ ")
       #write a dimension of the array, with elements comma separated (repr)
       inner, outer, elements = np.shape(values) # return array shape 
       total_length = inner * outer
       i_length=0 # checking if reached the last dimension 
       for i_inner in range(inner):
          for i_outer in range(outer):
              i_length+=1 
              jsonFile.write( str(repr(values[i_inner][i_outer])))
              if (i_length != total_length):
                jsonFile.write(",\n") # write new line for all but last array

       # write the final closing bracket 
       jsonFile.write(" ]\n")
       
       if writeComma :
          jsonFile.write("},\n\n")
       else :
          jsonFile.write("}\n\n")
 
"""
closing the json file
"""
def CloseJsonFile(opts,jsonFile,folderStatusName,run) :
    if not jsonFile.closed :
       cstring = ""
       tstring = ""
       values  = None

       if opts["iov"] == "run" :
          cstring = "\"run\", \"status\""
          tstring = "\"int\", \"int\""
          values  = [ [run,1] ]
       elif  opts["iov"] == "run_range" :
          cstring = " \"run_start\", \"run_end\",  \"status\" "
          tstring = " \"int\", \"int\", \"bool\" "
          values  = [ [run[0], run[1], 1] ]
       else :
          sys.exit("The input interval of validity is not implemented.  Please added your iov")

       CreateJsonFileHeader(jsonFile,folderStatusName,cstring,tstring)
       WriteJsonFileConstants(jsonFile,values,False) 

       jsonFile.write("}\n")
       jsonFile.close()

"""
Tracker: read offsets from a FHICL file given the FHICLPatchName
Put 0s for station 0 
"""
def getOffsets(FHICL_file):

    #Defining tracker constants ##
    stations = ("12", "18") 
    moduleN = 8 # per station 
    FHICLPatchName = ["strawModuleRShift", "strawModuleHShift"] # radial and vertical offsets 
    FHICLServicePath = "services.Geometry.strawtracker." #full path of the tracking FHICL patch
    
    # return data structure offsets[station][globalDoF]
    # globalDoF : radial or vertical shift 
    offsets_array = [ [ [], [] ], [ [], [] ] ]
    
    # loop over stations and globalDoF 
    # to match the line are sore offsets in the array 
    for line in FHICL_file:
      for i_station in range(0, len(stations)):
        for i_global in range(0, len(FHICLPatchName)):
          offset_name = FHICLServicePath+FHICLPatchName[i_global]+stations[i_station]
          if re.match(offset_name, line):
              # for the matched line strip all but the real numbers 
              offsets=line
              offsets = offsets.replace(offset_name+": [", "") 
              offsets = offsets.replace("]", "") 
              offsets = [float(r) for r in offsets.split(',')]
              offsets_array[i_station][i_global]=offsets

    FHICL_file.close()

    # Put 0s for station 0 
    zeros = np.zeros(moduleN)
    offsets_array_corrected = [ [list(zeros), list(zeros)], [offsets_array[0][0], offsets_array[0][1]], [offsets_array[1][0], offsets_array[1][1]] ]
    return offsets_array_corrected 

"""
primary function to create json files
"""
def CreateJsonFiles(opts) :
    fclFile  = open(opts["fcl"],'r') 
    
    if opts["ana"] == "kicker" :
       folderStatusName = "kicker_dqc_status"
       foldername = "kicker_dqc"
       columns    = [ "kickerAmplitudeUpperBound", "kickerAmplitudeLowerBound", "kickerTimingUpperBound", "kickerTimingLowerBound", "kickerFWHMUpperBound", "kickerFWHMLowerBound", "zeroCrossingCut" ]
       types      = [ "real", "real", "real", "real", "real", "real", "int" ]

       cstring    = MakeString(columns)
       tstring    = MakeString(types)

       run        = None
       values     = None 
       jsonFile   = None

       # loop over file lines
       for fclLine in fclFile.readlines() :
           line   = fclLine.strip()

           # create a new file 
           if line.find("run") != -1 and line.find(":") != -1 :
              values   = [ [0.,0.,0.,0.,0.,0.,0.], [0.,0.,0.,0.,0.,0.,0.], [0.,0.,0.,0.,0.,0.,0.] ] 
              run      = line[:line.find(":")].replace("run","").strip() 
              jsonFile = CreateJsonFile(opts,run)
              CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)
           elif line.find("}") != -1 :
              if jsonFile != None :
                 WriteJsonFileConstants(jsonFile,values)
                 CloseJsonFile(opts,jsonFile,folderStatusName,run)
           else :
             key  = -1
             if line.find("Kicker1") != -1 :
                key = 0
             elif line.find("Kicker2") != -1 :
                key = 1
             elif line.find("Kicker3") != -1 :
                key = 2
             else :
                continue

             item = -1 
             if line[:line.find("Kicker")] in columns :
                item = columns.index(line[:line.find("Kicker")]) 
             else :
                continue

             if types[item] == "real" :
                values[key][item] = float(line[line.find(":")+1:])
             elif types[item] == "int" :
                values[key][item] = int(line[line.find(":")+1:])

    # if internal alignment FHICL file is passed write a JSON file with constants
    # as a column of 8 offsets; 6 channels: S0_rad, S0_ver S12_rad, S12_ver, S18_rad, S18_rad
    # the channels for S0 are filled with 0 from getOffsets function 
    # IoV is a run
    elif opts["ana"] == "tracker_align_internal_module" :
    
       folderStatusName = "tracker_align_internal_module_status"
       foldername = "tracker_align_internal_module"
       columns    = [ "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8" ]
       types      = [ "real", "real", "real", "real", "real", "real", "real", "real"] 

       cstring    = MakeString(columns)
       tstring    = MakeString(types)

       run        = None # run_start
       values     = None 
       jsonFile   = None

       # this returns a 2x2 array: values[station][DoF]
       values = getOffsets(fclFile)
       # re-open the file and get the run_start and run_end 
       fclFile  = open(opts["fcl"],'r') 
       lines=fclFile.readlines()
       run = [int(s) for s in lines[0].split() if s.isdigit()][0]  # run_start
       
       # write the header once 
       jsonFile = CreateJsonFile(opts,run)
       CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)
       # 2D array is being loped over its dimensions inside the function  
       WriteJsonFileConstants2DArray(jsonFile,values)
       # write the tail and close the file 
       CloseJsonFile(opts,jsonFile,folderStatusName,run)
       print "\n",opts["path"]+"/"+opts["file"]+str(run)+".json","was written\n"
       ###end of tracker_align_internal_module statement 

    # if external alignment FHICL file is passed write a JSON file with constants
    # as a column of 4 offsets; 3 channels: S0, S12, S18
    # the channels for S0 are filled with 0 from getOffsets function 
    # IoV is a run
    elif opts["ana"] == "tracker_align_external":
    
       folderStatusName = "tracker_align_external_status"
       foldername = "tracker_align_external"
       columns    = [ "radialShift", "verticalShift", "trackerXZAngle", "trackerYZAngle"]
       types      = [ "real", "real", "real", "real"] 

       cstring    = MakeString(columns)
       tstring    = MakeString(types)

       run        = None # run_start
       values     = [ [], [], [] ] 
       jsonFile   = None

       stations = ("0", "12", "18")   
       # return data structure offsets[station][globalDoF]
       # globalDoF : radial or vertical shift  

       # re-open the file and get the run_start and run_end 
       fclFile  = open(opts["fcl"],'r') 
       lines=fclFile.readlines()
       run = [int(s) for s in lines[0].split() if s.isdigit()][0]  # run_start
       
       # loop over stations and globalDoF 
       # to match the line are sore offsets in the array 
       fclFile  = open(opts["fcl"],'r')
       for line in fclFile:
         for i_station, station in enumerate(stations):
           for name in columns:
             offset_name = name+station
             if re.match(offset_name, line):
                 # for the matched line strip all but the real number 
                 offset=line
                 offset = float(offset.replace(offset_name+": ", ""))
                 values[i_station].append(offset)
                 
       # write the header once 
       jsonFile = CreateJsonFile(opts,run)
       CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)
       # 2D array is being loped over its dimensions inside the function  
       WriteJsonFileConstants(jsonFile,values)
       # write the tail and close the file 
       CloseJsonFile(opts,jsonFile,folderStatusName,run)
       print "\n",opts["path"]+"/"+opts["file"]+str(run)+".json","was written\n"
       ###end of tracker_align_external statement 

    elif opts["ana"] == "ifg" :
        
        folderStatusName = "infill_gain_withexpstdp_status"
        foldername = "infill_gain_withexpstdp"
        columns = ["calo", "xtal", "p0", "p1", "p2", "p3", "p4"]
        types = [ "int", "int", "real", "real", "real", "real", "real"]
      
        cstring = MakeString(columns)
        tstring = MakeString(types)

        run_range = [ None, None ]
        values    = [ [None, None, None, None, None, None, None] ]
        jsonFile  = None

        calo  = -1

        fclLines = fclFile.readlines()
        for fidx, fclLine in enumerate(fclLines) :
            line = fclLine.strip().lower()

            if line.find("ifgf_withstdp") != -1:
              if line.find("60h") != -1:
                run_range = [15921, 15991]
              elif line.find("9d") != -1:
                run_range = [16355, 16539]
              elif line.find("endgame") != -1:
                run_range = [16908, 17528]
              elif line.find("highkick") != -1:
                run_range = [16110, 16256]
              elif line.find("_lowkick") != -1:
                run_range = [16669, 16714]
              elif line.find("superlowkick") != -1:
                run_range = [16827, 16900]

              jsonFile = CreateJsonFile(opts,run_range)
              CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)

            elif line.find("calo") != -1 :
              start = line.find("calo") + 4
              end   = line.find(":")
              calo  = int(line[start:end])
            elif line.find("xtal") != -1 :
              start = line.find("xtal") + 4
              end   = line.find(":")
              xtal  = int(line[start:end])
              p0    = float(fclLines[fidx+1].strip().replace(",",""))
              p1    = float(fclLines[fidx+2].strip())
           
              value = [ calo, xtal, p0, p1, 0, 0, 0 ]

              if values[0][0] == None :
                 values.pop(0)

              values.append(value)

            if len(values) == 24*54 :
               WriteJsonFileConstants(jsonFile,values)
               CloseJsonFile(opts,jsonFile,folderStatusName,run_range)
 
               values *= 0
               values  = [ [None, None, None, None] ]

    elif opts["ana"] == "ifg2" :
        
        folderStatusName = "infill_gain_nostdp_status"
        foldername = "infill_gain_nostdp"
        columns = ["calo", "xtal", "p0", "p1", "p2", "p3", "p4"]
        types = [ "int", "int", "real", "real", "real", "real", "real"]
      
        cstring = MakeString(columns)
        tstring = MakeString(types)

        run_range = [ None, None ]
        values    = [ [None, None, None, None, None, None, None] ]
        jsonFile  = None

        calo  = -1

        fclLines = fclFile.readlines()
        for fidx, fclLine in enumerate(fclLines) :
            line = fclLine.strip().lower()

            if line.find("ifgc") != -1:
              if line.find("60h") != -1:
                run_range = [15921, 15991]
              elif line.find("9d") != -1:
                run_range = [16355, 16539]
              elif line.find("endgame") != -1:
                run_range = [16908, 17528]
              elif line.find("highkick") != -1:
                run_range = [16110, 16256]
              elif line.find("_lowkick") != -1:
                run_range = [16669, 16714]
              elif line.find("superlowkick") != -1:
                run_range = [16827, 16900]

              jsonFile = CreateJsonFile(opts,run_range)
              CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)

            elif line.find("calo") != -1 :
              start = line.find("calo") + 4
              end   = line.find(":")
              calo  = int(line[start:end])
            elif line.find("xtal") != -1 :
              start = line.find("xtal") + 4
              end   = line.find(":")
              xtal  = int(line[start:end])
              p0    = float(fclLines[fidx+1].strip().replace(",",""))
              p1    = float(fclLines[fidx+2].strip().replace(",",""))
              p2    = float(fclLines[fidx+3].strip())
           
              value = [ calo, xtal, p0, p1, p2, 0, 0 ]

              if values[0][0] == None :
                 values.pop(0)

              values.append(value)

            if len(values) == 24*54 :
               WriteJsonFileConstants(jsonFile,values)
               CloseJsonFile(opts,jsonFile,folderStatusName,run_range)
 
               values *= 0
               values  = [ [None, None, None, None] ]

    elif opts["ana"] == "pedestals" :

        folderStatusName = "pedestal_offsets_status"
        foldername = "pedestal_offsets"
        columns = ["calo", "xtal", "wfd5_evenodd_offset", "noiselevel"]
        types = [ "int", "int", "real", "real"]

        cstring = MakeString(columns)
        tstring = MakeString(types)

        run_range = [ 11169 , 14395 ]
        values    = [ [ None, None, None, None ] ]
        jsonFile = CreateJsonFile(opts,run_range)
        CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)

        calo  = -1
        xtal  = -1
        noise = -1
        offset = -1
        fclLines = fclFile.readlines()
        for fidx, fclLine in enumerate(fclLines) :
            line = fclLine.strip().lower()

            if line.find("calo") != -1 and line.find("calorimeter") == -1 : 
              start = line.find("calo") + 4
              end   = line.find(":")
              if line[end-1:end].isdigit() : 
                end += 1
              calo  = int(line[start:end-1])
            elif line.find("xtal") != -1 :
              start = line.find("xtal") + 4
              end   = line.find(":")
              if line[end-1:end].isdigit() :
                end += 1
              xtal  = int(line[start:end-1])
            elif line.find("noiselevel") != -1 :
              start = line.find(":") + 1
              end   = line.find("\n")
              noise = float(line[start:len(line)])
            elif line.find("pedestaloffset") != -1 : 
              start = line.find(":") + 1
              end   = line.find("\n")
              offset = float(line[start:len(line)])
              value = [ calo, xtal, offset, noise ]
              if values[0][0] == None :
                 values.pop(0)
              values.append(value)
            if len(values) == 24*54 :
              WriteJsonFileConstants(jsonFile,values)
              CloseJsonFile(opts,jsonFile,folderStatusName,run_range)
              values *= 0
              values  = [ [None, None, None, None] ]

    elif opts["ana"] == "rwenergy" :
        folderStatusName = "rw_energy_calibration_status"
        foldername = "rw_energy_calibration"
        columns = ["calo", "xtal", "pulseintegral_to_mev"]
        types = [ "int", "int", "real"]
        cstring = MakeString(columns)
        tstring = MakeString(types)
        
        run_range = [ 30970, 35000 ] #[14395,17600], [23608, 27500], [29910, 30969], [30970, 35000]
        values    = [ [ None, None, None ] ]
        jsonFile = CreateJsonFile(opts,run_range)
        CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)
        
        calo  = -1
        xtal  = -1
        calibrationconstant = -1
        fclLines = fclFile.readlines()
        for fidx, fclLine in enumerate(fclLines) :
            line = fclLine.strip().lower()
            if line.find("calo") != -1:
                start = line.find("calo") + 4
                end   = line.find(":")
                if line[end-1:end].isdigit() :
                    end += 1
                calo  = int(line[start:end-1])
            elif line.find("xtal") != -1 :
                start = line.find("xtal") + 4
                end   = line.find(":")
                if line[end-1:end].isdigit() :
                    end += 1
                xtal  = int(line[start:end-1])
                start = line.find(":") + 1
                end   = line.find("\n")
                calibrationconstant = float(line[start:len(line)])
                value = [ calo, xtal, calibrationconstant ]
                if values[0][0] == None :
                    values.pop(0)
                values.append(value)
            if len(values) == 24*54 :
                WriteJsonFileConstants(jsonFile,values)
                CloseJsonFile(opts,jsonFile,folderStatusName,run_range)
                values *= 0
                values  = [ [None, None, None, None] ]

    elif opts["ana"] == "rwtimeoffsets" :
        folderStatusName = "rw_time_alignment_status"
        foldername = "rw_time_alignment"
        columns = ["calo", "xtal", "calo_offset", "xtal_offset"]
        types = [ "int", "int", "real", "real"]
        cstring = MakeString(columns)
        tstring = MakeString(types)
        
        run_range = [ 30970 , 35000 ] #[14395,17600], [23608, 27500], [29910, 30969], [30970, 35000]
        values    = [ [ None, None, None, None ] ]
        jsonFile = CreateJsonFile(opts,run_range)
        CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)
        
        calo  = -1
        xtal  = -1
        calo_offset = -1
        xtal_offset = -1
        fclLines = fclFile.readlines()
        for fidx, fclLine in enumerate(fclLines) :
            line = fclLine.strip().lower()
            if line.find("calo") != -1:
                start = line.find("calo") + 4
                end   = line.find(":")
                if line[end-1:end].isdigit() :
                    end += 1
                calo  = int(line[start:end-1])
            elif line.find("global") != -1 :
                start = line.find(":") + 1
                end = line.find("\n")
                calo_offset = float(line[start:len(line)])
            elif line.find("xtal") != -1 :
                start = line.find("xtal") + 4
                end   = line.find(":")
                if line[end-1:end].isdigit() :
                    end += 1
                xtal  = int(line[start:end-1])
                start = line.find(":") + 1
                end   = line.find("\n")
                xtal_offset = float(line[start:len(line)])
                value = [ calo, xtal, calo_offset, xtal_offset ]
                if values[0][0] == None :
                    values.pop(0)
                values.append(value)
            if len(values) == 24*54 :
                WriteJsonFileConstants(jsonFile,values)
                CloseJsonFile(opts,jsonFile,folderStatusName,run_range)
                values *= 0
                values  = [ [None, None, None, None] ]

    elif opts["ana"] == "channelstatus" :
        folderStatusName = "calo_channel_quality_status"
        foldername = "calo_channel_quality"
        columns = ["calo", "xtal", "calo_quality", "xtal_quality"]
        types = [ "int", "int", "bool", "bool"]
        cstring = MakeString(columns)
        tstring = MakeString(types)

        run_range = [ 26208 , 29926 ] #[26086,26207]
        values    = [ [ None, None, None, None ] ]
        jsonFile = CreateJsonFile(opts,run_range)
        CreateJsonFileHeader(jsonFile,foldername,cstring,tstring)

        calo  = -1
        xtal  = -1
        calo_quality = 0
        xtal_quality = 0
        fclLines = fclFile.readlines()
        for fidx, fclLine in enumerate(fclLines) :
            line = fclLine.strip().lower()
            if line.find("calo") != -1:
                start = line.find("calo") + 4
                end   = line.find(":")
                if line[end-1:end].isdigit() :
                    end += 1
                calo  = int(line[start:end-1])
            elif line.find("global") != -1 :
                start = line.find(":") + 1
                end = line.find("\n")
                calo_quality = int(line[start:len(line)])
            elif line.find("xtal") != -1 :
                start = line.find("xtal") + 4
                end   = line.find(":")
                if line[end-1:end].isdigit() :
                    end += 1
                xtal  = int(line[start:end-1])
                start = line.find(":") + 1
                end   = line.find("\n")
                xtal_quality = int(line[start:len(line)])
                value = [ calo, xtal, calo_quality, xtal_quality ]
                if values[0][0] == None :
                    values.pop(0)
                values.append(value)
            if len(values) == 24*54 :
                WriteJsonFileConstants(jsonFile,values)
                CloseJsonFile(opts,jsonFile,folderStatusName,run_range)
                values *= 0
                values  = [ [None, None, None, None] ]        

    else :
      fclFile.close()
      sys.exit( "The analysis is unsupported. Please update the script to account for your FHiCL file format." )


   


"""
main function
"""
def main() :

    # Get the options
    if sys.argv[1] == "--help" or sys.argv[1] == "-h" :
       JsonParserHelpOpts()
       _parser.parse_args( "--help".split() )

    else :
       JsonParserHelpOpts()
       (opts, args) = _parser.parse_args()
       opts = vars(opts)

       if opts["fcl"] == None :
          sys.exit("The input fhicl file is required.")

       if opts["iov"] == None :
          sys.exit("The interval of validity must be specify.")

       if opts["ana"] == None :
          sys.exit("The analysis type must be specify.")     

    # Create Json files
    CreateJsonFiles(opts)
     


if __name__ == "__main__" :
   main()

