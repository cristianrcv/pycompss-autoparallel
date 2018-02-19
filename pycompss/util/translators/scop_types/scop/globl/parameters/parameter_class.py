#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


class Parameter(object):
        """
        Represents a global parameter

        Attributes:
                - ptype : Type of the parameter
                - pvalue : Value of the parameter
        """

        def __init__(self, ptype=None, values_list=None):
                self.ptype = ptype
                if values_list is None:
                        self.pvalue = None
                else:
                        self.pvalue = " ".join(values_list)

        def get_type(self):
                return self.ptype

        def get_value(self):
                return self.pvalue

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process optional header
                ptype = None
                if content[index].startswith('<'):
                        ptype = content[index][1:-1]
                        index = index + 1

                # Process mandatory field: value
                pvalue = content[index]
                index = index + 1

                # Process optional footer
                if content[index].startswith('</'):
                        index = index + 1

                # Build Parameter
                p = Parameter(ptype, pvalue)

                # Return structure
                return p, index

        @staticmethod
        def read_py(f):
                pass

        def write_os(self, f):
                # Print header
                print("<" + str(self.ptype) + ">", file=f)
                print(str(self.pvalue), file=f)
                print("</" + str(self.ptype) + ">", file=f)

        def write_py(self, f):
                pass


#
# UNIT TESTS
#

class TestParameter(unittest.TestCase):

        def test_empty(self):
                param = Parameter()
                self.assertEqual(param.get_type(), None)
                self.assertEqual(param.get_value(), None)

        def test_full(self):
                t = "strings"
                val_list = ["mSize", "kSize", "nSize"]
                param = Parameter(t, val_list)

                val = "mSize kSize nSize"
                self.assertEqual(param.get_type(), t)
                self.assertEqual(param.get_value(), val)

        def test_write_os(self):
                t = "strings"
                val_list = ["mSize", "kSize", "nSize"]
                param = Parameter(t, val_list)

                # Generate file
                fileName = "parameter_test.out"
                with open(fileName, 'w') as f:
                        param.write_os(f)

                # Check file content
                expected = "<strings>\nmSize kSize nSize\n</strings>\n"
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
