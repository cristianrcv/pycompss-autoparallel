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
from pycompss.api.parameter import *

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


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def create_entry():
    import random
    return np.float64(100 * random.random())


############################################
# MAIN FUNCTION
############################################

# [COMPSs Autoparallel] Begin Autogenerated code
import math

from pycompss.api.api import compss_barrier, compss_wait_on, compss_open
from pycompss.api.task import task
from pycompss.api.parameter import *
from pycompss.util.translators.arg_utils.arg_utils import ArgUtils


@task(lbv=IN, ubv=IN, beta=IN, returns="LT3_args_size")
def LT3(lbv, ubv, beta, *args):
    global LT3_args_size
    var1, = ArgUtils.rebuild_args(args)
    for t3 in range(0, ubv + 1 - lbv):
        var1[t3] = S1_no_task(var1[t3], beta)
    return ArgUtils.flatten_args(var1)


@task(lbv=IN, ubv=IN, alpha=IN, returns="LT4_args_size")
def LT4(lbv, ubv, alpha, *args):
    global LT4_args_size
    var2, var3, var1 = ArgUtils.rebuild_args(args)
    for t4 in range(0, ubv + 1 - lbv):
        var1[t4] = S2_no_task(var1[t4], alpha, var2[t4], var3[t4])
    return ArgUtils.flatten_args(var1)


@task(var2=IN, beta=IN, returns=1)
def S1(var2, beta):
    return scale(var2, beta)


def S1_no_task(var2, beta):
    return scale(var2, beta)


@task(var2=IN, alpha=IN, var3=IN, var4=IN, returns=1)
def S2(var2, alpha, var3, var4):
    return multiply(var2, alpha, var3, var4)


def S2_no_task(var2, alpha, var3, var4):
    return multiply(var2, alpha, var3, var4)


def matmul(a, b, c, m_size, alpha, beta):
    if __debug__:
        a = compss_wait_on(a)
        b = compss_wait_on(b)
        c = compss_wait_on(c)
        print('Matrix A:')
        print(a)
        print('Matrix B:')
        print(b)
        print('Matrix C:')
        print(c)
    if __debug__:
        import copy
        input_a = copy.deepcopy(a)
        input_b = copy.deepcopy(b)
        input_c = copy.deepcopy(c)
        res_expected = seq_multiply(input_a, input_b, input_c, m_size, alpha, beta)
    if m_size >= 1:
        lbp = 0
        ubp = m_size - 1
        for t2 in range(lbp, ubp + 1):
            lbv = 0
            ubv = m_size - 1
            LT3_aux_0 = [c[t3][t2] for t3 in range(lbv, ubv + 1)]
            LT3_argutils = ArgUtils()
            global LT3_args_size
            LT3_flat_args, LT3_args_size = LT3_argutils.flatten(1, LT3_aux_0, LT3_aux_0)
            LT3_new_args = LT3(lbv, ubv, beta, *LT3_flat_args)
            LT3_aux_0, = LT3_argutils.rebuild(LT3_new_args)
            LT3_index = 0
            for t3 in range(lbv, ubv + 1):
                c[t3][t2] = LT3_aux_0[LT3_index]
                LT3_index = LT3_index + 1
        lbp = 0
        ubp = m_size - 1
        for t2 in range(lbp, ubp + 1):
            lbp = 0
            ubp = m_size - 1
            for t3 in range(0, m_size - 1 + 1):
                lbv = 0
                ubv = m_size - 1
                LT4_aux_0 = [a[t4][t3] for t4 in range(lbv, ubv + 1)]
                LT4_aux_1 = [b[t3][t2] for t4 in range(lbv, ubv + 1)]
                LT4_aux_2 = [c[t4][t2] for t4 in range(lbv, ubv + 1)]
                LT4_argutils = ArgUtils()
                global LT4_args_size
                LT4_flat_args, LT4_args_size = LT4_argutils.flatten(3, LT4_aux_0, LT4_aux_1, LT4_aux_2, LT4_aux_2)
                LT4_new_args = LT4(lbv, ubv, alpha, *LT4_flat_args)
                LT4_aux_2, = LT4_argutils.rebuild(LT4_new_args)
                LT4_index = 0
                for t4 in range(lbv, ubv + 1):
                    c[t4][t2] = LT4_aux_2[LT4_index]
                    LT4_index = LT4_index + 1
    compss_barrier()
    if __debug__:
        c = compss_wait_on(c)
        print('New Matrix C:')
        print(c)
    if __debug__:
        check_result(c, res_expected)

# [COMPSs Autoparallel] End Autogenerated code


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

    return c + alpha * a * b

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


############################################
# RESULT CHECK FUNCTIONS
############################################

def seq_multiply(a, b, c, m_size, alpha, beta):
    for i in range(m_size):
        for j in range(m_size):
            c[i][j] *= beta
        for k in range(m_size):
            for j in range(m_size):
                c[i][j] += alpha * a[i][k] * b[k][j]

    return c


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
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    mult_start_time = time.time()
    matmul(A, B, C, MSIZE, ALPHA, BETA)
    compss_barrier(True)
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = mult_start_time - start_time
    mult_time = end_time - mult_start_time

    print("RESULTS -----------------")
    print("VERSION AUTOPARALLEL")
    print("MSIZE " + str(MSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("MULT_TIME " + str(mult_time))
    print("-------------------------")
