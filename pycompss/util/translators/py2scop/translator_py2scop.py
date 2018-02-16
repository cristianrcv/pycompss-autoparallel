#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


#
# Translator class
#

class Py2Scop(object):

        # TODO: 2 consecutive for's as single for block

        def __init__(self, func=None):
                #
                # Initializes the translator internal structures
                #
                # Arguments:
                #       - func : Python function to translate
                # Return:
                # Raise:
                #       - Py2ScopException
                #

                # Retrieve function to translate
                self.func = func

                # Create AST
                import inspect
                import ast
                try:
                        self.func_code = inspect.getsource(func)
                        self.func_ast = ast.parse(self.func_code)
                except Exception as e:
                        raise Py2ScopException("ERROR: Cannot retrieve AST from function", e)

                # Initialize other variables
                self.for_blocks = None
                self.scops = None

        def translate(baseFileName):
                #
                # Inputs a Python code with scop pragmas and outputs its
                # openscop representation in the given file
                #
                # Arguments:
                #       func : Python function
                #       baseFileName : OpenScop base name for output file path
                # Return:
                #       outputFileNames : List of written OS files (one per loop block)
                # Raise:
                #       - Py2ScopException
                #

                # Generate the list of for blocks
                try:
                        self.for_blocks = Py2Scop._ast_extract_for_blocks(self.func_ast, 0, [])
                except Exception as e:
                        raise Py2ScopException("ERROR: Cannot generate code blocks", e)

                # Translate loop blocks
                try:
                        for fb in self.for_blocks:
                                self.scops.append(Py2Scop._ast2scop(fb))
                except Exception as e:
                        raise Py2ScopException("ERROR: Cannot generate SCOPs from ForBlocks", e)

                # Write loop blocks
                outputFileNames = []
                numFiles = 0
                for i in range(1, len(self.scops), 2):
                        fileName = baseFileName + str(numFiles)
                        try:
                                Py2Scop.write_os(self.scops[i], fileName)
                        except Exception as e:
                                raise Py2ScopException("ERROR: Cannot write OS file " + str(i), e)

                        numFiles = numFiles + 1
                        outputFileNames.append(fileName)

                # Return written fileNames
                return outputFileNames

        # Process AST code
        @staticmethod
        def _ast_extract_for_blocks(node, for_level=0, for_blocks=[]):
                #
                # Inputs an AST node and process it and its childs recursively
                #
                # Arguments:
                #       node : AST node
                #       for_level : Nested FOR level
                #       for_blocks : Primary for_blocks found recursively
                #
                # Return:
                #       for_blocks : Primary for_blocks
                # Raise:
                #

                import ast
                import _ast
                import copy

                # DEBUG: Print current node information
                #print('  ' + str(for_level) + " " + Py2Scop._debug_str_node(node))

                # Copy current node if it is an outermost loop
                if isinstance(node, _ast.For) and for_level == 0:
                        node_copy = copy.deepcopy(node)
                        ast.fix_missing_locations(node_copy)
                        for_blocks.append(node_copy)

                # Prepare for next recursion
                if isinstance(node, _ast.For):
                        for_level = for_level + 1

                # Child recursion
                for field, value in ast.iter_fields(node):
                        if isinstance(value, list):
                                for item in value:
                                        if isinstance(item, ast.AST):
                                                for_blocks = Py2Scop._ast_extract_for_blocks(item, for_level=for_level, for_blocks=for_blocks)
                        elif isinstance(value, ast.AST):
                                for_blocks = Py2Scop._ast_extract_for_blocks(value, for_level=for_level, for_blocks=for_blocks)

                # Return all the outermost loops
                return for_blocks

        @staticmethod
        def _debug_str_node(node):
                import ast
                if isinstance(node, ast.AST):
                        fields = [(name, Py2Scop._debug_str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
                        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
                        return rv + ')'
                else:
                        return repr(node)

        # TRANSLATION FROM AST TO SCOP
        @staticmethod
        def _ast2scop(tree):
                #
                # Inputs a AST loop block representation and returns its SCOP
                # representation
                #
                # Arguments:
                #       tree : AST loop block representation
                # Return:
                #       scop : SCOP object representing the loop block
                # Raise:
                #

                # TODO: IMPLEMENT METHOD

                from pycompss.util.translators.scop_types.scop_class import Scop
                scop = Scop()

                import ast
                print(ast.dump(tree))

                return scop

        # WRITE OS TO FILE
        @staticmethod
        def write_os(scop, fileName):
                #
                # Writes the given SCOP into the given OpenScop file
                #
                # Arguments:
                #       scop : SCOP object
                #       fileName : Output file path
                # Return:
                # Raise:
                #

                with open(fileName, 'w') as f:
                        print("# [File generated by the OpenScop Library 0.9.1]", file=f)
                        print("", file=f)
                        scop.write_os(f)


#
# Exception Class
#

class Py2ScopException(Exception):

        def __init__(self, msg, nested_exception):
                self.msg = msg
                self.nested_exception = nested_exception

        def __str__(self):
                return "Exception on Py2Scop.translate method.\n Message: " + str(self.msg) + "\n Nested Exception: " + str(self.nested_exception)


#
# UNIT TESTS
#

class TestPy2Scop(unittest.TestCase):

        @staticmethod
        def _test_ast_generation(func_name):
                # Insert function file into pythonpath
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                testsPath = dirPath + "/tests"
                import sys
                sys.path.insert(0, testsPath)

                # Import function to replace
                import importlib
                t1ag = getattr(__import__("tests.test1_ast_generation"), "test1_ast_generation")
                func = getattr(t1ag, func_name)

                # Create AST
                import inspect
                func_code = inspect.getsource(func)
                import ast
                func_ast = ast.parse(func_code)

                # Retrieve for blocks
                fbs = Py2Scop._ast_extract_for_blocks(func_ast, 0, [])

                # DEBUG: Print fbs
                #print("---- DEBUG FOR " + str(func_name))
                #for fb in fbs:
                #        print(ast.dump(fb))

                # Return generated blocks
                return fbs

        @staticmethod
        def _test_ast2scop(func_name):
                # Insert function file into pythonpath
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                testsPath = dirPath + "/tests"
                import sys
                sys.path.insert(0, testsPath)

                # Import function to replace
                import importlib
                t1ag = getattr(__import__("tests.test2_ast2scop"), "test2_ast2scop")
                func = getattr(t1ag, func_name)

                # Create AST
                import inspect
                func_code = inspect.getsource(func)
                import ast
                func_ast = ast.parse(func_code)

                # Retrieve for blocks
                fbs = Py2Scop._ast_extract_for_blocks(func_ast, 0, [])

                # Apply SCOP transformation to first for block
                scop = Py2Scop._ast2scop(fbs[0])

                # DEBUG: Print scop
                Py2Scop.write_os(scop, str(func_name) + ".debug.scop")

                # Return scop
                return scop

        def test_ast_empty(self):
                func_name = "empty"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 0)

        def test_ast_simple1(self):
                func_name = "simple1"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 1)

        def test_ast_simple2(self):
                func_name = "simple2"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 1)

        def test_ast_simple3(self):
                func_name = "simple3"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 1)

        def test_ast_simple4(self):
                func_name = "simple4"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 1)

        def test_ast_intermediate1(self):
                func_name = "intermediate1"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 2)

        def test_ast_intermediate2(self):
                func_name = "intermediate2"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 2)

        def test_ast_intermediate3(self):
                func_name = "intermediate3"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 2)

        def test_ast_loop_nests1(self):
                func_name = "loop_nests1"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 1)

        def test_ast_loop_nests2(self):
                func_name = "loop_nests2"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 1)

        def test_ast_complex(self):
                func_name = "complex"

                # Retrieve for blocks
                fbs = TestPy2Scop._test_ast_generation(func_name)
                
                # Check the number of generated for blocks
                self.assertEquals(len(fbs), 4)

        def test_ast2scop(self):
                func_name = "simple1"

                # Retrieve scop
                scop = TestPy2Scop._test_ast2scop(func_name)

                # Check scop
                #TODO: check scop

        def ttest_matmul(self):
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                srcFile = dirPath + "/tests/test2_matmul.src.python"
                expectedFile = dirPath + "/tests/test2_matmul.expected.scop"
                baseOutFile = dirPath + "/tests/test2_matmul.out.scop"

                try:
                        # Translate
                        translator = Py2Scop()
                        outputFiles = translator.translate(srcFile, baseOutFile)

                        # Check that there is only one output file
                        self.assertEqual(len(outputFiles), 1)

                        # Check file content
                        with open(expectedFile, 'r') as f:
                                expectedContent = f.read()
                        with open(outputFiles[0], 'r') as f:
                                outContent = f.read()
                        self.assertEqual(outContent, expectedContent)
                except Exception:
                        raise
                finally:
                        # Erase generated files
                        import glob
                        for f in glob.glob(baseOutFile + "*"):
                                os.remove(f)


#
# MAIN
#

if __name__ == '__main__':
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input', help="Input file containing python code")
        parser.add_argument('-o', '--output', help="Output file written in SCOP format")
        args = parser.parse_args()

        if args.input and args.output:
                Py2Scop.translate(args.input, args.output)
        elif args.input or args.output:
                print("ERROR: Invalid arguments.")
                print(" - Add input and output parameters to invoke the main class")
                print(" - Add no arguments to invoke unit tests")
                print("Aborting...")
        else:
                # Test mode
                print("PERFORMING ALL TESTS")
                unittest.main()
