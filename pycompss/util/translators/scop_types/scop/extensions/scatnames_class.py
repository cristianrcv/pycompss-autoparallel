#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


class Scatnames(object):
        """
        Represents an scatname object inside the extensions section

        Attributes:
                - names : Array of scatnames
        """

        def __init__(self, names=None):
                self.names = names

        def get_names(self):
                return self.names

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n' or content[index] == '<scatnames>\n':
                        index = index + 1

                # Process mandatory field: scatnames
                names = content[index].split()
                index = index + 1

                # Skip empty lines, any annotation, and footer
                while index < len(content) and (content[index].startswith('#') or content[index] == '\n' or content[index] == '</scatnames>\n'):
                        index = index + 1

                # Build Scatnames
                scatnames = Scatnames(names)

                # Return structure
                return scatnames, index

        def write_os(self, f):
                # Print header
                print("<scatnames>", file=f)

                # Print arrays
                if self.names is not None:
                        line = ""
                        for val in self.names:
                                line = line + str(val) + " "
                        print(line, file=f)

                # Print footer
                print("</scatnames>", file=f)
                print("", file=f)


#
# UNIT TESTS
#

class TestScatnames(unittest.TestCase):

        def test_empty(self):
                s = Scatnames()

                self.assertEqual(s.get_names(), None)

        def test_full(self):
                names = ["b0", "i", "b1", "j", "b2", "k", "b3"]
                s = Scatnames(names)

                self.assertEqual(s.get_names(), names)

        def test_write_os(self):
                names = ["b0", "i", "b1", "j", "b2", "k", "b3"]
                s = Scatnames(names)

                try:
                        # Generate file
                        fileName = "scatnames_test.out"
                        with open(fileName, 'w') as f:
                                s.write_os(f)

                        # Check file content
                        expected = "<scatnames>\nb0 i b1 j b2 k b3 \n</scatnames>\n\n"
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
                scatnamesFile = dirPath + "/tests/scatnames_test.expected.scop"
                with open(scatnamesFile, 'r') as f:
                        content = f.readlines()

                # Read from file
                scatnames, index = Scatnames.read_os(content, 0)

                # Check index value
                self.assertEqual(index, len(content))

                # Check Scatnames object content
                try:
                        # Write to file
                        outputFile = dirPath + "/tests/scatnames_test.out.scop"
                        with open(outputFile, 'w') as f:
                                scatnames.write_os(f)

                        # Check file content
                        with open(scatnamesFile, 'r') as f:
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
