
ROOTINC = $(shell root-config --cflags)
ROOTLIB = $(shell root-config --libs)


OBJ = gm2Labels.o gm2Style.o 

GM2OBJ = gm2Example.o $(OBJ)
BASICOBJ = gm2BasicExample.o $(OBJ)

all : gm2example gm2basicexample

.SUFFIXES: .C .o

.C.o :
	g++ $(ROOTINC) -c $<

gm2example : $(GM2OBJ)
	g++  -o $@ $(GM2OBJ) $(ROOTLIB)

gm2basicexample : $(BASICOBJ)
	g++  -o $@ $(BASICOBJ) $(ROOTLIB)

clean : 
	rm -rf *.o *~
