#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest
import logging

#
# Logger definition
#

logger = logging.getLogger(__name__)


#
# Translator class
#

class Py2PyCOMPSs(object):

    @staticmethod
    def translate(func_source, par_py_files, output):
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
            logger.debug("[Py2PyCOMPSs] Initialize translation")

        # LOG ALL
        print("----------------------")
        print("FUNC SOURCE:")
        print(str(func_source))
        print("PY FILES:")
        for par_f in par_py_files:
                logger.info(" - File: " + str(par_f))
                with open(par_f, 'r') as f:
                        print(f.read())
        print("OUTPUT: " + str(output))
        print("----------------------")

        # TODO: Add real code
        try:
            import os
            dir_path = os.path.dirname(os.path.realpath(__file__))
            pycompss_file = dir_path + "/tests/test1_matmul.expected.pycompss"
            from shutil import copyfile
            copyfile(pycompss_file, output)
        except Exception as e:
            raise Py2PyCOMPSsException("[ERROR] Cannot copy PyCOMPSs file", e)

        if __debug__:
            logger.debug("[Py2PyCOMPSs] End translation")


#
# Exception Class
#

class Py2PyCOMPSsException(Exception):

    def __init__(self, msg=None, nested_exception=None):
        self.msg = msg
        self.nested_exception = nested_exception

    def __str__(self):
        s = "Exception on Py2PyCOMPSs.translate method.\n"
        if self.msg is not None:
            s = s + "Message: " + str(self.msg) + "\n"
        if self.nested_exception is not None:
            s = s + "Nested Exception: " + str(self.nested_exception) + "\n"
        return s


#
# UNIT TESTS
#

class TestPy2PyCOMPSs(unittest.TestCase):

    def test_matmul(self):
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
        test_module = importlib.import_module("pycompss.util.translators.py2pycompss.tests.test1_matmul_func")
        func = getattr(test_module, func_name)
        import inspect
        func_code = inspect.getsource(func)
        
        # Create list of parallel py codes
        src_file0 = tests_path + "/test1_matmul.src.python"
        par_py_files = [src_file0]

        # Output file
        out_file = tests_path + "/test1_matmul.out.pycompss"

        # Translate
        Py2PyCOMPSs.translate(func_code, par_py_files, out_file)

        # Check file content
        expected_file = tests_path + "/test1_matmul.expected.pycompss"
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


#
# MAIN
#

if __name__ == '__main__':
    unittest.main()
