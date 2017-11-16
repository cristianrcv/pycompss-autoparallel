#!/usr/bin/python
# -*- coding: utf-8 -*-

# Decorator definition
def parallel(func):
        # Get the source code of the function
        import inspect
        print "INSPECTED USER FUNCTION BY DECORATOR"
        print inspect.getsource(func)

        import os

        # Process python code to scop
        matmul_scop = os.getcwd() + '/../../translators/python2scop/out.scop'
        print "GENERATED SCOP CODE"
        with open(matmul_scop, 'r') as fin:
                    print fin.read()

        # Parallelize SCOP code
        print "GENERATED PARALLEL SCOP CODE"
        # TODO: Add a PLUTO call to parallelize the SCOP code

        # Process scop code back to python
        matmul_parallel = os.getcwd() + '/../../translators/scop2python/out.c'
        print "GENERATED PARALLEL PYTHON CODE"
        with open(matmul_parallel, 'r') as fin:
                 print fin.read()

        # Add folder structure to python path
        # This should not be required since all of them will be declared as modules
        import sys
        sys.path.insert(0, os.getcwd() + '/../../translators/python2pycompss')
        # Translate parallel code to PyCOMPSs
        from matmul_pycompss import matmul as matmul_pycompss
        print "GENERATED COMPSS PYTHON CODE"
        print inspect.getsource(matmul_pycompss)

        # Execute parallelized code
        return matmul_pycompss

