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

compile: translator_c2scop.c
	@echo "Compiling Translator"
	$(CC) translator_c2scop.c -o translator_c2scop $(CFLAGS) $(LDLIBS)

tests: test1 test2

test1: compile
	@echo "Executing Translator for Test 1: Matmul"
	export LD_LIBRARY_PATH=$$LD_LIBRARY_PATH:$(OPENSCOP_LIB):$(CLAN_LIB); ./translator_c2scop ./tests/test1_matmul.src.c ./tests/test1_matmul.out.scop
	diff ./tests/test1_matmul.out.scop ./tests/test1_matmul.expected.scop
	@echo "PASS"

test2: compile
	@echo "Executing Translator for Test 2: Seidel"
	export LD_LIBRARY_PATH=$$LD_LIBRARY_PATH:$(OPENSCOP_LIB):$(CLAN_LIB); ./translator_c2scop ./tests/test2_seidel.src.c ./tests/test2_seidel.out.scop
	diff ./tests/test2_seidel.out.scop ./tests/test2_seidel.expected.scop
	@echo "PASS"

clean:
	@echo "Cleaning folder"
	-rm -f translator_c2scop core ./tests/test1_matmul.out.scop ./tests/test2_seidel.out.scop

