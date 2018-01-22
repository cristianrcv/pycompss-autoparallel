#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function


#
# Translator class
#

class Scop2PScop2Py(object):

        @staticmethod
        def translate(source, output):
                #
                # Inputs an OpenScop representation to PLUTO that generates
                # its parallel version in Python
                #
                # Arguments:
                #       - source : OpenScop source file path
                #       - output : Python output file path
                # Return:
                # Raise:
                #       - Scop2PScop2PyException
                #

                # PLUTO binary location
                PLUTO_DIR = "/opt/pluto/bin/" #"/opt/COMPSs/Dependencies/pluto/"
                PLC = PLUTO_DIR + "polycc"

                # Pluto binary options
                mandatory_opts = [ "--readscop", "-o " + output ]
                basic_opts = [ "--tile", "--parallel" ]
                adv_opts = [] # ["--rar", "--lastwriter"]
                mode_opts = [] # ["--silent"] # ["--debug"] # ["--moredebug"]

                # Construct binary call
                cmd = [PLC, source] + mandatory_opts + basic_opts + adv_opts + mode_opts
                if __debug__:
                        print("[scop2pscop2py] Command: " + str(cmd))

                # Call binary
                try:
                        from subprocess import Popen, PIPE
                        process = Popen(cmd, stdin = None, stdout = PIPE, stderr = PIPE, shell = False)
        
                        # Wait for completion and capture output, error and exit value
                        stdout, stderr = process.communicate()
                        exit_value = process.returncode
                except Exception as e:
                        raise Scop2PScop2PyException("[ERROR] PLUTO binary execution error", e)

                # Check process values
                if exit_value != 0:
                        print("[ERROR] Pluto binary returned non-zero exit value: " + str(exit_value))
                        print("[scop2pscop2py] Binary output:")
                        print(stdout)
                        print("[scop2pscop2py] Binary error:")
                        print(stderr)
                        raise Scop2PScop2PyException("[ERROR] Pluto binary exit value = " + str(exit_value), None)

                # Finish
                if __debug__:
                        print("[scop2pscop2py] Pluto binary successfull")
                        print("[scop2pscop2py] Binary output:")
                        print(stdout)


#
# Exception Class
#

class Scop2PScop2PyException(Exception):

        def __init__(self, msg, nested_exception):
                self.msg = msg
                self.nested_exception = nested_exception

        def __str__(self):
                return "Exception on Scop2PScop2Py.translate method.\n Message: " + str(self.msg) + "\n Nested Exception: " + str(self.nested_exception)


#
# UNIT TEST CASES
#

import unittest
class TestScop2PScop2Py(unittest.TestCase):

        def test_matmul(self):
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))

                # Source OpenScop file
                source_file = dirPath + "/tests/test1_matmul.src.scop"

                # Output Python file
                output_file = dirPath + "/tests/test1_matmul.output.python"

                # Expected output file
                expected_file = dirPath + "/tests/test1_matmul.expected.python"

                # Generate scop2pscop2py
                Scop2PScop2Py.translate(source_file, output_file)

                # Check file content
                with open(expected_file, 'r') as f:
                        expected_content = f.read()
                with open(output_file, 'r') as f:
                        output_content = f.read()
                self.assertEqual(output_content, expected_content)

                # Erase output file
                os.remove(output_file)

        def test_seidel(self):
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))

                # Source OpenScop file
                source_file = dirPath + "/tests/test2_seidel.src.scop"

                # Output Python file
                output_file = dirPath + "/tests/test2_seidel.output.python"

                # Expected output file
                expected_file = dirPath + "/tests/test2_seidel.expected.python"

                # Generate scop2pscop2py
                Scop2PScop2Py.translate(source_file, output_file)

                # Check file content
                with open(expected_file, 'r') as f:
                        expected_content = f.read()
                with open(output_file, 'r') as f:
                        output_content = f.read()
                self.assertEqual(output_content, expected_content)

                # Erase output file
                os.remove(output_file)


#
# MAIN FOR UNIT TEST
#

if __name__ == '__main__':
        unittest.main()

