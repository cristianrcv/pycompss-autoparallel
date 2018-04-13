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

def initialize_variables(nx_size, ny_size):
    ex = create_matrix(nx_size, ny_size, nx_size)
    ey = create_matrix(nx_size, ny_size, ny_size)
    hz = create_matrix(nx_size, ny_size, nx_size)

    return ex, ey, hz


def create_matrix(nx_size, ny_size, ref_size):
    mat = []
    for i in range(nx_size):
        mat.append([])
        for j in range(ny_size):
            mb = create_entry(i, j, ref_size)
            mat[i].append(mb)
    return mat


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def create_entry(i, j, size):
    return np.float64(np.float64(i * (j + 1)) / np.float64(size))


############################################
# MAIN FUNCTION
############################################

# [COMPSs Autoparallel] Begin Autogenerated code
import math

from pycompss.api.api import compss_barrier, compss_wait_on, compss_open
from pycompss.api.task import task
from pycompss.api.parameter import *


@task(t=IN, returns=1)
def S1(t):
    return copy_reference(t)


@task(var2=IN, coef1=IN, var3=IN, var4=IN, returns=1)
def S2(var2, coef1, var3, var4):
    return compute_e(var2, coef1, var3, var4)


@task(var2=IN, coef1=IN, var3=IN, var4=IN, returns=1)
def S3(var2, coef1, var3, var4):
    return compute_e(var2, coef1, var3, var4)


@task(var2=IN, coef2=IN, var3=IN, var4=IN, var5=IN, var6=IN, returns=1)
def S4(var2, coef2, var3, var4, var5, var6):
    return compute_h(var2, coef2, var3, var4, var5, var6)


