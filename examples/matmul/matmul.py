#!/usr/bin/python
# -*- coding: utf-8 -*-

# Initializes a matrix with size (n x m) with blocks (bSize x bSize) randomly or not
def initialize(n, m, bSize, random):
        import numpy as np

        matrix = []
        for i in range(n):
                matrix.append([])
                for j in range(m):
                        if random:
                                block = np.array(np.random.random((bSize, bSize)), dtype=np.double, copy=False)
                        else:
                                block = np.array(np.zeros((bSize, bSize)), dtype=np.double, copy=False)
                        mb = np.matrix(block, dtype=np.double, copy=False)
                        matrix[i].append(mb)
        return matrix

# Performs the matrix multiplication by blocks
from pycompss.api.parallel import parallel
@parallel
def matmul(mSize, nSize, kSize, bSize, debug):
        # Initialize
        a = initialize(mSize, nSize, bSize, True)
        b = initialize(nSize, kSize, bSize, True)
        c = initialize(mSize, kSize, bSize, False)

        # Debug
        if debug:
                print "Matrix A:"
                print a
	        print "Matrix B:"
                print b
                print "Matrix C:"
                print c

        # Perform computation
        # c = a*b
        for i in range(mSize):
                for j in range(kSize):
                        for k in range(nSize):
                                c[i][j] += a[i][k] * b[k][j]

        # Debug
        if debug:
                print "Matrix C:"
	        print c

        # Result
        return c


# MAIN CODE
if __name__ == "__main__":
        # Import libraries
        import time

        # Parse arguments
        mSize = 5
        nSize = 2
        kSize = 3
        bSize = 1
        debug = True

        # Begin computation
        startTime = time.time()
        result = matmul(mSize, nSize, kSize, bSize, debug)
        endTime = time.time()

        # Log results and time
        print "Ellapsed Time {} (s)".format(endTime - startTime)

