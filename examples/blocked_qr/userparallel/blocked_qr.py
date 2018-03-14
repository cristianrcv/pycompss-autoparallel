#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from pycompss.api.constraint import constraint
from pycompss.api.task import task
from pycompss.api.api import compss_barrier, compss_wait_on


# TODO: Extend for non-square matrices. There is no size verifications.


def generate_matrix(block_type='random'):
    mat = []
    for i in range(MSIZE):
        mat.append([])
        for j in range(MSIZE):
            mat[i].append(create_block_wrapper(block_type))
    return mat


def generate_identity():
    mat = []
    for i in range(MSIZE):
        mat.append([])
        for j in range(0, i):
            mat[i].append(create_block_wrapper(block_type='zeros'))
        mat[i].append(create_block_wrapper(block_type='identity'))
        for j in range(i + 1, MSIZE):
            mat[i].append(create_block_wrapper(block_type='zeros'))
    return mat


def create_block_wrapper(block_type='random'):
    if block_type == 'zeros':
        block = []
    elif block_type == 'identity':
        block = []
    else:
        block = create_block(BSIZE)
    return [block_type, block]


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def create_block(b_size):
    import numpy as np
    return np.matrix(np.random.random((b_size, b_size)), dtype=np.double, copy=False)


def qr_blocked(overwrite_a=False):
    import numpy as np

    # Debug
    if __debug__:
        input_a = compss_wait_on(A)
        print("Matrix A:")
        print(input_a)

    q_mat = generate_identity()

    if not overwrite_a:
        r_mat = copy_blocked()
    else:
        r_mat = A

    for i in range(MSIZE):
        q_act, r_mat[i][i] = qr(r_mat[i][i], BSIZE, transpose=True)

        for j in range(MSIZE):
            q_mat[j][i] = dot(q_mat[j][i], q_act, transpose_b=True)

        for j in range(i + 1, MSIZE):
            r_mat[i][j] = dot(q_act, r_mat[i][j])

        # Update values of the respective column
        for j in range(i + 1, MSIZE):
            sub_q = [[np.matrix(np.array([0])), np.matrix(np.array([0]))],
                     [np.matrix(np.array([0])), np.matrix(np.array([0]))]]
            sub_q[0][0], sub_q[0][1], sub_q[1][0], sub_q[1][1], r_mat[i][i], r_mat[j][i] = little_qr(r_mat[i][i],
                                                                                                     r_mat[j][i], BSIZE,
                                                                                                     transpose=True)
            # sub_q = blocked_transpose(sub_q)
            # Update values of the row for the value updated in the column
            for k in range(i + 1, MSIZE):
                [[r_mat[i][k]], [r_mat[j][k]]] = multiply_blocked(sub_q, [[r_mat[i][k]], [r_mat[j][k]]], BSIZE)

            for k in range(MSIZE):
                [[q_mat[k][i], q_mat[k][j]]] = multiply_blocked([[q_mat[k][i], q_mat[k][j]]], sub_q, BSIZE,
                                                                transpose_b=True)

    # q_mat = blocked_transpose(q_mat)

    # Debug result
    if __debug__:
        q_res = join_matrix(compss_wait_on(q_mat), BSIZE)
        r_res = join_matrix(compss_wait_on(r_mat), BSIZE)

        print("Matrix Q:")
        print(q_res)
        print("Matrix R:")
        print(r_res)


def copy_blocked(transpose=False):
    import numpy as np

    res = []
    for i in range(len(A)):
        res.append([])
        for j in range(len(A[0])):
            res[i].append(np.matrix([0]))
    for i in range(len(A)):
        for j in range(len(A[0])):
            if transpose:
                res[j][i] = A[i][j]
            else:
                res[i][j] = [A[i][j][0], A[i][j][1]]
    return res


