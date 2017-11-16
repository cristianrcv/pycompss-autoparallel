#!/usr/bin/python                                                                                                                                                                                                                                                              
# -*- coding: utf-8 -*-

# Decorator definition
def parallel(func):
        # Get the source code of the function
        import inspect
        print inspect.getsource(func)

        # Add folder structure to python path
        # This should not be required since all of them will be declared as modules
        import sys
        import os
        sys.path.insert(0, os.getcwd() + '/../../translators/python2scop')
        sys.path.insert(0, os.getcwd() + '/../../translators/scop2python')
        sys.path.insert(0, os.getcwd() + '/../../translators/python2pycompss')

        # Process python code to scop and parallelize it
        from matmul_scop import matmul as matmul_scop
        print inspect.getsource(matmul_scop)

        # Process scop code back to python
        from matmul_parallel import matmul as matmul_parallel
        print inspect.getsource(matmul_parallel)

        # Translate parallel code to PyCOMPSs
        from matmul_pycompss import matmul as matmul_pycompss
        print inspect.getsource(matmul_pycompss)

        return matmul_pycompss

