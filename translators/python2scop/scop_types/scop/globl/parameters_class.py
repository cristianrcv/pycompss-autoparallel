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

        def __init__(self, parameters = []):
                self.parameters = parameters

        def get_parameters(self):
                return self.parameters

        def write(self, f):
                # Print header
                print(str(len(self.parameters)), file = f)
                for param in self.parameters:
                        param.write(f)
                print("", file = f)

import unittest
class testParameters(unittest.TestCase):

        def test_empty(self):
                params = Parameters()
                self.assertEqual(params.get_parameters(), [])

        def test_full(self):
                from parameters import Parameter
                t = "strings"
                val = "mSize kSize nSize"
                p1 = Parameter(t, val)
                params = Parameters([p1])

                self.assertEqual(params.get_parameters(), [p1])

        def test_print(self):
                from parameters import Parameter
                t = "strings"
                val = "mSize kSize nSize"
                p1 = Parameter(t, val)
                params = Parameters([p1])

                # Generate file
                fileName = "parameters_test.out"
                with open(fileName, 'w') as f:
                        params.write(f)

                # Check file content
                expected = "1\n<strings>\nmSize kSize nSize\n</strings>\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()

