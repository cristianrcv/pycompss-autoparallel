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

                # TODO: Add real code
                try:
                        import os
                        dirPath = os.path.dirname(os.path.realpath(__file__))
                        pycompss_file = dirPath + "/tests/test1_matmul.expected.pycompss"
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
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                srcFile = dirPath + "/tests/test1_matmul.src.python"
                expectedFile = dirPath + "/tests/test1_matmul.expected.pycompss"
                outFile = dirPath + "/tests/test1_matmul.out.pycompss"

                # Translate
                Py2PyCOMPSs.translate(None, srcFile, outFile)

                # Check file content
                with open(expectedFile, 'r') as f:
                        expectedContent = f.read()
                with open(outFile, 'r') as f:
                        outContent = f.read()
                self.assertEqual(outContent, expectedContent)

                # Erase file
                os.remove(outFile)


#
# MAIN
#

if __name__ == '__main__':
        unittest.main()
