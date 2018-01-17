#!/usr/bin/python                                                                                                                                                                                                                                                              
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Debug flag
DEBUG=1


# 
# Code Replacer class
#

class CodeReplacer(object):

        @staticmethod
        def replace(func, new_code):
                #
                # Replaces the func code by the content of new_code
                #
                # Arguments:
                #       - func : function to be replaced
                #       - new_code : File path containing the new code
                # Return:
                #       - new_func : pointer to the new function
                # Raise:
                #       - CodeReplacerException
                #
        
                # Retrieve original content
                try:
                        import inspect
                        func_file = inspect.getfile(func)
                        with open(func_file, 'r') as f:
                                original_content = f.read()
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot load original code from file", e)
        
                # Retrieve function content
                try:
                        func_content = inspect.getsource(func)
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot retrieve function content", e)
        
                # Retrieve new code
                try:
                        with open(new_code, 'r') as f:
                                new_content = f.read()
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot retrieve new content", e)
        
                # Replace function content by new code in original content
                try:
                        new_content = original_content.replace(func_content, new_content)
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot generate new content", e)
        
                # Create new source file
                try:
                        import os
                        new_file = os.path.splitext(func_file)[0] + "_autogen.py"
                        with open(new_file, 'w') as f:
                                f.write(new_content)
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot create new source file", e)
                if DEBUG:
                        print("[code_replacer] New code generated in file " + str(new_file))
        
                # Load new function from new file
                # Similar to: from new_module import func.__name__ as new_func
                new_module = os.path.splitext(new_file)[0]
                if DEBUG:
                        print("[code_replacer] Import module " + str(func.__name__) + " from " + str(new_module))
                try:
                        import importlib
                        new_func = getattr(importlib.import_module(new_module), func.__name__)
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot load new function and module", e)
                if DEBUG:
                        print("[code_replacer] New function: " + str(new_func))
        
                # Finish
                return new_func


#                                                                                                                                                                                                                                                                              
# Exception Class
#                                                                                                                                                                                                                                                                              

class CodeReplacerException(Exception):

        def __init__(self, msg, nested_exception):
                self.msg = msg
                self.nested_exception = nested_exception

        def __str__(self):
                return "Exception on CodeReplacer.replace method.\n Message: " + str(self.msg) + "\n Nested Exception: " + str(self.nested_exception)


# 
# UNIT TEST CASES
#

import unittest
class testCodeReplacer(unittest.TestCase):

        def test_code_replacer(self):
                pass


#
# MAIN FOR UNIT TEST
#

if __name__ == '__main__':
        unittest.main()

