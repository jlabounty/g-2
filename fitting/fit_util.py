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