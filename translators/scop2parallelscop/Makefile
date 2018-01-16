# Please enter here the locations for the CLooG, OpenScop and Clan
# include and library if they aren't the default values
# (i.e., /usr/lib and /usr/include).

PLUTO_EXEC = ./pluto_exec.sh

tests: test1 test2

test1:
	@echo "Executing Test 1: Matmul"
	$(PLUTO_EXEC) ./tests/test1_matmul.src.scop ./tests/test1_matmul.out.py
	diff ./tests/test1_matmul.out.py ./tests/test1_matmul.expected.py
	@echo "PASS"

test2:
	@echo "Executing Test 2: Seidel"
	$(PLUTO_EXEC) ./tests/test2_seidel.src.scop ./tests/test2_seidel.out.py
	diff ./tests/test2_seidel.out.py ./tests/test2_seidel.expected.py
	@echo "PASS"

clean:
	@echo "Cleaning folder"
	-rm -f ./tests/t1_matmul.out.py ./tests/test2_seidel.out.py