def qr(mat, b_size, mode='reduced', transpose=False):
    q_aux, r_aux = qr_task(mat[1], b_size, mat[0], mode=mode, transpose=transpose)
    return ['random', q_aux], ['random', r_aux]


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=(list, list))
def qr_task(mat, b_size, block_type, mode='reduced', transpose=False):
    import numpy as np
    from numpy.linalg import qr

    if block_type == 'random':
        q_mat, r_mat = qr(mat, mode=mode)
    elif block_type == 'zeros':
        q_mat, r_mat = qr(np.matrix(np.zeros((b_size, b_size))), mode=mode)
    else:
        q_mat, r_mat = qr(np.matrix(np.identity(b_size)), mode=mode)
    if transpose:
        q_mat = np.transpose(q_mat)
    return q_mat, r_mat


def dot(a, b, transpose_result=False, transpose_b=False):
    if a[0] == 'zeros':
        return ['zeros', []]
    if a[0] == 'identity':
        if transpose_b and transpose_result:
            return b
        if transpose_b or transpose_result:
            return transpose_block(b)
        return b

    if b[0] == 'zeros':
        return ['zeros', []]
    if b[0] == 'identity':
        if transpose_result:
            return transpose_block(a)
        return a

    return ['random', dot_task(a[1], b[1], transpose_result=transpose_result, transpose_b=transpose_b)]


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def dot_task(a, b, transpose_result=False, transpose_b=False):
    import numpy as np

    if transpose_b:
        b = np.transpose(b)
    if transpose_result:
        return np.transpose(np.dot(a, b))
    return np.dot(a, b)


def transpose_block(a):
    if a[0] == 'zeros' or a[0] == 'identity':
        return a
    return ['random', transpose_block_task(a[1])]


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=list)
def transpose_block_task(mat):
    import numpy as np

    return np.transpose(mat)


def little_qr(a, b, b_size, transpose=False):
    sub_q00, sub_q01, sub_q10, sub_q11, aa, bb = little_qr_task(a[1], a[0], b[1], b[0], b_size, transpose)
    return ['random', sub_q00], ['random', sub_q01], ['random', sub_q10], ['random', sub_q11], ['random', aa], [
        'random', bb]


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=(list, list, list, list, list, list))
def little_qr_task(a_mat, a_block_type, b_mat, b_block_type, b_size, transpose=False):
    import numpy as np

    ent_a = [a_block_type, a_mat]
    ent_b = [b_block_type, b_mat]
    for mat in [ent_a, ent_b]:
        if mat[0] == 'zeros':
            mat[1] = np.matrix(np.zeros((b_size, b_size)))
        elif mat[1] == 'identity':
            mat[1] = np.matrix(np.identity(b_size))
    curr_a = np.bmat([[ent_a[1]], [ent_b[1]]])
    (sub_q, sub_r) = np.linalg.qr(curr_a, mode='complete')
    aa = sub_r[0:b_size]
    bb = sub_r[b_size:2 * b_size]
    sub_q = split_matrix(sub_q, 2)
    if transpose:
        return np.transpose(sub_q[0][0]), np.transpose(sub_q[1][0]), np.transpose(sub_q[0][1]), np.transpose(
            sub_q[1][1]), aa, bb
    else:
        return sub_q[0][0], sub_q[0][1], sub_q[1][0], sub_q[1][1], aa, bb


def multiply_blocked(a, b, b_size, transpose_b=False):
    if transpose_b:
        b_new = []
        for i in range(len(b[0])):
            b_new.append([])
            for j in range(len(b)):
                b_new[i].append(b[j][i])
        b = b_new
    c_mat = []
    for i in range(len(a)):
        c_mat.append([])
        for j in range(len(b[0])):
            c_mat[i].append(['zeros', []])
            for k in range(len(a[0])):
                c_mat[i][j] = multiply_single_block(a[i][k], b[k][j], c_mat[i][j], b_size, transpose_b=transpose_b)
    return c_mat


