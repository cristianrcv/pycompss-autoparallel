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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s - %(message)s')
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
        logger.debug("Init @parallel decorator...")

        # Store arguments passed to the decorator
        self.args = args
        self.kwargs = kwargs

        # Add a place to store internal translator structures
        self.translator_py2scop = None
        self.code_replacer = None

    def __call__(self, func):
        """
        Parallelizes the annotated function and returns a wrapper to it

        Arguments:
                - func : Python Function Object to parallelize
        Return:
                - parallel_f : Wrapper to the parallel version of the given function (new_func)
        Raise:
                - Py2ScopException
                - Scop2PScop2PyException
                - Py2PyCOMPSsException
                - CodeReplacerException
        """

        if __debug__:
            logger.debug("[decorator] Start decorator for function: " + str(func))

        # Parallelize code
        new_func = self._translate(func)

        # Add decorator wrapper
        @wraps(new_func)
        def parallel_f(*args, **kwargs):
            # This is executed only when called.
            if __debug__:
                logger.debug("[parallel_f] Executing parallel_f wrapper")

            # Save things
            if __debug__:
                logger.debug("[parallel_f] Saving method data")
            slf = None
            saved = {}
            if len(args) > 0:
                # The 'self' for a method function is passed as args[0]
                slf = args[0]
                # Replace and store the attributes
                for k, v in self.kwargs.items():
                    if hasattr(slf, k):
                        saved[k] = getattr(slf, k)
                        setattr(slf, k, v)

            # Call the method
            if __debug__:
                logger.debug("[parallel_f] Calling user method")

            try:
                ret = new_func(*args, **kwargs)
            except Exception:
                raise
            finally:
                # Put things back
                if __debug__:
                    logger.debug("[parallel_f] Restoring method data")
                if len(args) > 0:
                    for k, v in saved.items():
                        setattr(slf, k, v)

                # Restore user code (according to code_replacer)
                if __debug__:
                    logger.debug("[parallel_f] Restoring user code")
                if self.code_replacer is not None:
                    self.code_replacer.restore()

            # Return method value
            return ret

        # Return the wrapper of the parallelized function
        parallel_f.__doc__ = new_func.__doc__
        return parallel_f

    def _translate(self, func=None, keep_generated_files=False):
        """
        Parallelizes the given function and returns a pointer to the new parallel function

        Arguments:
                - func : Python Function Object to parallelize
                - keep_generated_files : Keep auto-generated intermediate files (default False)
        Return:
                - new_func : Python Function Object to parallel function
        Raise:
                - Py2ScopException
                - Scop2PScop2PyException
                - Py2PyCOMPSsException
                - CodeReplacerException
        """

        if __debug__:
            logger.debug("[decorator] Translating function: " + str(func))

        scop_files = None
        py_files = None
        pycompss_file = None
        try:
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
            self._py2pycompss(func, py_files, pycompss_file)
            if __debug__:
                logger.debug("[decorator] Generated PyCOMPSs content")
                # with open(pycompss_file, 'r') as f:
                #        logger.debug(f.read())

            # Embed code into user file
            new_func = self._load_generated_code(func, pycompss_file, keep_generated_files)
        except Exception as e:
            logger.error(e)
            raise
        finally:
            # Clean
            files_to_clean = []
            if scop_files is not None:
                for f in scop_files:
                    files_to_clean.append(f)
            if py_files is not None:
                for f in py_files:
                    files_to_clean.append(f)
            if pycompss_file is not None:
                files_to_clean.append(pycompss_file)
            self._clean(files_to_clean)

        # Return parallelized code
        if __debug__:
            logger.debug("[decorator] Replaced " + str(func) + " by " + str(new_func))
        return new_func

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
        self.translator_py2scop = Py2Scop(func)
        output_files = self.translator_py2scop.translate(base_output)

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
        file_num = 0
        for sf in scop_files:
            # Generate file name
            of = base_output + str(file_num)
            # Perform PLUTO call
            Scop2PScop2Py.translate(sf, of)
            # Prepare for next iteration
            output_files.append(of)
            file_num = file_num + 1

        # Finish
        if __debug__:
            logger.debug("[decorator] Finished scop2pscop2py")

        return output_files

    def _py2pycompss(self, func, par_py_files, output):
        """
        Substitutes the given parallel python files into the original
        function code and adds the required PyCOMPSs annotations. The
        result is stored in the given output file

        Arguments:
                - func : Python original function
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
        Py2PyCOMPSs.translate(func, par_py_files, output)

        # Finish
        if __debug__:
            logger.debug("[decorator] Finished py2pycompss")

    def _load_generated_code(self, func, new_code, keep_generated_files):
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
        self.code_replacer = CodeReplacer(func)
        new_func = self.code_replacer.replace(new_code, keep_generated_files)

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
        Raise:
        """

        if __debug__:
            logger.debug("[decorator] Cleaning...")

        import os
        for f in list_of_files:
            if __debug__:
                logger.debug("[decorator] Cleaning file " + str(f))
            os.remove(f)

        if __debug__:
            logger.debug("[decorator] Finished cleaning")


#
# UNIT TEST CASES
#

class TestParallelDecorator(unittest.TestCase):

    def test_decorator(self):
        # Base variables
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))
        tests_path = dir_path + "/tests"

        # Insert function file into pythonpath
        import sys
        sys.path.insert(0, tests_path)

        # Import function to replace
        import importlib
        func_name = "matmul"
        test_module = importlib.import_module("pycompss.api.tests.test1_matmul")
        func = getattr(test_module, func_name)

        # Generate parallel code
        from pycompss.util.translators.code_replacer.code_replacer import CodeReplacerException
        p = parallel()
        try:
            # We don't retrieve new_func because we are not gonna import it (COMPSs is off)
            p._translate(func, True)
        except CodeReplacerException as cre:
            logger.info("Catch CodeReplacerException because COMPSs is not initialized. CONTINUING")
            if __debug__:
                logger.debug(cre)

        # Check file content
        out_file = tests_path + "/test1_matmul_autogen.py"
        expected_file = tests_path + "/test1_matmul.expected.python"
        try:
            with open(expected_file, 'r') as f:
                expected_content = f.read()
            with open(out_file, 'r') as f:
                out_content = f.read()
            self.assertEqual(out_content, expected_content)
        except Exception:
            raise
        finally:
            # Erase file
            os.remove(out_file)
            # Erase PYC file because we are overriding it and python does not know
            os.remove(tests_path + "/test1_matmul.pyc")


#
# MAIN FOR UNIT TEST
#

if __name__ == '__main__':
    unittest.main()
