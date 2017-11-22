#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

class Extensions(object):
        """
        Represents an Extension clause within a SCOP

        Attributes:
                - scatnames : Scatnames
                - arrays : Arrays
                - Coordinates : Coordinates
        """

        def __init__(self, scatnames = None, arrays = None, coordinates = None):
                self.scatnames = scatnames
                self.arrays = arrays
                self.coordinates = coordinates

        def get_scatnames(self):
                return self.scatnames

        def get_arrays(self):
                return self.arrays

        def get_coordinates(self):
                return self.coordinates

        def write(self, f):
                # Write header
                print("# =============================================== Extensions", file = f)

                # Write scatnames
                if self.scatnames != None:
                        self.scatnames.write(f)

                # Write arrays
                if self.arrays != None:
                        self.arrays.write(f)

                # Write coordinates
                if self.coordinates != None:
                        self.coordinates.write(f)


import unittest
class testExtensions(unittest.TestCase):

        def test_empty(self):
                ext = Extensions()

                self.assertEqual(ext.get_scatnames(), None)
                self.assertEqual(ext.get_arrays(), None)
                self.assertEqual(ext.get_coordinates(), None)

        def test_full(self):
                from extensions import Scatnames, Arrays, Coordinates
                scatnames = Scatnames(["b0", "i", "b1", "j", "b2", "k", "b3"])
                arrays = Arrays(["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"])
                coordinates = Coordinates("example2_src_matmul.cc", 72, 0, 80, 0, 8)
                ext = Extensions(scatnames, arrays, coordinates)

                self.assertEqual(ext.get_scatnames(), scatnames)
                self.assertEqual(ext.get_arrays(), arrays)
                self.assertEqual(ext.get_coordinates(), coordinates)

        def test_print(self):
                from extensions import Scatnames, Arrays, Coordinates
                scatnames = Scatnames(["b0", "i", "b1", "j", "b2", "k", "b3"])
                arrays = Arrays(["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"])
                coordinates = Coordinates("example2_src_matmul.cc", 72, 0, 80, 0, 8)
                ext = Extensions(scatnames, arrays, coordinates)

                # Generate file
                fileName = "extensions_test.out"
                with open(fileName, 'w') as f:
                        ext.write(f)

                # Check file content
                expected = "# =============================================== Extensions\n<scatnames>\nb0 i b1 j b2 k b3 \n</scatnames>\n\n<arrays>\n# Number of arrays\n9\n# Mapping array-identifiers/array-names\n1 i\n2 mSize\n3 j\n4 kSize\n5 k\n6 nSize\n7 c\n8 a\n9 b\n</arrays>\n\n<coordinates>\n# File name\nexample2_src_matmul.cc\n# Starting line and column\n72 0\n# Ending line and column\n80 0\n# Identation\n8\n</coordinates>\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()

