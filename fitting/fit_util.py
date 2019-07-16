def DumpClass( item ):
    ''' 
        Dump the contents of a class in a more readable way. 
    '''
    try:
        print("Dumping: ", item)
        print("Class: ", type(item))
        ding = vars(item)
        #print(ding)
        for var in ding:
            print("   ", var, "=", ding[var])
    except:
        print("Unable to dump members of this class")

def GetBlindingPhrase( file ):
    '''
        simple util to get the first line of a file and return as string for use as a blinding phrase
    '''
    with open(file) as f:
        content = f.readlines()
        phrase = content[0].strip()
    return str(phrase)