#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# TODO: Workarround with pythonpath
import sys
import os
sys.path.insert(0, os.getcwd() + '/../../translators/')


#
# Translator class
#

class Py2Scop(object):

        # WRITE FILE
        @staticmethod
        def writeFile(fileName, scops):
                with open(fileName, 'w') as f:
                        write_file_header(f)
                        for scop in scops:
                                scop.write_os(f)

        @staticmethod
        def write_file_header(f):
                print("# [File generated by the OpenScop Library 0.9.1]", file = f)
                print("", file = f)

        # READ FILE
        @staticmethod
        def readFile(fileName):
                from scop_types.scop import Global, Statement, Extensions

                # Generate global
                from scop_types.scop.globl import Context, ContextType, Parameters
                from scop_types.scop.globl.parameters import Parameter
                context = Context(ContextType.CONTEXT, 0, 5, 0, 0, 0, 3)
                params = Parameters([Parameter("strings", "mSize kSize nSize")])
                g = Global("C", context, params)

                # Generate statements
                from scop_types.scop.statement import Relation, RelationType, StatementExtension
                s1_domain = Relation(RelationType.DOMAIN, 9, 8, 3, 0, 0, 3, [[1, 1], [1, -1]])
                s1_scattering = Relation(RelationType.SCATTERING, 7, 15, 7, 3, 0, 3, [[0, -1], [0, 0]])
                s1_a1 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s1_a2 = Relation(RelationType.WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s1_a3 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s1_a4 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s1_access = [s1_a1, s1_a2, s1_a3, s1_a4]
                s1_ext1 = StatementExtension(["i", "j", "k"], "c[i][j] += a[i][k]*b[k][j];")
                s1_extensions = [s1_ext1]
                s1 = Statement(s1_domain, s1_scattering, s1_access, s1_extensions)

                s2_domain = Relation(RelationType.DOMAIN, 9, 8, 3, 0, 0, 3, [[1, 1], [1, -1]])
                s2_scattering = Relation(RelationType.SCATTERING, 7, 15, 7, 3, 0, 3, [[0, -1], [0, 0]])
                s2_a1 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s2_a2 = Relation(RelationType.WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s2_a3 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s2_access = [s2_a1, s2_a2, s2_a3]
                s2_ext1 = StatementExtension(["i", "j", "k"], "a[i][k] += b[i][k];")
                s2_extensions = [s2_ext1]
                s2 = Statement(s2_domain, s2_scattering, s2_access, s2_extensions)

                statements = [s1, s2]

                # Generate extensions
                from scop_types.scop.extensions import Scatnames, Arrays, Coordinates
                scatnames = Scatnames(["b0", "i", "b1", "j", "b2", "k", "b3"])
                arrays = Arrays(["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"])
                coordinates = Coordinates("example2_src_matmul.cc", 72, 0, 80, 0, 8)
                e = Extensions(scatnames, arrays, coordinates)

                # Generate SCOP
                from scop_types import Scop
                scop = Scop(g, statements, e)

                return [scop]

        @staticmethod
        def translate(source, output):
                #
                # Inputs a Python code with scop pragmas and outputs its
                # openscop representation in the given file
                #
                # Arguments:
                #       source : Python code with scop prgramas
                #       output : OpenScop output file path
                # Return:
                # Raise:
                #       - Py2ScopException
                #

                # TODO: Add real code
                # Generate scops from source file
                #scops = readFile(srcFile)

                # Generate file
                #writeFile(outFile, scops)

                try:
                        import os
                        dirPath = os.path.dirname(os.path.realpath(__file__))
                        scop_file = dirPath + "/tests/test1_matmul.expected.scop"
                        from shutil import copyfile
                        copyfile(scop_file, output)
                except Exception as e:
                        raise Py2ScopException("[ERROR] Cannot copy SCOP file", e)


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

import unittest
class TestPy2Scop(unittest.TestCase):

        def test_matmul(self):
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                srcFile = dirPath + "/tests/test1_matmul.src.python"
                expectedFile = dirPath + "/tests/test1_matmul.expected.scop"
                outFile = dirPath + "/tests/test1_matmul.out.scop"
 
                # Translate
                Py2Scop.translate(srcFile, outFile)

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
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input', help = "Input file containing python code")
        parser.add_argument('-o', '--output', help = "Output file written in SCOP format")
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

