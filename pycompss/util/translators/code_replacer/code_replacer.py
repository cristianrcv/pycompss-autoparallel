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
                        original_file = inspect.getfile(func)
                        with open(original_file, 'r') as f:
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

                # Backup user file
                try:
                        import os
                        from shutil import copyfile
                        bkp_file = os.path.splitext(original_file)[0] + "_bkp.py"
                        copyfile(original_file, bkp_file)
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot backup source file", e)
                if __debug__:
                        logger.debug("[code_replacer] User code backup in file " + str(bkp_file))

                # Create new source file
                try:
                        import os
                        new_file = os.path.splitext(original_file)[0] + "_autogen.py"
                        with open(new_file, 'w') as f:
                                f.write(new_content)
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot create new source file", e)
                if __debug__:
                        logger.debug("[code_replacer] New code generated in file " + str(new_file))

                # Move new content to original file
                try:
                        from shutil import copyfile
                        copyfile(new_file, original_file)
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot replace original file", e)

                # Load new function from new file
                # Similar to: from new_module import func.__name__ as new_func
                new_module = os.path.splitext(os.path.basename(original_file))[0]
                if __debug__:
                        logger.debug("[code_replacer] Import module " + str(func.__name__) + " from " + str(new_module))
                try:
                        import importlib
                        new_func = getattr(importlib.import_module(new_module), func.__name__)
                except Exception as e:
                        raise CodeReplacerException("[ERROR] Cannot load new function and module " + str(func.__name__) + " from " + str(new_module), e)
                if __debug__:
                        logger.debug("[code_replacer] New function: " + str(new_func))

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

class TestCodeReplacer(unittest.TestCase):

        def test_code_replacer(self):
                # Insert function file into pythonpath
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                testsPath = dirPath + "/tests"
                import sys
                sys.path.insert(0, testsPath)

                # Import function to replace
                from tests.original import test_func as f
                import inspect
                userFile = inspect.getfile(f)

                # Import new code
                import os
                file_new_code = testsPath + "/new.py"

                try:
                        # Perform replace
                        new_f = CodeReplacer.replace(f, file_new_code)

                        # Check function has been reloaded
                        self.assertNotEqual(f, new_f)

                        # Check final user file content
                        expectedFile = testsPath + "/expected.python"
                        with open(expectedFile, 'r') as f:
                                expectedContent = f.read()
                        with open(userFile, 'r') as f:
                                userContent = f.read()
                        self.assertEqual(userContent, expectedContent)
                except Exception:
                        raise
                finally:
                        TestCodeReplacer._restore(testsPath, userFile)
                        TestCodeReplacer._clean(testsPath)

        @staticmethod
        def _restore(testsPath, userFile):
                bkpFile = testsPath + "/original_bkp.py"
                try:
                        from shutil import copyfile
                        copyfile(bkpFile, userFile)
                except Exception as e:
                        print("ERROR: Cannot restore original file")
                        print (str(e))

        @staticmethod
        def _clean(testsPath):
                import os
                bkpFile = testsPath + "/original_bkp.py"
                if os.path.isfile(bkpFile):
                        os.remove(bkpFile)

                autogenFile = testsPath + "/original_autogen.py"
                if os.path.isfile(autogenFile):
                        os.remove(autogenFile)


#
# MAIN FOR UNIT TEST
#

if __name__ == '__main__':
        unittest.main()
