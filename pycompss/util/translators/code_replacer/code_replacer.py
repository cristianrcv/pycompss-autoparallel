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
    """
    Creates an object to replace the given function

    Attributes:
            - func : Python function object to replace
            - original_file : File containing the original function code
            - bkp_file : Backup of the original file
            - new_file : File containing the new parallel function code
    """

    def __init__(self, func=None):
        """
        Creates a code replacer for the given function

        Arguments:
                - func : function to be replaced
        Raise:
                - CodeReplacerException
        """
        self.func = func

        # Retrieve original file
        try:
            import inspect
            self.original_file = inspect.getfile(func)
        except Exception as e:
            raise CodeReplacerException("[ERROR] Cannot find original file", e)

        # Set backup file
        import os
        file_name = os.path.splitext(self.original_file)[0]
        self.bkp_file = file_name + "_bkp.py"
        # Set new file
        self.new_file = file_name + "_autogen.py"

    def replace(self, new_code, keep_generated_files=False):
        """
        Replaces the func code by the content of new_code and cleans all the files if an
        internal error is raised

        Arguments:
                - new_code : File path containing the new code
        Return:
                - new_func : pointer to the new function
        Raise:
                - CodeReplacerException
        """

        if __debug__:
            logger.debug("[code_replacer] Replacing code of " + str(self.func) + " by code inside " + str(new_code))

        # Wrap the internal replace method to catch exceptions and restore user code
        try:
            new_func = self._replace(new_code)
        except Exception as e:
            if keep_generated_files:
                self.restore()
            else:
                self.clean()
            raise CodeReplacerException("[ERROR] Cannot replace func " + str(self.func), e)

        # Finish
        if __debug__:
            logger.debug("[code_replacer] New function: " + str(new_func))
        return new_func

    def _replace(self, new_code):
        """
        Replaces the func code by the content of new_code

        Arguments:
                - new_code : File path containing the new code
        Return:
                - new_func : pointer to the new function
        Raise:
                - CodeReplacerException
        """

        # Retrieve original content
        try:
            with open(self.original_file, 'r') as f:
                original_content = f.read()
        except Exception as e:
            raise CodeReplacerException("[ERROR] Cannot load original code from file", e)

        # Retrieve function content
        try:
            import inspect
            func_content = inspect.getsource(self.func)
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
            from shutil import copyfile
            copyfile(self.original_file, self.bkp_file)
        except Exception as e:
            raise CodeReplacerException("[ERROR] Cannot backup source file", e)
        if __debug__:
            logger.debug("[code_replacer] User code backup in file " + str(self.bkp_file))

        # Create new source file
        try:
            with open(self.new_file, 'w') as f:
                f.write(new_content)
        except Exception as e:
            raise CodeReplacerException("[ERROR] Cannot create new source file", e)
        if __debug__:
            logger.debug("[code_replacer] New code generated in file " + str(self.new_file))

        # Move new content to original file
        try:
            from shutil import copyfile
            copyfile(self.new_file, self.original_file)
        except Exception as e:
            raise CodeReplacerException("[ERROR] Cannot replace original file", e)

        # Load new function from new file
        # Similar to: from new_module import func.__name__ as new_func
        import os
        new_module = os.path.splitext(os.path.basename(self.original_file))[0]
        if __debug__:
            logger.debug("[code_replacer] Import module " + str(self.func.__name__) + " from " + str(new_module))
        try:
            import importlib
            new_func = getattr(importlib.import_module(new_module), self.func.__name__)
        except Exception as e:
            raise CodeReplacerException(
                "[ERROR] Cannot load new function and module " + str(self.func.__name__) + " from " + str(new_module),
                e)

        # Return the new function
        return new_func

    def restore(self):
        """
        Erases intermediate files

        Arguments:
        Return:
        Raise:
        """

        if __debug__:
            logger.debug("[code_replacer] Restoring user code")

        import os
        if os.path.isfile(self.bkp_file):
            # Restore user file
            from shutil import copyfile
            copyfile(self.bkp_file, self.original_file)

            # Clean intermediate files
            os.remove(self.bkp_file)

    def clean(self):
        """
        Erases all the generated files

        Arguments:
        Return:
        Raise:
        """

        # Restore user code
        self.restore()

        # Clean auto-generated file
        if __debug__:
            logger.debug("[code_replacer] Cleaning all files")

        import os
        if os.path.isfile(self.new_file):
            os.remove(self.new_file)


#
# Exception Class
#

class CodeReplacerException(Exception):

    def __init__(self, msg=None, nested_exception=None):
        self.msg = msg
        self.nested_exception = nested_exception

    def __str__(self):
        s = "Exception on CodeReplacer.replace method.\n"
        if self.msg is not None:
            s = s + "Message: " + str(self.msg) + "\n"
        if self.nested_exception is not None:
            s = s + "Nested Exception: " + str(self.nested_exception) + "\n"
        return s


#
# UNIT TEST CASES
#

class TestCodeReplacer(unittest.TestCase):

    def test_code_replacer(self):
        # Insert function file into PYTHONPATH
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))
        tests_path = dir_path + "/tests"
        import sys
        sys.path.insert(0, tests_path)

        # Import function to replace
        from tests.original import test_func as f
        import inspect
        user_file = inspect.getfile(f)

        # Import new code
        file_new_code = tests_path + "/new.py"
        cr = None
        try:
            # Perform replace
            cr = CodeReplacer(f)
            new_f = cr.replace(file_new_code)

            # Check function has been reloaded
            self.assertNotEqual(f, new_f)

            # Check final user file content
            expected_file = tests_path + "/expected.python"
            with open(expected_file, 'r') as f:
                expected_content = f.read()
            with open(user_file, 'r') as f:
                user_content = f.read()
            self.assertEqual(user_content, expected_content)
        except Exception:
            raise
        finally:
            # Clean intermediate files
            if cr is not None:
                cr.clean()


#
# MAIN FOR UNIT TEST
#

if __name__ == '__main__':
    unittest.main()
