#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

class Parameters(object):
        """
        Represents a list of global Parameter

        Attributes:
                - parameters : List of global Parameter
        """

        def __init__(self, parameters = None):
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
                from parameters import Parameter
                params = []
                for _ in range(num_params):
                        p, index = Parameter.read_os(content, index)
                        params.append(p)

                # Build Parameters
                parameters = Parameters(params)

                # Return structure
                return parameters, index

        @staticmethod
        def read_py(f):
                pass

        def write_os(self, f):
                if self.parameters != None:
                        # Print number of parameter
                        print(str(len(self.parameters)), file = f)

                        # Print parameters
                        for param in self.parameters:
                                param.write_os(f)

                print("", file = f)

        def write_py(self, f):
                pass


#
# UNIT TESTS
#

import unittest
class TestParameters(unittest.TestCase):

        def test_empty(self):
                params = Parameters()
                self.assertEqual(params.get_parameters(), None)

        def test_full(self):
                from parameters import Parameter
                t = "strings"
                val = "mSize kSize nSize"
                p1 = Parameter(t, val)
                params = Parameters([p1])

                self.assertEqual(params.get_parameters(), [p1])

        def test_write_os(self):
                from parameters import Parameter
                t = "strings"
                val = "mSize kSize nSize"
                p1 = Parameter(t, val)
                params = Parameters([p1])

                # Generate file
                fileName = "parameters_test.out"
                with open(fileName, 'w') as f:
                        params.write_os(f)

                # Check file content
                expected = "1\n<strings>\nmSize kSize nSize\n</strings>\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


#
# MAIN
#

if __name__ == '__main__':
        unittest.main()

