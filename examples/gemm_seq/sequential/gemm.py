#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import numpy as np


############################################
# MATRIX GENERATION
############################################

def initialize_variables(m_size):
    a = create_matrix(m_size)
    b = create_matrix(m_size)
    c = create_matrix(m_size)

    return a, b, c


def create_matrix(m_size):
    mat = []
    for i in range(m_size):
        mat.append([])
        for _ in range(m_size):
            mb = create_entry()
            mat[i].append(mb)
    return mat


def create_entry():
    import os
    np.random.seed(ord(os.urandom(1)))
    return np.float64(100 * np.random.random())


############################################
# MAIN FUNCTION
############################################

def matmul(a, b, c, m_size, alpha, beta):
    # Debug
    if __debug__:
        print("Matrix A:")
        print(a)
        print("Matrix B:")
        print(b)
        print("Matrix C:")
        print(c)

    # Matrix multiplication
    for i in range(m_size):
        for j in range(m_size):
            c[i][j] = scale(c[i][j], beta)
        for k in range(m_size):
            for j in range(m_size):
                c[i][j] = multiply(c[i][j], alpha, a[i][k], b[k][j])

    # Debug result
    if __debug__:
        print("New Matrix C:")
        print(c)


############################################
# MATHEMATICAL FUNCTIONS
############################################

def scale(c, beta):
    # import time
    # start = time.time()

    return c * beta

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


def multiply(c, alpha, a, b):
    # import time
    # start = time.time()

    return c + alpha * np.dot(a, b)

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


############################################
# MAIN
############################################

if __name__ == "__main__":
    # Import libraries
    import time

    # Parse arguments
    import sys

    args = sys.argv[1:]
    MSIZE = int(args[0])
    ALPHA = np.float64(1.5)
    BETA = np.float64(1.2)

    # Log arguments if required
    if __debug__:
        print("Running matmul application with:")
        print(" - MSIZE = " + str(MSIZE))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    A, B, C = initialize_variables(MSIZE)

    # Begin computation
    if __debug__:
        print("Performing computation")
    mult_start_time = time.time()
    matmul(A, B, C, MSIZE, ALPHA, BETA)
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = mult_start_time - start_time
    mult_time = end_time - mult_start_time

    print("RESULTS -----------------")
    print("VERSION SEQUENTIAL")
    print("MSIZE " + str(MSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("MULT_TIME " + str(mult_time))
    print("-------------------------")
