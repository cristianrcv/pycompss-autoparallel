# Please enter here the locations for the CLooG, OpenScop and Clan
# include and library if they aren't the default values
# (i.e., /usr/lib and /usr/include).

OPENSCOP_INC = /opt/openscop/include
OPENSCOP_LIB = /opt/openscop/lib64

CLAN_INC = /opt/pluto/include
CLAN_LIB = /opt/pluto/lib64

CC = gcc
LDLIBS= -losl -lclan
CFLAGS= -I $(OPENSCOP_INC) -L $(OPENSCOP_LIB) \
        -I $(CLAN_INC)     -L $(CLAN_LIB)

compile: converter.c
	@echo "Compiling Converter"
	$(CC) converter.c -o converter $(CFLAGS) $(LDLIBS)

exec: compile
	@echo "Executing Converter for src.c to out.scop"
	-./converter src.c out.scop

clean:
	@echo "Cleaning folder"
	-rm -f converter core out.scop

