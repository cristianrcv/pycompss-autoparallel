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
# Replacer class
#

class CodeLoader(object):

        @staticmethod
        def load(func):
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
                        logger.debug("[CodeLoader] Load code from " + str(func))
                try:
                        import inspect
                        func_source = inspect.getsource(func)
                except Exception as e:
                        raise CodeLoaderException("[ERROR] Cannot obtain source code from function", e)

                if __debug__:
                        logger.debug("[CodeLoader] Code successfully loaded")

                return func_source


#
# Exception Class
#

class CodeLoaderException(Exception):

        def __init__(self, msg=None, nested_exception=None):
                self.msg = msg
                self.nested_exception = nested_exception

        def __str__(self):
                s = "Exception on CodeLoader.load method.\n"
                if self.msg is not None:
                        s = s + "Message: " + str(self.msg) + "\n"
                if self.nested_exception is not None:
                        s = s + "Nested Exception: " + str(self.nested_exception) + "\n"
                return s


#
# UNIT TEST CASES
#

class DummyTestClass():

        @staticmethod
        def dummy_func():
                # A dummy function
                print ("A dummy function")


class TestCodeLoader(unittest.TestCase):

        def test_code_loader(self):
                # Get a function pointer
                func_name = 'dummy_func'
                func_class = DummyTestClass()
                func = None
                try:
                        func = getattr(func_class, func_name)
                except AttributeError:
                        raise NotImplementedError("Class `{}` does not implement `{}`".format(func_class.__class__.__name__, func_name))

                # Load function source
                source_func = CodeLoader.load(func)

                # Check output
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                expect_func_file = dirPath + "/tests/dummy_func_expected.python"
                with open(expect_func_file, 'r') as f:
                        expected_func = f.read()

                self.assertEquals(source_func, expected_func)


#
# MAIN FOR UNIT TEST
#

if __name__ == '__main__':
        unittest.main()
