#!/usr/bin/python

# -*- coding: utf-8 -*-

# Imports
from pycompss.api.task import task
from pycompss.api.parameter import *
from pycompss.api.api import compss_barrier
from pycompss.api.api import compss_wait_on


# Initializes a matrix with size (n x m) with blocks (bSize x bSize) randomly or not
def initialize(n_size, m_size, b_size, random):
    import numpy as np

    matrix = []
    for i in range(n_size):
        matrix.append([])
        for j in range(m_size):
            if random:
                block = np.array(np.random.random((b_size, b_size)), dtype=np.double, copy=False)
            else:
                block = np.array(np.zeros((b_size, b_size)), dtype=np.double, copy=False)
            mb = np.matrix(block, dtype=np.double, copy=False)
            matrix[i].append(mb)
    return matrix


@task(c = INOUT)
def multiply(a, b, c):
    #import time
    #start = time.time()

    import numpy as np
    #np.show_config()

    c += a*b

    #end = time.time()
    #tm = end - start
    #print "TIME: " + str(tm*1000) + " msec"


# Performs the matrix multiplication by blocks
def matmul(m_size, n_size, k_size, b_size, debug):
    # Initialize
    a = initialize(m_size, n_size, b_size, True)
    b = initialize(n_size, k_size, b_size, True)
    c = initialize(m_size, k_size, b_size, False)

    # Debug
    if debug:
        print "Matrix A:"
        print a
        print "Matrix B:"
        print b
        print "Matrix C:"
        print c

    # Perform computation
    # c = a*b
    for i in range(m_size):
        for j in range(k_size):
            for k in range(n_size):
                multiply(a[i][k], b[k][j], c[i][j])

    compss_barrier()
    #    for i in range(m_size):
    #        for j in range(k_size):
    #           print "C" + str(i) + str(j) + "=" + str(compss_wait_on(c[i][j]))

    # Debug
    if debug:
        print "Matrix C:"
        print c

    # Result
    return c


# MAIN CODE
if __name__ == "__main__":
    # Import libraries
    import time

    # Parse arguments
    m_mat_size = 8
    n_mat_size = 8
    k_mat_size = 8
    block_size = 4
    is_debug = True

    # Begin computation
    startTime = time.time()
    result = matmul(m_mat_size, n_mat_size, k_mat_size, block_size, is_debug)
    endTime = time.time()

    # Log results and time
    print "Elapsed Time {} (s)".format(endTime - startTime)
