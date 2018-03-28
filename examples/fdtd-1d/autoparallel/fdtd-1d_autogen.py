#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from pycompss.api.parallel import parallel
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

# [COMPSs Autoparallel] Begin Autogenerated code
import math

from pycompss.api.api import compss_barrier, compss_wait_on, compss_open
from pycompss.api.task import task
from pycompss.api.parameter import *


@task(var2=IN, coef1=IN, var3=IN, var4=IN, returns=1)
def S1(var2, coef1, var3, var4):
    return compute_e(var2, coef1, var3, var4)


@task(var2=IN, coef2=IN, var3=IN, var4=IN, returns=1)
def S2(var2, coef2, var3, var4):
    return compute_h(var2, coef2, var3, var4)


def fdtd_1d(h, e, t_size, n_size, coef1, coef2):
    if __debug__:
        print('Matrix H:')
        print(h)
        print('Matrix E:')
        print(e)
    if n_size >= 1 and t_size >= 1:
        if n_size >= 2:
            h[0] = S2(h[0], coef2, e[0 + 1], e[0])
        if n_size == 1:
            lbp = 0
            ubp = 2 * t_size - 2
            for t1 in range(0, 2 * t_size - 2 + 1):
                if t1 % 2 == 0:
                    h[0] = S2(h[0], coef2, e[0 + 1], e[0])
        if n_size >= 2:
            lbp = 1
            ubp = 2 * t_size - 2
            for t1 in range(1, 2 * t_size - 2 + 1):
                if t1 % 2 == 0:
                    h[0] = S2(h[0], coef2, e[0 + 1], e[0])
                lbp = int(math.ceil(float(t1 + 1) / float(2)))
                ubp = min(int(math.floor(float(t1 + n_size - 1) / float(2))
                    ), t1)
                for t2 in range(lbp, ubp + 1):
                    e[-t1 + 2 * t2] = S1(e[-t1 + 2 * t2], coef1, h[-t1 + 2 *
                        t2], h[-t1 + 2 * t2 - 1])
                    h[0] = S2(h[0], coef2, e[0 + 1], e[0])
        lbp = 2 * t_size - 1
        ubp = n_size + 2 * t_size - 3
        for t1 in range(2 * t_size - 1, n_size + 2 * t_size - 3 + 1):
            lbp = t1 - t_size + 1
            ubp = min(int(math.floor(float(t1 + n_size - 1) / float(2))), t1)
            for t2 in range(lbp, ubp + 1):
                e[-t1 + 2 * t2] = S1(e[-t1 + 2 * t2], coef1, h[-t1 + 2 * t2
                    ], h[-t1 + 2 * t2 - 1])
                h[0] = S2(h[0], coef2, e[0 + 1], e[0])
    compss_barrier()
    if __debug__:
        print('New Matrix H:')
        h = compss_wait_on(h)
        print(h)

# [COMPSs Autoparallel] End Autogenerated code


############################################
# MATHEMATICAL FUNCTIONS
############################################

def compute_e(e, coef1, h2, h1):
    # import time
    # start = time.time()

    return e - coef1 * (h2 - h1)

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


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
    print("VERSION AUTOPARALLEL")
    print("TSIZE " + str(TSIZE))
    print("NSIZE " + str(NSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("FDTD_TIME " + str(fdtd_time))
    print("-------------------------")