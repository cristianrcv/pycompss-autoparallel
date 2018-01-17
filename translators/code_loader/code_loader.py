#!/usr/bin/python                                                                                                                                                                                                                                                              
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function


# 
# Replacer class
#

class CodeLoader(object):

        @staticmethod
        def load(func):
                # 
                # Returns the source code of the given function
                #
                # Arguments:
                #       - func : Function
                # Return:
                #       - func_source : Source code of the function
                # Raise:
                #       - GetPyException
                #
        
                try:
                        import inspect
                        func_source = inspect.getsource(func)
                except Exception as e:
                        raise CodeLoaderException("[ERROR] Cannot obtain source code from function", e)
        
                return func_source


#                                                                                                                                                                                                                                                                              
# Exception Class
#                                                                                                                                                                                                                                                                              

class CodeLoaderException(Exception):

        def __init__(self, msg, nested_exception):
                self.msg = msg
                self.nested_exception = nested_exception

        def __str__(self):
                return "Exception on CodeLoader.load method.\n Message: " + str(self.msg) + "\n Nested Exception: " + str(self.nested_exception)


# 
# UNIT TEST CASES
#

import unittest
class testCodeLoader(unittest.TestCase):

        def test_code_loader(self):
                pass


#
# MAIN FOR UNIT TEST
#

if __name__ == '__main__':
        unittest.main()

