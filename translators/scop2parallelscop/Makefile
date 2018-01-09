# Please enter here the locations for the CLooG, OpenScop and Clan
# include and library if they aren't the default values
# (i.e., /usr/lib and /usr/include).

PLUTO_EXEC = ./pluto_exec.sh

test_all: test1 test2

test1:
	@echo "Executing Test 1: Matmul"
	$(PLUTO_EXEC) test1_matmul.src test1_matmul.out

test2:
	@echo "Executing Test 2: Seidel"
	$(PLUTO_EXEC) test2_seidel.src test2_seidel.out

clean:
	@echo "Cleaning folder"
	-rm -f *.out

