#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

class Arrays(object):
        """
        Represents an array object inside the extensions section

        Attributes:
                - values : array values
        """

        def __init__(self, values = None):
                self.values = values

        def get_values(self):
                return self.values

        def write(self, f):
                # Print header
                print("<arrays>", file = f)

                if self.values != None:
                        # Print number of arrays
                        print("# Number of arrays", file = f)
                        print(str(len(self.values)), file = f)

                        # Print arrays
                        print("# Mapping array-identifiers/array-names", file = f)
                        index = 1
                        for value in self.values:
                                print(str(index) + " " + str(value), file = f)
                                index = index + 1

                # Print footer
                print("</arrays>", file = f)
                print("", file = f)

import unittest
class testArrays(unittest.TestCase):

        def test_empty(self):
                a = Arrays()

                self.assertEqual(a.get_values(), None)

        def test_full(self):
                values = ["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"]
                a = Arrays(values)

                self.assertEqual(a.get_values(), values)

        def test_print(self):
                values = ["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"]
                a = Arrays(values)

                # Generate file
                fileName = "arrays_test.out"
                with open(fileName, 'w') as f:
                        a.write(f)

                # Check file content
                expected = "<arrays>\n# Number of arrays\n9\n# Mapping array-identifiers/array-names\n1 i\n2 mSize\n3 j\n4 kSize\n5 k\n6 nSize\n7 c\n8 a\n9 b\n</arrays>\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()

