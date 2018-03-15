#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from pycompss.api.constraint import constraint
from pycompss.api.task import task
from pycompss.api.api import compss_barrier
from pycompss.api.api import compss_wait_on
from pycompss.api.parameter import *


def initialize_variables(m_size, b_size):
    a = create_matrix(m_size, b_size, True)
    b = create_matrix(m_size, b_size, True)
    c = create_matrix(m_size, b_size, False)

    return a, b, c


def create_matrix(m_size, b_size, is_random):
    mat = []
    for i in range(m_size):
        mat.append([])
        for _ in range(m_size):
            mb = create_block(b_size, is_random)
            mat[i].append(mb)
    return mat


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


def matmul(a, b, c, m_size):
    # Debug
    if __debug__:
        print("Matrix A:")
        a = compss_wait_on(a)
        print(a)
        print("Matrix B:")
        b = compss_wait_on(b)
        print(b)
        print("Matrix C:")
        c = compss_wait_on(c)
        print(c)

    # Matrix multiplication
    for i in range(m_size):
        for j in range(m_size):
            for k in range(m_size):
                multiply(a[i][k], b[k][j], c[i][j])

    # Debug result
    if __debug__:
        print("New Matrix C:")
        c = compss_wait_on(c)
        print(c)


@constraint(ComputingUnits="${ComputingUnits}")
@task(c=INOUT)
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

    # Log arguments if required
    if __debug__:
        print("Running matmul application with:")
        print(" - MSIZE = " + str(MSIZE))
        print(" - BSIZE = " + str(BSIZE))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    A, B, C = initialize_variables(MSIZE, BSIZE)
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    mult_start_time = time.time()
    matmul(A, B, C, MSIZE)
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
