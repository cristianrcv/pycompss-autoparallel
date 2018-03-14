#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from pycompss.api.constraint import constraint
from pycompss.api.task import task
from pycompss.api.parameter import *
from pycompss.api.api import compss_barrier, compss_wait_on

import numpy as np


def generate_matrix():
    for i in range(MSIZE):
        A.append([])
        for j in range(MSIZE):
            mb = create_block(BSIZE)
            A[i].append(mb)


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def create_block(b_size):
    import numpy as np

    block = np.array(np.random.random((b_size, b_size)), dtype=np.double, copy=False)
    mb = np.matrix(block, dtype=np.double, copy=False)
    return mb


def lu_blocked():
    # Debug
    if __debug__:
        input_a = compss_wait_on(A)
        print("Matrix A:")
        print(input_a)

    p_mat = [[np.matrix(np.zeros((BSIZE, BSIZE)), dtype=float)] * MSIZE for _ in range(MSIZE)]
    l_mat = [[None] * MSIZE for _ in range(MSIZE)]
    u_mat = [[None] * MSIZE for _ in range(MSIZE)]

    for i in range(len(A)):
        for j in range(i + 1, len(A)):
            l_mat[i][j] = np.matrix(np.zeros((BSIZE, BSIZE)), dtype=float)
            u_mat[j][i] = np.matrix(np.zeros((BSIZE, BSIZE)), dtype=float)

    if len(A) == 0:
        return

    p_mat[0][0], l_mat[0][0], u_mat[0][0] = custom_lu(A[0][0])

    for j in range(1, MSIZE):
        aux = invert_triangular(l_mat[0][0], lower=True)
        u_mat[0][j] = multiply([1], aux, p_mat[0][0], A[0][j])

    for i in range(1, MSIZE):
        for j in range(i, MSIZE):
            for k in range(i, MSIZE):
                aux = invert_triangular(u_mat[i - 1][i - 1], lower=False)
                A[j][k] = dgemm(-1, A[j][k], multiply([], A[j][i - 1], aux), u_mat[i - 1][k])

        p_mat[i][i], l_mat[i][i], u_mat[i][i] = custom_lu(A[i][i])

        for j in range(0, i):
            aux = invert_triangular(u_mat[j][j], lower=False)
            l_mat[i][j] = multiply([0], p_mat[i][i], A[i][j], aux)

        for j in range(i + 1, MSIZE):
            invert_triangular(l_mat[i][i], lower=True)
            u_mat[i][j] = multiply([1], aux, p_mat[i][i], A[i][j])

    # Debug result
    if __debug__:
        p_res = join_matrix(compss_wait_on(p_mat))
        l_res = join_matrix(compss_wait_on(l_mat))
        u_res = join_matrix(compss_wait_on(u_mat))

        print("Matrix P:")
        print(p_res)
        print("Matrix L:")
        print(l_res)
        print("Matrix U:")
        print(u_res)


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def invert_triangular(a, lower=False):
    import numpy as np
    from scipy.linalg import solve_triangular

    dim = len(a)
    identity = np.matrix(np.identity(dim))
    return solve_triangular(A, identity, lower=lower)


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def multiply(inv_list, *args):
    import numpy as np

    # Base case checks
    assert (len(args) > 0)
    input_args = list(args)
    if len(input_args) == 1:
        return input_args[0]

    # Complex cases
    if len(inv_list) > 0:
        from numpy.linalg import inv
        for elem in inv_list:
            input_args[elem] = inv(args[elem])

    result = np.dot(input_args[0], input_args[1])
    for i in range(2, len(input_args)):
        result = np.dot(result, input_args[i])

    return result


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=1)
def dgemm(alpha, a, b, c):
    import numpy as np

    a += (alpha * np.dot(b, c))

    return a


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=(np.ndarray, np.ndarray, np.ndarray))
def custom_lu(a):
    from scipy.linalg import lu
    return lu(a)


def join_matrix(mat):
    joint_matrix = np.matrix([[]])
    for i in range(0, len(mat)):
        current_row = mat[i][0]
        for j in range(1, len(mat[i])):
            current_row = np.bmat([[current_row, mat[i][j]]])
        if i == 0:
            joint_matrix = current_row
        else:
            joint_matrix = np.bmat([[joint_matrix], [current_row]])

    return np.matrix(joint_matrix)


if __name__ == "__main__":
    # Import libraries
    import time

    # Parse arguments
    import sys

    args = sys.argv[1:]
    MSIZE = int(args[0])
    BSIZE = int(args[1])
    A = []

    # Log arguments if required
    if __debug__:
        print("Running LU application with:")
        print(" - MSIZE = " + str(MSIZE))
        print(" - BSIZE = " + str(BSIZE))

    # Initialize matrix
    if __debug__:
        print("Initializing matrix")
    start_time = time.time()
    generate_matrix()
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    lu_start_time = time.time()
    lu_blocked()
    compss_barrier()
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = lu_start_time - start_time
    lu_time = end_time - lu_start_time

    print("RESULTS -----------------")
    print("MSIZE " + str(MSIZE))
    print("BSIZE " + str(MSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("LU_TIME " + str(lu_time))
    print("-------------------------")
