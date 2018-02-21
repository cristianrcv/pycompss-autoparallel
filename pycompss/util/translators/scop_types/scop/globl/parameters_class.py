#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


class Parameters(object):
        """
        Represents a list of global Parameter

        Attributes:
                - parameters : List of global Parameter
        """

        def __init__(self, parameters=None):
                self.parameters = parameters

        def get_parameters(self):
                return self.parameters

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process mandatory field: num_params
                num_params = int(content[index])
                index = index + 1

                # Process each parameter
                from pycompss.util.translators.scop_types.scop.globl.parameters.parameter_class import Parameter
                params = []
                for _ in range(num_params):
                        p, index = Parameter.read_os(content, index)
                        params.append(p)

                # Skip empty lines and any annotation
                while index < len(content) and (content[index].startswith('#') or content[index] == '\n'):
                        index = index + 1

                # Build Parameters
                parameters = Parameters(params)

                # Return structure
                return parameters, index

        def write_os(self, f):
                if self.parameters is not None:
                        # Print number of parameter
                        print(str(len(self.parameters)), file=f)

                        # Print parameters
                        for param in self.parameters:
                                param.write_os(f)

                print("", file=f)


#
# UNIT TESTS
#

class TestParameters(unittest.TestCase):

        def test_empty(self):
                params = Parameters()
                self.assertEqual(params.get_parameters(), None)

        def test_full(self):
                from pycompss.util.translators.scop_types.scop.globl.parameters.parameter_class import Parameter
                t = "strings"
                val = ["mSize", "kSize", "nSize"]
                p1 = Parameter(t, val)
                params = Parameters([p1])

                self.assertEqual(params.get_parameters(), [p1])

        def test_write_os(self):
                from pycompss.util.translators.scop_types.scop.globl.parameters.parameter_class import Parameter
                t = "strings"
                val = ["mSize", "kSize", "nSize"]
                p1 = Parameter(t, val)
                params = Parameters([p1])

                try:
                        # Generate file
                        fileName = "parameters_test.out"
                        with open(fileName, 'w') as f:
                                params.write_os(f)

                        # Check file content
                        expected = "1\n<strings>\nmSize kSize nSize\n</strings>\n\n"
                        with open(fileName, 'r') as f:
                                content = f.read()
                        self.assertEqual(content, expected)
                except Exception:
                        raise
                finally:
                        # Erase file
                        import os
                        os.remove(fileName)

        def test_read_os(self):
                # Store all file content
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                parametersFile = dirPath + "/tests/parameters_test.expected.scop"
                with open(parametersFile, 'r') as f:
                        content = f.readlines()

                # Read from file
                pars, index = Parameters.read_os(content, 0)

                # Check index value
                self.assertEqual(index, len(content))

                # Check Parameters object content
                try:
                        # Write to file
                        outputFile = dirPath + "/tests/parameters_test.out.scop"
                        with open(outputFile, 'w') as f:
                                pars.write_os(f)

                        # Check file content
                        with open(parametersFile, 'r') as f:
                                expectedContent = f.read()
                        with open(outputFile, 'r') as f:
                                outputContent = f.read()
                        self.assertEqual(outputContent, expectedContent)
                except Exception:
                        raise
                finally:
                        # Remove test file
                        os.remove(outputFile)


#
# MAIN
#

if __name__ == '__main__':
        unittest.main()
