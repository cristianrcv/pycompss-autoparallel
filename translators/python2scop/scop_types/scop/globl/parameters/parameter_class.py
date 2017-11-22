#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

class Parameter(object):
        """
        Represents a global parameter

        Attributes:
                - ptype : Type of the parameter
                - pvalue : Value of the parameter
        """

        def __init__(self, ptype = None, pvalue = None):
                self.ptype = ptype
                self.pvalue = pvalue

        def get_type(self):
                return self.ptype

        def get_value(self):
                return self.pvalue

        def write(self, f):
                # Print header
                print("<" + str(self.ptype) + ">", file = f)
                print(str(self.pvalue), file = f)
                print("</" + str(self.ptype) + ">", file = f)


import unittest
class testParameter(unittest.TestCase):

        def test_empty(self):
                param = Parameter()
                self.assertEqual(param.get_type(), None)
                self.assertEqual(param.get_value(), None)

        def test_full(self):
                t = "strings"
                val = "mSize kSize nSize"
                param = Parameter(t, val)

                self.assertEqual(param.get_type(), t)
                self.assertEqual(param.get_value(), val)

        def test_print(self):
                t = "strings"
                val = "mSize kSize nSize"
                param = Parameter(t, val)

                # Generate file
                fileName = "parameter_test.out"
                with open(fileName, 'w') as f:
                        param.write(f)

                # Check file content
                expected = "<strings>\nmSize kSize nSize\n</strings>\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()

