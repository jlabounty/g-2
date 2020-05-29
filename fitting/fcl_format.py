import numpy 
import os 
import sys
import argparse


def main( file, safemode, overwrite ):
    '''
        Formats the input fcl file according to my personal preferences
    '''
    #back up the file before formatting
    os.system("cp "+str(file)+" "+str(file)+"_backup")

    if(not overwrite):
        print("hi")
        outfile = str(file)+"_new"
    else:
        outfile = str(file)
    fout = open(outfile,"w")

    print("Processing", file)
    ntabs = 0
    with open(file+"_backup","r") as fin:
        for line in fin:
            #print(line)
            newline, ntabs = formatLine(line, ntabs)
            if(len(newline) > 0):
                #print("|",newline.strip("\n"),"|")
                #fout.writelines(str(ntabs)+"\n")
                fout.writelines(newline)

    fout.close()

    if(not safemode):
        os.system("rm -f "+str(file)+"_backup")

    print("All done! Written to", outfile)

def formatLine(line, ntabs):
    #strip any leading/trailing whitespace
    line = line.strip("\n").strip(" ")#.strip("\t")

    #unify comment type
    line = line.replace("//","# ",1)

    #return (line+"\n", ntabs)

    #parse the line
    if(len(line) is 0 or line.isspace()):
        #do nothing
        newline = line 
        return ("", ntabs)
    elif(line[0] is "#"):
        #do nothing to comments for now
        newline = line 
    else:
        newline = line
        # for char in line:
        #     print(char)
        if("{" in newline and "}" in newline):
            #if this is just and open/close brackers, then keep on the same line.
            ntabs = ntabs 
            newline = "\t"+newline 
        elif("{" in newline ):
            #split line on opening string
            if( len(newline) > 1 ):
                newline = newline.replace("{", "\n"+apptabs(ntabs)+"{\n\t")
            ntabs += 1
        elif("}" in newline  ):
            ntabs -= 1
            if( len(newline) > 1):
                newline = newline.replace("}", "\n"+apptabs(ntabs)+"}")
        
        if(("[" in newline) and ("]" not in newline) and len(newline) > 1):
            #indent multiline vectors
            newline = newline.replace("[","\n"+apptabs(ntabs)+"[\n"+apptabs(ntabs+1))
            ntabs += 1
        if(("]" in newline) and ("[" not in newline) and len(newline) > 1):
            #unindent multiline vectors
            ntabs -= 1
            newline = "\t"+newline 
            newline = newline.replace("]","\n"+apptabs(ntabs)+"]")


    #add the appropriate number of tabs
    if("{" in line):
        newline = apptabs(ntabs-1)+newline
    else:
        newline = apptabs(ntabs)+newline

    if(":" in newline and ntabs < 1):
        #blank line before every new module
        newline = "\n"+newline

    #add final trailing newline
    newline += "\n"

    return (newline, ntabs)

def apptabs(ntabs):
    ding = ""
    for i in range(ntabs):
        ding += "\t"

    return ding 


if __name__ == "__main__":
    #file = sys.argv[1]
    parser = argparse.ArgumentParser(description='Process fcl file formatting options')
    parser.add_argument('file', default=None, type=str, 
        help="fcl file to be parsed")
    parser.add_argument("--safemode-off", default=False, action='store_true', 
        help="If true, will keep backup file in the same directory with _backup appended to file name")
    parser.add_argument("--overwrite", default=False, action='store_true', 
        help="If true, will overwrite existing fcl file. If false, will create new file in same directory")
    ding = parser.parse_args(sys.argv[1:])

    print(ding)
    print(sys.argv)

    if(ding.file is None):
        raise ValueError("--file was not set")

    for i in range(1):
        main(ding.file, (not ding.safemode_off), ding.overwrite)
