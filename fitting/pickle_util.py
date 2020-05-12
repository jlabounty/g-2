
import pickle 
import numba
from numba import int32, float64    # import the types
from numba import *

import numpy as np
import ROOT as r
import matplotlib.colors as colors

import pickle
from functools import wraps, update_wrapper

import numpy as np
from numba import jitclass, int32, float64
  
def storeData(outfile, ding): 
    # Its important to use binary mode 
    dbfile = open(str(outfile), 'ab') 
    # source, destination 
    pickle.dump(ding, dbfile)                      
    dbfile.close() 
    print("Saved", ding, "to file:", outfile)
  
def loadData(filename): 
    # for reading also binary mode is important 
    dbfile = open(str(filename), 'rb')      
    db = pickle.load(dbfile) 
    for keys in db: 
        print(keys, '=>', db[keys]) 
    dbfile.close() 

    return db

def pickle_dump(ding, file=None):
    '''
        loop over all attributes and dump them to a pickle file (or to console if no file is specified)
    '''
    allstrings = []
    for x in dir(ding):
        typestring = str(type(getattr(ding, x)))
        classname = type(getattr(ding, x)).__name__
        modulename = type(getattr(ding, x)).__module__
        #print(x, typestring)
        if("method" in typestring or "CPUDispatcher" in typestring or "NoneType" in typestring or "__" in x):
            continue
        elif("jitclass" in typestring):
            #print("****************")
            allstrings.append((x, typestring, classname, modulename, dumps_jitclass( getattr(ding, x) )))
        else:
            #continue
            allstrings.append((x, typestring, classname, modulename, pickle.dumps( getattr(ding, x) )))
    
    to_dump = pickle.dumps((type(ding).__name__, type(ding).__module__, allstrings))

    if(file is None):
        print(to_dump)
    else:
        with open(file,"wb") as fi:
            fi.write(to_dump)
            
    return to_dump

def pickle_load(pickle_text):
    name, module, data = pickle.loads(pickle_text) #this is the output from pickle_dump, everything compressed into one object
    import importlib
    #from module import name 
    mod  = importlib.import_module(module)
    print(mod)
    #print(name, "is the class which contains:")
    #for x in globals():
    #    print(x)
    #print(globals())
    #cls = globals()[name]
    cls = getattr(mod, name)
    instance = cls() # **data['struct']
    for x, typestring, classname, modulename, obj in data:
        #print(x, obj)
        if("jitclass" in typestring):
            #print(x, loads_jitclass(obj))
            setattr(instance, x, loads_jitclass(obj, classname, modulename))
        else:
            print(x, pickle.loads(obj))
            obj2 = pickle.loads(obj)
            setattr(instance, x, obj2)

    return instance

def dumps_jitclass(jc): # https://stackoverflow.com/questions/49246021/serialization-of-numba-classes
    typ = jc._numba_type_
    fields = typ.struct

    # structi = {}
    # for k in fields:
    #     if( "jit" in str(getattr(jc, k) ) ):
    #         structi.update({k: dumps_jitclass( getattr(jc, k) )})
    #     else:
    #         structi.update({k:getattr(jc, k)})
    data = {
        'name': typ.classname,
        'struct': {k: getattr(jc, k) for k in fields}
    }

    return pickle.dumps(data)


from py_th2 import *
def loads_jitclass(s, classname, module):
    #import importlib
    #from module import name 
    #mod  = importlib.import_module(module)
    #class_ = getattr(mod, classname)
    data = pickle.loads(s)
    #print(data)
    cls = globals()[data['name']]
    instance = cls() # **data['struct']
    for key in data['struct']:
        typestring = str(type(data['struct'][key]))
        if("numpy" in typestring): 
            setattr(instance,key, np.copy(data['struct'][key]))
        elif("method" in typestring):
            #do nothing
            continue
        else:
            setattr(instance,key, data['struct'][key])

    return instance