def fdtd_2d(ex, ey, hz, nx_size, ny_size, t_size, coef1, coef2):
    if __debug__:
        ex = compss_wait_on(ex)
        ey = compss_wait_on(ey)
        hz = compss_wait_on(hz)
        print('Matrix Ex:')
        print(ex)
        print('Matrix Ey:')
        print(ey)
        print('Matrix Hz:')
        print(hz)
    if __debug__:
        import copy
        ex_seq = copy.deepcopy(ex)
        ey_seq = copy.deepcopy(ey)
        hz_seq = copy.deepcopy(hz)
        hz_expected = seq_fdtd_2d(ex_seq, ey_seq, hz_seq, nx_size, ny_size,
            t_size, coef1, coef2)
    if ny_size >= 1 and t_size >= 1:
        if nx_size >= 2 and ny_size >= 2:
            ey[0][0] = S1(0)
            lbp = 1
            ubp = nx_size - 1
            for t3 in range(1, nx_size - 1 + 1):
                ey[t3][0] = S2(ey[t3][0], coef1, hz[t3][0], hz[t3 - 1][0])
        if nx_size >= 2 and ny_size == 1:
            lbp = 0
            ubp = 2 * t_size - 2
            for t1 in range(0, 2 * t_size - 2 + 1):
                if t1 % 2 == 0:
                    ey[0][0] = S1(t1 / 2)
                    lbp = int(math.ceil(float(t1 + 2) / float(2)))
                    ubp = int(math.floor(float(t1 + 2 * nx_size - 2) /
                        float(2)))
                    for t3 in range(int(math.ceil(float(t1 + 2) / float(2))
                        ), int(math.floor(float(t1 + 2 * nx_size - 2) /
                        float(2))) + 1):
                        ey[(-t1 + 2 * t3) / 2][0] = S2(ey[(-t1 + 2 * t3) / 
                            2][0], coef1, hz[(-t1 + 2 * t3) / 2][0], hz[(-
                            t1 + 2 * t3) / 2 - 1][0])
        if nx_size == 1 and ny_size >= 2:
            ey[0][0] = S1(0)
        if nx_size == 1 and ny_size == 1:
            lbp = 0
            ubp = 2 * t_size - 2
            for t1 in range(0, 2 * t_size - 2 + 1):
                if t1 % 2 == 0:
                    ey[0][0] = S1(t1 / 2)
        if nx_size <= 0:
            lbp = 0
            ubp = 2 * t_size + ny_size - 3
            for t1 in range(0, 2 * t_size + ny_size - 3 + 1):
                lbp = max(int(math.ceil(float(t1) / float(2))), t1 - t_size + 1
                    )
                ubp = min(int(math.floor(float(t1 + ny_size - 1) / float(2)
                    )), t1)
                for t2 in range(lbp, ubp + 1):
                    ey[0][-t1 + 2 * t2] = S1(t1 - t2)
        if nx_size >= 2 and ny_size >= 2:
            lbp = 1
            ubp = 2 * t_size - 2
            for t1 in range(1, 2 * t_size - 2 + 1):
                if t1 % 2 == 0:
                    ey[0][0] = S1(t1 / 2)
                    lbp = int(math.ceil(float(t1 + 2) / float(2)))
                    ubp = int(math.floor(float(t1 + 2 * nx_size - 2) /
                        float(2)))
                    for t3 in range(int(math.ceil(float(t1 + 2) / float(2))
                        ), int(math.floor(float(t1 + 2 * nx_size - 2) /
                        float(2))) + 1):
                        ey[(-t1 + 2 * t3) / 2][0] = S2(ey[(-t1 + 2 * t3) / 
                            2][0], coef1, hz[(-t1 + 2 * t3) / 2][0], hz[(-
                            t1 + 2 * t3) / 2 - 1][0])
                lbp = int(math.ceil(float(t1 + 1) / float(2)))
                ubp = min(int(math.floor(float(t1 + ny_size - 1) / float(2)
                    )), t1)
                for t2 in range(lbp, ubp + 1):
                    ex[0][-t1 + 2 * t2] = S3(ex[0][-t1 + 2 * t2], coef1, hz
                        [0][-t1 + 2 * t2], hz[0][-t1 + 2 * t2 - 1])
                    ey[0][-t1 + 2 * t2] = S1(t1 - t2)
                    lbp = t1 - t2 + 1
                    ubp = t1 - t2 + nx_size - 1
                    for t3 in range(t1 - t2 + 1, t1 - t2 + nx_size - 1 + 1):
                        ey[-t1 + t2 + t3][-t1 + 2 * t2] = S2(ey[-t1 + t2 +
                            t3][-t1 + 2 * t2], coef1, hz[-t1 + t2 + t3][-t1 +
                            2 * t2], hz[-t1 + t2 + t3 - 1][-t1 + 2 * t2])
                        ex[-t1 + t2 + t3][-t1 + 2 * t2] = S3(ex[-t1 + t2 +
                            t3][-t1 + 2 * t2], coef1, hz[-t1 + t2 + t3][-t1 +
                            2 * t2], hz[-t1 + t2 + t3][-t1 + 2 * t2 - 1])
                        hz[-t1 + t2 + t3 - 1][-t1 + 2 * t2 - 1] = S4(hz[-t1 +
                            t2 + t3 - 1][-t1 + 2 * t2 - 1], coef2, ex[-t1 +
                            t2 + t3 - 1][-t1 + 2 * t2 - 1 + 1], ex[-t1 + t2 +
                            t3 - 1][-t1 + 2 * t2 - 1], ey[-t1 + t2 + t3 - 1 +
                            1][-t1 + 2 * t2 - 1], ey[-t1 + t2 + t3 - 1][-t1 +
                            2 * t2 - 1])
        if nx_size >= 2:
            lbp = 2 * t_size - 1
            ubp = 2 * t_size + ny_size - 3
            for t1 in range(2 * t_size - 1, 2 * t_size + ny_size - 3 + 1):
                lbp = t1 - t_size + 1
                ubp = min(int(math.floor(float(t1 + ny_size - 1) / float(2)
                    )), t1)
                for t2 in range(lbp, ubp + 1):
                    ex[0][-t1 + 2 * t2] = S3(ex[0][-t1 + 2 * t2], coef1, hz
                        [0][-t1 + 2 * t2], hz[0][-t1 + 2 * t2 - 1])
                    ey[0][-t1 + 2 * t2] = S1(t1 - t2)
                    lbp = t1 - t2 + 1
                    ubp = t1 - t2 + nx_size - 1
                    for t3 in range(t1 - t2 + 1, t1 - t2 + nx_size - 1 + 1):
                        ey[-t1 + t2 + t3][-t1 + 2 * t2] = S2(ey[-t1 + t2 +
                            t3][-t1 + 2 * t2], coef1, hz[-t1 + t2 + t3][-t1 +
                            2 * t2], hz[-t1 + t2 + t3 - 1][-t1 + 2 * t2])
                        ex[-t1 + t2 + t3][-t1 + 2 * t2] = S3(ex[-t1 + t2 +
                            t3][-t1 + 2 * t2], coef1, hz[-t1 + t2 + t3][-t1 +
                            2 * t2], hz[-t1 + t2 + t3][-t1 + 2 * t2 - 1])
                        hz[-t1 + t2 + t3 - 1][-t1 + 2 * t2 - 1] = S4(hz[-t1 +
                            t2 + t3 - 1][-t1 + 2 * t2 - 1], coef2, ex[-t1 +
                            t2 + t3 - 1][-t1 + 2 * t2 - 1 + 1], ex[-t1 + t2 +
                            t3 - 1][-t1 + 2 * t2 - 1], ey[-t1 + t2 + t3 - 1 +
                            1][-t1 + 2 * t2 - 1], ey[-t1 + t2 + t3 - 1][-t1 +
                            2 * t2 - 1])
        if nx_size == 1 and ny_size >= 2:
            lbp = 1
            ubp = 2 * t_size - 2
            for t1 in range(1, 2 * t_size - 2 + 1):
                if t1 % 2 == 0:
                    ey[0][0] = S1(t1 / 2)
                lbp = int(math.ceil(float(t1 + 1) / float(2)))
                ubp = min(int(math.floor(float(t1 + ny_size - 1) / float(2)
                    )), t1)
                for t2 in range(lbp, ubp + 1):
                    ex[0][-t1 + 2 * t2] = S3(ex[0][-t1 + 2 * t2], coef1, hz
                        [0][-t1 + 2 * t2], hz[0][-t1 + 2 * t2 - 1])
                    ey[0][-t1 + 2 * t2] = S1(t1 - t2)
        if nx_size == 1:
            lbp = 2 * t_size - 1
            ubp = 2 * t_size + ny_size - 3
            for t1 in range(2 * t_size - 1, 2 * t_size + ny_size - 3 + 1):
                lbp = t1 - t_size + 1
                ubp = min(int(math.floor(float(t1 + ny_size - 1) / float(2)
                    )), t1)
                for t2 in range(lbp, ubp + 1):
                    ex[0][-t1 + 2 * t2] = S3(ex[0][-t1 + 2 * t2], coef1, hz
                        [0][-t1 + 2 * t2], hz[0][-t1 + 2 * t2 - 1])
                    ey[0][-t1 + 2 * t2] = S1(t1 - t2)
    compss_barrier()
    if __debug__:
        hz = compss_wait_on(hz)
        print('New Matrix Hz:')
        print(hz)
    if __debug__:
        check_result(hz, hz_expected)

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


