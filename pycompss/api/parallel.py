#!/usr/bin/python

# -*- coding: utf-8 -*-

# Imports
import unittest


#
# Decorator definition
#

def parallel(func):
        """
        Receives a function annotated with the @parallel decorator and modifies
        the user code to make it parallel. Since it removes the @parallel
        decorator each function is only processed once

        Arguments:
                - func : Function annotated with the @parallel decorator
        Return:
        """

        if __debug__:
                print("[decorator] Start decorator for function: " + str(func))

        new_func = func
        try:
                # Get the source code of the function
                func_source = get_py(func)
                if __debug__:
                        print("[decorator] Func source code")
                        # print(str(func_source))

                # Process python code to scop
                scop_file = ".tmp_gen_scop.scop"
                py2scop(func_source, scop_file)
                if __debug__:
                        print("[decorator] Generated OpenScop content")
                        # with open(scop_file, 'r') as f:
                        #         print(f.read())

                # Parallelize OpenScop code and process it back to python
                py_file = ".tmp_gen_parallel.py"
                scop2pscop2py(scop_file, py_file)
                if __debug__:
                        print("[decorator] Generated Parallel Python content")
                        # with open(py_file, 'r') as f:
                        #        print(f.read())

                # Add PyCOMPSs annotations
                pycompss_file = ".tmp_gen_pycompss.py"
                py2pycompss(func_source, py_file, pycompss_file)
                if __debug__:
                        print("[decorator] Generated PyCOMPSs content")
                        # with open(pycompss_file, 'r') as f:
                        #        print(f.read())

                # Embed code into user file
                new_func = load_generated_code(func, pycompss_file)
        except Exception as e:
                print(e)
                raise
        finally:
                # Clean
                files_to_clean = []
                if 'scop_file' in locals():
                        files_to_clean.append(scop_file)
                if 'py_file' in locals():
                        files_to_clean.append(py_file)
                if 'pycompss_file' in locals():
                        files_to_clean.append(pycompss_file)
                clean(files_to_clean)

        # Execute parallelized code
        print("[decorator] Replaced " + str(func) + " by " + str(new_func))
        return new_func


#
# Internal functions
#

def get_py(func):
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
                print("[decorator] Start get_py")

        from code_loader import CodeLoader
        func_source = CodeLoader.load(func)

        # Finish
        if __debug__:
                print("[decorator] Finished get_py")
        return func_source


def py2scop(source, output):
        """
        Inputs a Python code with scop pragmas and outputs its
        openscop representation in the given file

        Arguments:
                source : Python code with scop prgramas
                output : OpenScop output file path
        Return:
        Raise:
                - Py2ScopException
        """

        if __debug__:
                print("[decorator] Start py2scop")

        from py2scop import Py2Scop
        Py2Scop.translate(source, output)

        # Finish
        if __debug__:
                print("[decorator] Finished py2scop")


def scop2pscop2py(source, output):
        """
        Inputs an OpenScop representation to PLUTO that generates
        its parallel version in Python

        Arguments:
                - source : OpenScop source file path
                - output : Python output file path
        Return:
        Raise:
                - Scop2PScop2PyException
        """

        if __debug__:
                print("[decorator] Start scop2pscop2py")

        from scop2pscop2py import Scop2PScop2Py
        Scop2PScop2Py.translate(source, output)

        # Finish
        if __debug__:
                print("[decorator] Finished scop2pscop2py")


def py2pycompss(func_source, source, output):
        """
        Inputs a Python code with parallel annotations and outputs its
        PyCOMPSs code

        Arguments:
                - func_source : Python original function
                - source : Python with parallel annotations file path
                - output : PyCOMPSs file path
        Return:
                - error : Non-zero value if an error is found, 0 otherwise
        Raise:
                - Py2PyCOMPSsException
        """

        if __debug__:
                print("[decorator] Start py2pycompss")

        from py2pycompss import Py2PyCOMPSs
        Py2PyCOMPSs.translate(func_source, source, output)

        # Finish
        if __debug__:
                print("[decorator] Finished py2pycompss")


def load_generated_code(func, new_code):
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
                print("[decorator] Start load_generated_code")

        from code_replacer import CodeReplacer
        new_func = CodeReplacer.replace(func, new_code)

        # Finish
        if __debug__:
                print("[decorator] Finished load_generated_code")
        return new_func


def clean(list_of_files):
        """
        Cleans intermediate files

        Arguments:
                - list_of_files : List of files
        Return:
        """

        if __debug__:
                print("[decorator] Cleaning...")

        import os
        for file in list_of_files:
                if __debug__:
                        print("[decorator] Cleaning file " + str(file))
                os.remove(file)

        if __debug__:
                print("[decorator] Finished cleaning")


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
