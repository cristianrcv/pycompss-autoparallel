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
                        base_scop_file = ".tmp_gen_scop.scop"
                        scop_files = self._py2scop(func, base_scop_file)
                        if __debug__:
                                logger.debug("[decorator] Generated OpenScop content")
                                # for scop_file in scop_files:
                                #       with open(scop_file, 'r') as f:
                                #               logger.debug(f.read())

                        # Parallelize each OpenScop code and process it back to python
                        base_py_file = ".tmp_gen_parallel.py"
                        py_files = self._scop2pscop2py(scop_files, base_py_file)
                        if __debug__:
                                logger.debug("[decorator] Generated Parallel Python content")
                                # for py_file in py_files:
                                #       with open(py_file, 'r') as f:
                                #               logger.debug(f.read())

                        # Merges and adds PyCOMPSs annotations
                        pycompss_file = ".tmp_gen_pycompss.py"
                        self._py2pycompss(func_source, py_files, pycompss_file)
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
                        if 'scop_files' in locals():
                                for f in scop_files:
                                        files_to_clean.append(f)
                        if 'py_files' in locals():
                                for f in py_files:
                                        files_to_clean.append(f)
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

        def _py2scop(self, func, base_output):
                """
                Inputs a Python function and outputs a OpenScop representation for
                each loop block found in the code. Output files are generated from
                the base_output file name and appending the loop block id

                Arguments:
                        func : Python function to translate
                        base_output : OpenScop output base file path
                Return:
                        output_files : List of file names of the OS generated files
                Raise:
                        - Py2ScopException
                """

                if __debug__:
                        logger.debug("[decorator] Start py2scop")

                from pycompss.util.translators.py2scop.translator_py2scop import Py2Scop
                translator = Py2Scop(func)
                output_files = translator.translate(base_output)

                # Finish
                if __debug__:
                        logger.debug("[decorator] Finished py2scop")

                return output_files

        def _scop2pscop2py(self, scop_files, base_output):
                """
                Inputs each given OpenScop file to PLUTO to generate
                its Python parallel version. Output files are generated
                from the base_output file name and appending the loop block id

                Arguments:
                        - scop_files : List of OpenScop file names
                        - base_output: Parallel Python output base file path
                Return:
                        - output_files : List of file names containing the generated
                                paralell Python code
                Raise:
                        - Scop2PScop2PyException
                """

                if __debug__:
                        logger.debug("[decorator] Start scop2pscop2py")

                from pycompss.util.translators.scop2pscop2py.translator_scop2pscop2py import Scop2PScop2Py
                output_files = []
                id = 0
                for sf in scop_files:
                        # Generate file name
                        of = base_output + str(id)
                        # Perform PLUTO call
                        Scop2PScop2Py.translate(sf, of)
                        # Prepare for next iteration
                        output_files.append(of)
                        id = id + 1

                # Finish
                if __debug__:
                        logger.debug("[decorator] Finished scop2pscop2py")

                return output_files

        def _py2pycompss(self, func_source, par_py_files, output):
                """
                Substitutes the given parallel python files into the original
                function code and adds the required PyCOMPSs annotations. The
                result is stored in the given output file

                Arguments:
                        - func_source : Python original function
                        - par_py_files : List of files containing the Python parallelization
                                of each for block in the func_source
                        - output : PyCOMPSs file path
                Return:
                Raise:
                        - Py2PyCOMPSsException
                """

                if __debug__:
                        logger.debug("[decorator] Start py2pycompss")

                from pycompss.util.translators.py2pycompss.translator_py2pycompss import Py2PyCOMPSs
                Py2PyCOMPSs.translate(func_source, par_py_files, output)

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
