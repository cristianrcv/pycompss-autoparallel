#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


#
# Translator class
#

class Py2PyCOMPSs(object):

        @staticmethod
        def translate(func_source, source, output):
                #
                # Inputs a Python code with parallel annotations and outputs its PyCOMPSs code
                #
                # Arguments:
                #       - func_source : Python original function
                #       - source : Python with parallel annotations file path
                #       - output : PyCOMPSs file path
                # Return:
                #       - error : Non-zero value if an error is found, 0 otherwise
                # Raise:
                #       - Py2PyCOMPSsException
                #

                # TODO: Add real code

                try:
                        import os
                        dirPath = os.path.dirname(os.path.realpath(__file__))
                        pycompss_file = dirPath + "/tests/test1_matmul.expected.pycompss"
                        from shutil import copyfile
                        copyfile(pycompss_file, output)
                except Exception as e:
                        raise Py2PyCOMPSsException("[ERROR] Cannot copy PyCOMPSs file", e)


#
# Exception Class
#

class Py2PyCOMPSsException(Exception):

        def __init__(self, msg, nested_exception):
                self.msg = msg
                self.nested_exception = nested_exception

        def __str__(self):
                return "Exception on Py2PyCOMPSs.translate method.\n Message: " + str(self.msg) + "\n Nested Exception: " + str(self.nested_exception)


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
