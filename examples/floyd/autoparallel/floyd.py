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
    d = create_matrix(n_size)

    return d


def create_matrix(n_size):
    mat = []
    for i in range(n_size):
        mat.append([])
        for j in range(n_size):
            mb = create_block(n_size, i == j)
            mat[i].append(mb)

    return mat


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def create_block(n_size, is_zero):
    if is_zero:
        return float(0)
    else:
        import random
        return n_size * random.random()


############################################
# MAIN FUNCTION
############################################

@parallel()
def floyd(d, n_size):
    # Debug
    if __debug__:
        # TODO: PyCOMPSs BUG sync-INOUT-sync
        # d = compss_wait_on(d)
        print("Matrix d:")
        print(d)

    # Floyd
    for k in range(n_size):
        for y in range(n_size):
            for x in range(n_size):
                d[y][x] = compute_distance(d[y][x], d[y][k], d[k][x])

    # Debug result
    if __debug__:
        print("New Matrix D:")
        d = compss_wait_on(d)
        print(d)


############################################
# MATHEMATICAL FUNCTIONS
############################################

def compute_distance(distance, path1, path2):
    # import time
    # start = time.time()

    new_distance = path1 + path2

    if new_distance < distance:
        return new_distance
    else:
        return distance

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
    NSIZE = int(args[0])

    # Log arguments if required
    if __debug__:
        print("Running floyd application with:")
        print(" - NSIZE = " + str(NSIZE))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    D = initialize_variables(NSIZE)
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    floyd_start_time = time.time()
    floyd(D, NSIZE)
    compss_barrier()
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = floyd_start_time - start_time
    floyd_time = end_time - floyd_start_time

    print("RESULTS -----------------")
    print("VERSION AUTOPARALLEL")
    print("NSIZE " + str(NSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("FLOYD_TIME " + str(floyd_time))
    print("-------------------------")
