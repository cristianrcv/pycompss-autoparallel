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
    a = create_matrix(n_size, False)
    b = create_matrix(n_size, True)

    return a, b


def create_matrix(n_size, is_zero):
    mat = []
    for i in range(n_size):
        mat.append([])
        for j in range(n_size):
            mb = create_block(j, n_size, is_zero)
            mat[i].append(mb)

    return mat


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def create_block(index, n_size, is_zero):
    if is_zero:
        return float(0)
    else:
        return float(index) / float(n_size)


############################################
# MAIN FUNCTION
############################################

def jacobi_2d(a, b, n_size, t_size, coef):
    # Debug
    if __debug__:
        # TODO: PyCOMPSs BUG sync-INOUT-sync
        # a = compss_wait_on(a)
        # b = compss_wait_on(b)
        print("Matrix A:")
        print(a)
        print("Matrix B:")
        print(b)

    # Jacobi
    for _ in range(t_size):
        for i in range(2, n_size - 1):
            for j in range(2, n_size - 1):
                # b[i][j] = 0.2 * (a[i][j] + a[i][j - 1] + a[i][1 + j] + a[1 + i][j] + a[i - 1][j])
                b[i][j] = compute_b(coef, a[i][j], a[i][j - 1], a[i][1 + j], a[1 + i][j], a[i - 1][j])
        for i in range(2, n_size - 1):
            for j in range(2, n_size - 1):
                a[i][j] = copy(b[i][j])

    # Debug result
    if __debug__:
        print("New Matrix A:")
        a = compss_wait_on(a)
        print(a)
        print("New Matrix B:")
        b = compss_wait_on(b)
        print(b)


############################################
# MATHEMATICAL FUNCTIONS
############################################

@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def compute_b(coef, a_left, a_center, a_right, a_top, a_bottom):
    # import time
    # start = time.time()

    return coef * (a_left + a_center + a_right + a_top + a_bottom)

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def copy(b):
    return b


############################################
# MAIN
############################################

if __name__ == "__main__":
    # Import libraries
    import time

    # Parse arguments
    import sys

    args = sys.argv[1:]
    NSIZE = int(args[0])
    TSIZE = int(args[1])
    COEF = float(1) / float(3)

    # Log arguments if required
    if __debug__:
        print("Running jacobi-2d application with:")
        print(" - NSIZE = " + str(NSIZE))
        print(" - TSIZE = " + str(TSIZE))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    A, B = initialize_variables(NSIZE)
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    jacobi_start_time = time.time()
    jacobi_2d(A, B, NSIZE, TSIZE, COEF)
    compss_barrier()
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = jacobi_start_time - start_time
    jacobi_time = end_time - jacobi_start_time

    print("RESULTS -----------------")
    print("VERSION USERPARALLEL")
    print("NSIZE " + str(NSIZE))
    print("TSIZE " + str(TSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("JACOBI_TIME " + str(jacobi_time))
    print("-------------------------")
