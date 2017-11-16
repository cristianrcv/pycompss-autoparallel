# Please enter here the locations for the CLooG, OpenScop and Clan
# include and library if they aren't the default values
# (i.e., /usr/lib and /usr/include).

CLOOG_INC = /opt/pluto/include
CLOOG_LIB = /opt/pluto/lib64

OPENSCOP_INC = /opt/openscop/include
OPENSCOP_LIB = /opt/openscop/lib64

CC = gcc
LDLIBS= -lcloog-isl -losl
CFLAGS= -DCLOOG_INT_GMP \
        -I $(CLOOG_INC)    -L $(CLOOG_LIB) \
        -I $(OPENSCOP_INC) -L $(OPENSCOP_LIB) 

compile: converter.c
	@echo "Compiling Converter"
	$(CC) converter.c -o converter $(CFLAGS) $(LDLIBS)

exec: compile
	@echo "Executing Converter for src.c to out.scop"
	-./converter src.scop out.c

clean:
	@echo "Cleaning folder"
	-rm -f converter core out.scop

