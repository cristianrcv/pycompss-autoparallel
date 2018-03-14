#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from pycompss.api.parallel import parallel
from pycompss.api.constraint import constraint
from pycompss.api.task import task
from pycompss.api.api import compss_barrier, compss_wait_on


def initialize_variables():
    for matrix in [A, B]:
        for i in range(MSIZE):
            matrix.append([])
            for _ in range(MSIZE):
                mb = create_block(BSIZE, False)
                matrix[i].append(mb)
    for i in range(MSIZE):
        C.append([])
        for _ in range(MSIZE):
            mb = create_block(BSIZE, True)
            C[i].append(mb)


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def create_block(b_size, is_random):
    import numpy as np

    if is_random:
        block = np.array(np.random.random((b_size, b_size)), dtype=np.double, copy=False)
    else:
        block = np.array(np.zeros((b_size, b_size)), dtype=np.double, copy=False)
    mb = np.matrix(block, dtype=np.double, copy=False)
    return mb


@parallel()
def matmul():
    # Debug
    if __debug__:
        print("Matrix A:")
        input_a = compss_wait_on(A)
        print(input_a)
        print("Matrix B:")
        input_b = compss_wait_on(A)
        print(input_b)
        print("Matrix C:")
        input_c = compss_wait_on(A)
        print(input_c)

    # Matrix multiplication
    for i in range(MSIZE):
        for j in range(MSIZE):
            for k in range(MSIZE):
                # multiply(A[i][k], B[k][j], C[i][j])
                C[i][j] += A[i][k] * B[k][j]

    # Debug result
    if __debug__:
        print(" New Matrix C:")
        for i in range(MSIZE):
            for j in range(MSIZE):
                print("C" + str(i) + str(j) + " = " + str(compss_wait_on(C[i][j])))


def multiply(a, b, c):
    # import time
    # start = time.time()

    c += a * b

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


# MAIN CODE
if __name__ == "__main__":
    # Import libraries
    import time

    # Parse arguments
    import sys

    args = sys.argv[1:]
    MSIZE = int(args[0])
    BSIZE = int(args[1])
    A = []
    B = []
    C = []

    # Log arguments if required
    if __debug__:
        print("Running matmul application with:")
        print(" - MSIZE = " + str(MSIZE))
        print(" - BSIZE = " + str(BSIZE))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    initialize_variables()
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    mult_start_time = time.time()
    matmul()
    compss_barrier()
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = mult_start_time - start_time
    mult_time = end_time - mult_start_time

    print("RESULTS -----------------")
    print("MSIZE " + str(MSIZE))
    print("BSIZE " + str(MSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("MULT_TIME " + str(mult_time))
    print("-------------------------")
