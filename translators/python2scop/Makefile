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

compile: converter_c2scop.c
	@echo "Compiling Converter"
	$(CC) converter_c2scop.c -o converter_c2scop $(CFLAGS) $(LDLIBS)

exec: compile
	@echo "Executing Converter for src.c to out.scop"
	export LD_LIBRARY_PATH=$$LD_LIBRARY_PATH:$(OPENSCOP_LIB):$(CLAN_LIB); ./converter_c2scop example1_src_seidel.c out1_seidel.scop
	export LD_LIBRARY_PATH=$$LD_LIBRARY_PATH:$(OPENSCOP_LIB):$(CLAN_LIB); ./converter_c2scop example2_src_matmul.cc out2_matmul.scop

clean:
	@echo "Cleaning folder"
	-rm -f converter_c2scop core out1_seidel.scop out2_matmul.scop

