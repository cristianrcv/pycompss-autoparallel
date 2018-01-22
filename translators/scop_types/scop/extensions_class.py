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

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process optional field: scatnames
                from extensions import Scatnames
                scatnames = None
                if content[index] == '<scatnames>\n':
                        scatnames, index = Scatnames.read_os(content, index)

                # Process mandatory field: arrays
                from extensions import Arrays
                arrays, index = Arrays.read_os(content, index)

                # Skip empty lines and any annotation
                while index < len(content) and (content[index].startswith('#') or content[index] == '\n'):
                        index = index + 1

                # Process optional field: coordinates
                from extensions import Coordinates
                coordinates = None
                if index < len(content) and content[index] == '<coordinates>\n':
                        coordinates, index = Coordinates.read_os(content, index)

                # Build Extensions
                ext = Extensions(scatnames, arrays, coordinates)

                # Return structure
                return ext, index

        @staticmethod
        def read_py(f):
                pass

        def write_os(self, f):
                # Write header
                print("# =============================================== Extensions", file = f)

                # Write scatnames
                if self.scatnames != None:
                        self.scatnames.write_os(f)

                # Write arrays
                if self.arrays != None:
                        self.arrays.write_os(f)

                # Write coordinates
                if self.coordinates != None:
                        self.coordinates.write_os(f)

        def write_py(self, f):
                pass


#
# UNIT TESTS
#

import unittest
class TestExtensions(unittest.TestCase):

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

        def test_write_os(self):
                from extensions import Scatnames, Arrays, Coordinates
                scatnames = Scatnames(["b0", "i", "b1", "j", "b2", "k", "b3"])
                arrays = Arrays(["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"])
                coordinates = Coordinates("example2_src_matmul.cc", 72, 0, 80, 0, 8)
                ext = Extensions(scatnames, arrays, coordinates)

                # Generate file
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                outputFile = dirPath + "/tests/extensions_test.out.scop"
                expectedFile = dirPath + "/tests/extensions_test.expected.scop"
                with open(outputFile, 'w') as f:
                        ext.write_os(f)

                # Check file content
                with open(expectedFile, 'r') as f:
                        expectedContent = f.read()
                with open(outputFile, 'r') as f:
                        outputContent = f.read()
                self.assertEqual(outputContent, expectedContent)

                # Erase file
                import os
                os.remove(outputFile)


#
# MAIN
#

if __name__ == '__main__':
        unittest.main()

