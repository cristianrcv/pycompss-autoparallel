#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from pycompss.api.constraint import constraint
from pycompss.api.task import task
from pycompss.api.api import compss_barrier, compss_wait_on


def generate_matrix():
    for i in range(MSIZE):
        A.append([])
        for _ in range(MSIZE):
            A[i].append([])

    for i in range(MSIZE):
        mb = create_block(BSIZE, True)
        A[i][i] = mb
        for j in range(i + 1, MSIZE):
            mb = create_block(BSIZE, False)
            A[i][j] = mb
            A[j][i] = mb


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def create_block(b_size, is_diag):
    import numpy as np

    block = np.array(np.random.random((b_size, b_size)), dtype=np.double, copy=False)
    mb = np.matrix(block, dtype=np.double, copy=False)
    mb = mb + np.transpose(mb)
    if is_diag:
        mb = mb + 2 * b_size * np.eye(b_size)
    return mb


def cholesky_blocked():
    import numpy as np

    # Debug
    if __debug__:
        input_a = compss_wait_on(A)
        print("Matrix A:")
        print(input_a)

    # Debug: task counter
    cont = 0

    # Cholesky decomposition
    for k in range(MSIZE):
        # Diagonal block factorization
        A[k][k] = potrf(A[k][k])
        if __debug__:
            cont += 1
        # Triangular systems
        for i in range(k + 1, MSIZE):
            A[i][k] = solve_triangular(A[k][k], A[i][k])
            A[k][i] = np.zeros((BSIZE, BSIZE))
            if __debug__:
                cont += 1

        # update trailing matrix
        for i in range(k + 1, MSIZE):
            for j in range(i, MSIZE):
                A[j][i] = gemm(-1.0, A[j][k], A[i][k], A[j][i], 1.0)
                if __debug__:
                    cont += 1
            # TODO: Why not called? Counter?
            # A[j][i] = syrk(A[j][k], A[j][i])
            if __debug__:
                cont += 1

    # Debug: task counter
    if __debug__:
        print("Number of spawned tasks: " + str(cont))

    # Debug result
    if __debug__:
        res = compss_wait_on(A)
        res = join_matrix(res)
        print("New Matrix A:")
        print(res)


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def potrf(a):
    from scipy.linalg.lapack import dpotrf
    a = dpotrf(a, lower=True)[0]
    return a


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def solve_triangular(a, b):
    from scipy.linalg import solve_triangular
    from numpy import transpose

    b = transpose(b)
    b = solve_triangular(a, b, lower=True)
    b = transpose(b)
    return b


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def gemm(alpha, a, b, c, beta):
    from scipy.linalg.blas import dgemm
    from numpy import transpose

    b = transpose(b)
    c = dgemm(alpha, a, b, c=c, beta=beta)
    return c


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def syrk(a, b):
    from scipy.linalg.blas import dsyrk

    alpha = -1.0
    beta = 1.0
    b = dsyrk(alpha, a, c=b, beta=beta, lower=True)
    return b


def join_matrix(a):
    import numpy as np

    joint_matrix = np.matrix([[]])
    for i in range(0, len(a)):
        current_row = a[i][0]
        for j in range(1, len(a[i])):
            current_row = np.bmat([[current_row, a[i][j]]])
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
        print("Running cholesky application with:")
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
    cholesky_start_time = time.time()
    cholesky_blocked()
    compss_barrier()
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = cholesky_start_time - start_time
    cholesky_time = end_time - cholesky_start_time

    print("RESULTS -----------------")
    print("MSIZE " + str(MSIZE))
    print("BSIZE " + str(MSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("CHOLESKY_TIME " + str(cholesky_time))
    print("-------------------------")