def compute_h(h, coef2, ex2, ex1, ey2, ey1):
    # import time
    # start = time.time()

    return h - coef2 * (ex2 - ex1 + ey2 - ey1)

    # end = time.time()
    # tm = end - start
    # print "TIME: " + str(tm*1000) + " ms"


def copy_reference(elem):
    return elem


############################################
# RESULT CHECK FUNCTIONS
############################################

def seq_fdtd_2d(ex, ey, hz, nx_size, ny_size, t_size, coef1, coef2):
    for t in range(t_size):
        for j in range(ny_size):
            ey[0][j] = t
        for i in range(1, nx_size):
            for j in range(ny_size):
                ey[i][j] -= coef1 * (hz[i][j] - hz[i - 1][j])
        for i in range(nx_size):
            for j in range(1, ny_size):
                ex[i][j] -= coef1 * (hz[i][j] - hz[i][j - 1])
        for i in range(nx_size - 1):
            for j in range(ny_size - 1):
                hz[i][j] -= coef2 * (ex[i][j + 1] - ex[i][j] + ey[i + 1][j] - ey[i][j])

    return hz


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
    NXSIZE = int(args[0])
    NYSIZE = int(args[1])
    TSIZE = int(args[2])
    COEF1 = np.float64(0.5)
    COEF2 = np.float64(0.7)

    # Log arguments if required
    if __debug__:
        print("Running fdtd-2d application with:")
        print(" - NXSIZE = " + str(NXSIZE))
        print(" - NYSIZE = " + str(NYSIZE))
        print(" - TSIZE = " + str(TSIZE))
        print(" - COEF1 = " + str(COEF1))
        print(" - COEF2 = " + str(COEF2))

    # Initialize matrices
    if __debug__:
        print("Initializing matrices")
    start_time = time.time()
    EX, EY, HZ = initialize_variables(NXSIZE, NYSIZE)
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    fdtd_start_time = time.time()
    fdtd_2d(EX, EY, HZ, NXSIZE, NYSIZE, TSIZE, COEF1, COEF2)
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
    print("NXSIZE " + str(NXSIZE))
    print("NYSIZE " + str(NYSIZE))
    print("TSIZE " + str(TSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("FDTD_TIME " + str(fdtd_time))
    print("-------------------------")
