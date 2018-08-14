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

def initialize_variables(n_size, m_size):
    mat = create_matrix(n_size, m_size)

    return mat


def create_matrix(n_size, m_size):
    mat = []
    for i in range(n_size):
        row = []
        for j in range(m_size):
            mb = create_entry(i + j, n_size + m_size)
            row.append(mb)
        mat.append(row)
    return mat


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def create_entry(index, n_size):
    return np.float64(np.float64(index) / np.float64(n_size))


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


@task(t2=IN, m_size=IN, t1=IN, n_size=IN, coef1=IN, coef2=IN, mat=INOUT, returns="LT2_args_size")
def LT2(t2, m_size, t1, n_size, coef1, coef2, *args):
    global LT2_args_size
    mat, = ArgUtils.rebuild_args(args)
    for t3 in range(32 * t2, min(m_size - 1, 32 * t2 + 31) + 1):
        lbv = 2 * t1
        ubv = min(n_size - 1, 2 * t1 + 1)
        for t4 in range(2 * t1, min(n_size - 1, 2 * t1 + 1) + 1):
            mat[t4 - 2 * t1][t3 - 32 * t2] = S1_no_task(mat[t4 - 2 * t1][t3 - 32 * t2], coef1, coef2)
    return ArgUtils.flatten_args(mat)


@task(var2=IN, coef1=IN, coef2=IN, returns=1)
def S1(var2, coef1, coef2):
    return compute(var2, coef1, coef2)


def S1_no_task(var2, coef1, coef2):
    return compute(var2, coef1, coef2)


def ep(mat, n_size, m_size, coef1, coef2):
    if __debug__:
        mat = compss_wait_on(mat)
        print('Matrix:')
        print(mat)
    if __debug__:
        import copy
        mat_seq = copy.deepcopy(mat)
        mat_expected = seq_ep(mat_seq, n_size, m_size, coef1, coef2)
    if m_size >= 1 and n_size >= 1:
        lbp = 0
        ubp = int(math.floor(float(n_size - 1) / float(2)))
        for t1 in range(lbp, ubp + 1):
            lbp = 0
            ubp = int(math.floor(float(m_size - 1) / float(32)))
            for t2 in range(0, int(math.floor(float(m_size - 1) / float(32))) + 1):
                lbp = 32 * t2
                ubp = min(m_size - 1, 32 * t2 + 31)
                LT2_aux_0 = [[mat[gv0][gv1] for gv1 in range(32 * t2, 3 * 2 + 32 * t2 if m_size >= 3 * 3 + 32 * t2 and
                    n_size >= 3 + 2 * t1 else m_size if 32 * t2 <= m_size <= 3 * 2 + 32 * t2 and n_size >= 3 + 2 *
                    t1 else 3 * 2 + 32 * t2 if m_size >= 3 * 3 + 32 * t2 and 2 * t1 <= n_size <= 2 + 2 * t1 else
                    m_size, 1)] for gv0 in range(2 * t1, 2 + 2 * t1 if m_size >= 3 * 3 + 32 * t2 and n_size >= 3 + 2 *
                    t1 else 2 + 2 * t1 if 32 * t2 <= m_size <= 3 * 2 + 32 * t2 and n_size >= 3 + 2 * t1 else n_size if
                    m_size >= 3 * 3 + 32 * t2 and 2 * t1 <= n_size <= 2 + 2 * t1 else n_size, 1)]
                LT2_argutils = ArgUtils()
                global LT2_args_size
                LT2_flat_args, LT2_args_size = LT2_argutils.flatten(1, LT2_aux_0, LT2_aux_0)
                LT2_new_args = LT2(t2, m_size, t1, n_size, coef1, coef2, *LT2_flat_args)
                LT2_aux_0, = LT2_argutils.rebuild(LT2_new_args)
                for gv0 in range(2 * t1, 2 + 2 * t1 if m_size >= 3 * 3 + 32 * t2 and n_size >= 3 + 2 * t1 else 2 + 2 *
                    t1 if 32 * t2 <= m_size <= 3 * 2 + 32 * t2 and n_size >= 3 + 2 * t1 else n_size if m_size >= 3 *
                    3 + 32 * t2 and 2 * t1 <= n_size <= 2 + 2 * t1 else n_size, 1):
                    for gv1 in range(32 * t2, 3 * 2 + 32 * t2 if m_size >= 3 * 3 + 32 * t2 and n_size >= 3 + 2 * t1 else
                        m_size if 32 * t2 <= m_size <= 3 * 2 + 32 * t2 and n_size >= 3 + 2 * t1 else 3 * 2 + 32 * t2 if
                        m_size >= 3 * 3 + 32 * t2 and 2 * t1 <= n_size <= 2 + 2 * t1 else m_size, 1):
                        mat[gv0][gv1] = LT2_aux_0[gv0 - 2 * t1][gv1 - 32 * t2]
    compss_barrier()
    if __debug__:
        mat = compss_wait_on(mat)
        print('New Matrix:')
        print(mat)
    if __debug__:
        check_result(mat, mat_expected)

# [COMPSs Autoparallel] End Autogenerated code


def compute(elem, coef1, coef2):
    return coef1 * elem + coef2


############################################
# RESULT CHECK FUNCTIONS
############################################

def seq_ep(mat, n_size, m_size, coef1, coef2):
    for i in range(n_size):
        for j in range(m_size):
            mat[i][j] = compute(mat[i][j], coef1, coef2)

    return mat


def check_result(result, result_expected):
    is_ok = np.allclose(result, result_expected)
    print("Result check status: " + str(is_ok))

    if not is_ok:
        raise Exception("Result does not match expected result")


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
    MSIZE = int(args[1])
    COEF1 = np.float64(0.5)
    COEF2 = np.float64(0.7)

    # Log arguments if required
    if __debug__:
        print("Running ep application with:")
        print(" - NSIZE = " + str(NSIZE))
        print(" - MSIZE = " + str(MSIZE))
        print(" - COEF1 = " + str(COEF1))
        print(" - COEF2 = " + str(COEF2))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    MAT = initialize_variables(NSIZE, MSIZE)
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    ep_start_time = time.time()
    ep(MAT, NSIZE, MSIZE, COEF1, COEF2)
    compss_barrier(True)
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = ep_start_time - start_time
    fdtd_time = end_time - ep_start_time

    print("RESULTS -----------------")
    print("VERSION AUTOPARALLEL")
    print("NSIZE " + str(NSIZE))
    print("MSIZE " + str(MSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("EP_TIME " + str(fdtd_time))
    print("-------------------------")
