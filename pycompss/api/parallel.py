#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest
import logging
from functools import wraps


#
# Logger definition
#

logger = logging.getLogger(__name__)


#
# Decorator definition
#

class parallel(object):
        """
        Activates with the @parallel decorator and modifies the user code to make it
        parallel. Preserves the argspec, but includes the __init__ and the
        __call__ methods.
        """

        def __init__(self, *args, **kwargs):
                # Store arguments passed to the decorator
                self.args = args
                self.kwargs = kwargs
                logger.debug("Init @parallel decorator...")

        def __call__(self, func):
                if __debug__:
                        logger.debug("[decorator] Start decorator for function: " + str(func))

                new_func = func
                try:
                        # Get the source code of the function
                        func_source = self._get_py(func)
                        if __debug__:
                                logger.debug("[decorator] Func source code")
                                # logger.debug(str(func_source))

                        # Process python code to scop
                        scop_file = ".tmp_gen_scop.scop"
                        self._py2scop(func_source, scop_file)
                        if __debug__:
                                logger.debug("[decorator] Generated OpenScop content")
                                # with open(scop_file, 'r') as f:
                                #         logger.debug(f.read())

                        # Parallelize OpenScop code and process it back to python
                        py_file = ".tmp_gen_parallel.py"
                        self._scop2pscop2py(scop_file, py_file)
                        if __debug__:
                                logger.debug("[decorator] Generated Parallel Python content")
                                # with open(py_file, 'r') as f:
                                #        logger.debug(f.read())

                        # Add PyCOMPSs annotations
                        pycompss_file = ".tmp_gen_pycompss.py"
                        self._py2pycompss(func_source, py_file, pycompss_file)
                        if __debug__:
                                logger.debug("[decorator] Generated PyCOMPSs content")
                                # with open(pycompss_file, 'r') as f:
                                #        logger.debug(f.read())

                        # Embed code into user file
                        new_func = self._load_generated_code(func, pycompss_file)
                except Exception as e:
                        logger.error(e)
                        raise
                finally:
                        # Clean
                        files_to_clean = []
                        if 'scop_file' in locals():
                                files_to_clean.append(scop_file)
                        if 'py_file' in locals():
                                files_to_clean.append(py_file)
                        if 'pycompss_file' in locals():
                                files_to_clean.append(pycompss_file)
                        self._clean(files_to_clean)

                # Execute parallelized code
                logger.debug("[decorator] Replaced " + str(func) + " by " + str(new_func))

                @wraps(new_func)
                def parallel_f(*args, **kwargs):
                        # This is executed only when called.
                        logger.debug("Executing parallel_f wrapper")

                        if len(args) > 0:
                                # The 'self' for a method function is passed as args[0]
                                slf = args[0]

                                # Replace and store the attributes
                                saved = {}
                                for k, v in self.kwargs.items():
                                        if hasattr(slf, k):
                                                saved[k] = getattr(slf, k)
                                                setattr(slf, k, v)

                        # Call the method
                        if __debug__:
                                logger.debug("Calling user method")
                        ret = new_func(*args, **kwargs)

                        # Put things back
                        if len(args) > 0:
                                for k, v in saved.items():
                                        setattr(slf, k, v)

                        # Restore user code (according to code_replacer)
                        if __debug__:
                                logger.debug("Restoring user code")
                        try:
                                import inspect
                                original_file = inspect.getfile(new_func)
                                import os
                                bkp_file = os.path.splitext(original_file)[0] + "_bkp.py"
                                from shutil import copyfile
                                copyfile(bkp_file, original_file)

                                os.remove(bkp_file)
                        except Exception as e:
                                logger.error(e)
                                raise

                        return ret
                parallel_f.__doc__ = new_func.__doc__
                return parallel_f

        def _get_py(self, func):
                """
                Returns the source code of the given function

                Arguments:
                        - func : Function
                Return:
                        - func_source : Source code of the function
                Raise:
                        - GetPyException
                """

                if __debug__:
                        logger.debug("[decorator] Start get_py")

                from pycompss.util.translators.code_loader.code_loader import CodeLoader
                func_source = CodeLoader.load(func)

                # Finish
                if __debug__:
                        logger.debug("[decorator] Finished get_py")
                return func_source

        def _py2scop(self, source, output):
                """
                Inputs a Python code with scop pragmas and outputs its
                openscop representation in the given file

                Arguments:
                        source : Python code with scop prgramas
                        output : OpenScop output file path
                Return:
                Raise:
                        - Py2ScopException
                """

                if __debug__:
                        logger.debug("[decorator] Start py2scop")

                from pycompss.util.translators.py2scop.translator_py2scop import Py2Scop
                Py2Scop.translate(source, output)

                # Finish
                if __debug__:
                        logger.debug("[decorator] Finished py2scop")

        def _scop2pscop2py(self, source, output):
                """
                Inputs an OpenScop representation to PLUTO that generates
                its parallel version in Python

                Arguments:
                        - source : OpenScop source file path
                        - output : Python output file path
                Return:
                Raise:
                        - Scop2PScop2PyException
                """

                if __debug__:
                        logger.debug("[decorator] Start scop2pscop2py")

                from pycompss.util.translators.scop2pscop2py.translator_scop2pscop2py import Scop2PScop2Py
                Scop2PScop2Py.translate(source, output)

                # Finish
                if __debug__:
                        logger.debug("[decorator] Finished scop2pscop2py")

        def _py2pycompss(self, func_source, source, output):
                """
                Inputs a Python code with parallel annotations and outputs its
                PyCOMPSs code

                Arguments:
                        - func_source : Python original function
                        - source : Python with parallel annotations file path
                        - output : PyCOMPSs file path
                Return:
                        - error : Non-zero value if an error is found, 0 otherwise
                Raise:
                        - Py2PyCOMPSsException
                """

                if __debug__:
                        logger.debug("[decorator] Start py2pycompss")

                from pycompss.util.translators.py2pycompss.translator_py2pycompss import Py2PyCOMPSs
                Py2PyCOMPSs.translate(func_source, source, output)

                # Finish
                if __debug__:
                        logger.debug("[decorator] Finished py2pycompss")

        def _load_generated_code(self, func, new_code):
                """
                Replaces the func code by the content of new_code

                Arguments:
                        - func : function to be replaced
                        - new_code : File path containing the new code
                Return:
                        - new_func : pointer to the new function
                Raise:
                        - LoadGeneratedCodeException
                """

                if __debug__:
                        logger.debug("[decorator] Start load_generated_code")

                from pycompss.util.translators.code_replacer.code_replacer import CodeReplacer
                new_func = CodeReplacer.replace(func, new_code)

                # Finish
                if __debug__:
                        logger.debug("[decorator] Finished load_generated_code")
                return new_func

        def _clean(self, list_of_files):
                """
                Cleans intermediate files

                Arguments:
                        - list_of_files : List of files
                Return:
                """

                if __debug__:
                        logger.debug("[decorator] Cleaning...")

                import os
                for file in list_of_files:
                        if __debug__:
                                logger.debug("[decorator] Cleaning file " + str(file))
                        os.remove(file)

                if __debug__:
                        logger.debug("[decorator] Finished cleaning")


#
# UNIT TEST CASES
#

class TestParallelDecorator(unittest.TestCase):

        def test_decorator(self):
                pass


#
# MAIN FOR UNIT TEST
#

if __name__ == '__main__':
        unittest.main()
