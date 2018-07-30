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

import numpy as np


############################################
# MATRIX GENERATION
############################################

def initialize_variables(n_size):
    mat = create_matrix(n_size)

    return mat


def create_matrix(n_size):
    mat = []
    for i in range(n_size):
        mb = create_entry(i, n_size)
        mat.append(mb)
    return mat


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def create_entry(i, size):
    return np.float64(np.float64(i) / np.float64(size))


############################################
# MAIN FUNCTION
############################################

# @parallel()
# [COMPSs Autoparallel] Begin Autogenerated code
import math

from pycompss.api.api import compss_barrier, compss_wait_on, compss_open
from pycompss.api.task import task
from pycompss.api.parameter import *
from pycompss.util.translators.arg_utils.arg_utils import ArgUtils


@task(n_size=IN, index=IN, mat=INOUT, returns="LT3_args_size")
def LT3(n_size, index, *args):
    global LT3_args_size
    mat, = ArgUtils.rebuild_args(args)
    for t1 in range(2, n_size - 1 + 1):
        mat[t1 - (2 if n_size >= 2 and (index >= 3 or index == 2) else index)] = S1_no_task(n_size)
        S2_no_task(mat[index - (2 if n_size >= 2 and (index >= 3 or index == 2) else index)])
    return ArgUtils.flatten_args(mat)


@task(n_size=IN, returns=1)
def S1(n_size):
    return compute_mat(n_size)


def S1_no_task(n_size):
    return compute_mat(n_size)


@task(var1=IN)
def S2(var1):
    display(var1)


def S2_no_task(var1):
    display(var1)


def test_main(mat, n_size):
    if __debug__:
        mat = compss_wait_on(mat)
        print('Matrix:')
        print(mat)
    index = 4
    if n_size >= 3:
        lbp = 2
        ubp = n_size - 1
        LT3_aux_0 = [mat[gv0] for gv0 in range(2 if n_size >= 2 and (index >= 3 or index == 2) else index, n_size if
            n_size >= 2 and (index < n_size or index == n_size) else index, 1)]
        LT3_argutils = ArgUtils()
        global LT3_args_size
        LT3_flat_args, LT3_args_size = LT3_argutils.flatten(1, LT3_aux_0, LT3_aux_0)
        LT3_new_args = LT3(n_size, index, *LT3_flat_args)
        LT3_aux_0, = LT3_argutils.rebuild(LT3_new_args)
        for gv0 in range(2 if n_size >= 2 and (index >= 3 or index == 2) else index, n_size if n_size >= 2 and (
            index < n_size or index == n_size) else index, 1):
            mat[gv0] = LT3_aux_0[gv0 - (2 if n_size >= 2 and (index >= 3 or index == 2) else index)]
    compss_barrier()
    if __debug__:
        mat = compss_wait_on(mat)
        print('New Matrix:')
        print(mat)

# [COMPSs Autoparallel] End Autogenerated code


############################################
# MATHEMATICAL FUNCTIONS
############################################

def compute_mat(n_size):
    # import time
    # start = time.time()

    return n_size

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


def display(elem):
    # Display value inside task
    print("GOT: " + str(elem))


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
        print("Running test application with:")
        print(" - NSIZE = " + str(NSIZE))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    MAT = initialize_variables(NSIZE)
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    comp_start_time = time.time()
    test_main(MAT, NSIZE)
    compss_barrier(True)
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = comp_start_time - start_time
    comp_time = end_time - comp_start_time

    print("RESULTS -----------------")
    print("VERSION AUTOPARALLEL")
    print("NSIZE " + str(NSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("FDTD_TIME " + str(comp_time))
    print("-------------------------")