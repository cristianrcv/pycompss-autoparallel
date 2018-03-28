#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from pycompss.api.constraint import constraint
from pycompss.api.task import task
from pycompss.api.api import compss_barrier
from pycompss.api.api import compss_wait_on


############################################
# MATRIX GENERATION
############################################

def initialize_variables(n_size):
    h = create_matrix(n_size)
    e = create_matrix(n_size + 1)

    return h, e


def create_matrix(n_size):
    mat = []
    for i in range(n_size):
        mb = create_block(i, n_size)
        mat.append(mb)
    return mat


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def create_block(index, n_size):
    return float(index) / float(n_size)


############################################
# MAIN FUNCTION
############################################

def fdtd_1d(h, e, t_size, n_size, coef1, coef2):
    # Debug
    if __debug__:
        # TODO: PyCOMPSs BUG sync-INOUT-sync
        # h = compss_wait_on(h)
        # e = compss_wait_on(e)
        print("Matrix H:")
        print(h)
        print("Matrix E:")
        print(e)

    # FDTD
    for _ in range(t_size):
        for i in range(1, n_size):
            e[i] = compute_e(e[i], coef1, h[i], h[i - 1])
        for i in range(n_size):
            h[i] = compute_h(h[i], coef2, e[i + 1], e[i])

    # Debug result
    if __debug__:
        print("New Matrix H:")
        h = compss_wait_on(h)
        print(h)


############################################
# MATHEMATICAL FUNCTIONS
############################################
@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def compute_e(e, coef1, h2, h1):
    # import time
    # start = time.time()

    return e - coef1 * (h2 - h1)

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def compute_h(h, coef2, e2, e1):
    # import time
    # start = time.time()

    return h - coef2 * (e2 - e1)

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
    TSIZE = int(args[0])
    NSIZE = int(args[1])
    COEF1 = 0.5
    COEF2 = 0.7

    # Log arguments if required
    if __debug__:
        print("Running fdtd-1d application with:")
        print(" - TSIZE = " + str(TSIZE))
        print(" - NSIZE = " + str(NSIZE))
        print(" - COEF1 = " + str(COEF1))
        print(" - COEF2 = " + str(COEF2))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    H, E = initialize_variables(NSIZE)
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    fdtd_start_time = time.time()
    fdtd_1d(H, E, TSIZE, NSIZE, COEF1, COEF2)
    compss_barrier()
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = fdtd_start_time - start_time
    fdtd_time = end_time - fdtd_start_time

    print("RESULTS -----------------")
    print("VERSION USERPARALLEL")
    print("TSIZE " + str(TSIZE))
    print("NSIZE " + str(NSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("FDTD_TIME " + str(fdtd_time))
    print("-------------------------")