def multiply_single_block(a, b, c, b_size, transpose_b=False):
    if a[0] == 'zeros' or b[0] == 'zeros':
        return c
    c[1] = multiply_single_block_task(a[1], a[0], b[1], b[0], c[1], c[0], b_size, transpose_b=transpose_b)
    c = ['random', c[1]]
    return c


@constraint(ComputingUnits="${ComputingUnits}")
@task(returns=(list))
def multiply_single_block_task(a_mat, a_block_type, b_mat, b_block_type, c_mat, c_block_type, b_size,
                               transpose_b=False):
    import numpy as np

    a_fun = [a_block_type, a_mat]
    b_fun = [b_block_type, b_mat]
    if c_block_type == 'zeros':
        c_mat = np.matrix(np.zeros((b_size, b_size)))
    elif c_block_type == 'identity':
        c_mat = np.matrix(np.identity(b_size))

    if a_fun[0] == 'identity':
        if b_fun[0] == 'identity':
            b_fun[1] = np.matrix(np.identity(b_size))
        if transpose_b:
            aux = np.transpose(b_fun[1])
        else:
            aux = b_fun[1]
        c_mat += aux
        return c_mat

    if b_fun[0] == 'identity':
        c_mat += a_fun[1]
        return c_mat
    if transpose_b:
        b_fun[1] = np.transpose(b_fun[1])
    c_mat += (a_fun[1] * b_fun[1])

    return c_mat


def split_matrix(mat, m_size):
    import numpy as np

    splitted_matrix = []
    b_size = len(mat) / m_size
    splitted_matrix = [[None for _ in range(m_size)] for _ in range(m_size)]
    for i in range(m_size):
        for j in range(m_size):
            splitted_matrix[i][j] = np.matrix(mat[i * b_size:(i + 1) * b_size, j * b_size:(j + 1) * b_size])
    return splitted_matrix


def blocked_transpose(mat):
    import numpy as np

    res = []
    for i in range(len(mat)):
        res.append([])
        for j in range(len(mat[0])):
            res[i].append(['random', np.matrix([0])])
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            res[j][i] = transpose_block(mat[i][j])
    return res


def join_matrix(mat, b_size):
    import numpy as np

    joint_matrix = np.matrix([[]])
    for i in range(0, len(mat)):
        if mat[i][0][0] == 'zeros':
            mat[i][0][1] = np.matrix(np.zeros((b_size, b_size)))
        elif mat[i][0][0] == 'identity':
            mat[i][0][1] = np.matrix(np.identity(b_size))
        current_row = mat[i][0][1]
        for j in range(1, len(mat[i])):
            if mat[i][j][0] == 'zeros':
                mat[i][j][1] = np.matrix(np.zeros((b_size, b_size)))
            elif mat[i][j][0] == 'identity':
                mat[i][j][1] = np.matrix(np.identity(b_size))
            current_row = np.bmat([[current_row, mat[i][j][1]]])
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

    # Log arguments if required
    if __debug__:
        print("Running QR application with:")
        print(" - MSIZE = " + str(MSIZE))
        print(" - BSIZE = " + str(BSIZE))

    # Initialize matrix
    if __debug__:
        print("Initializing matrix")
    start_time = time.time()
    A = generate_matrix()
    compss_barrier()

    # Begin computation
    if __debug__:
        print("Performing computation")
    qr_start_time = time.time()
    qr_blocked()
    compss_barrier()
    end_time = time.time()

    # Log results and time
    if __debug__:
        print("Post-process results")
    total_time = end_time - start_time
    init_time = qr_start_time - start_time
    qr_time = end_time - qr_start_time

    print("RESULTS -----------------")
    print("MSIZE " + str(MSIZE))
    print("BSIZE " + str(MSIZE))
    print("DEBUG " + str(__debug__))
    print("TOTAL_TIME " + str(total_time))
    print("INIT_TIME " + str(init_time))
    print("QR_TIME " + str(qr_time))
    print("-------------------------")
