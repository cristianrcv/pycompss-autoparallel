#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


class Arrays(object):
        """
        Represents an array object inside the extensions section

        Attributes:
                - values : array values
        """

        def __init__(self, values=None):
                self.values = values

        def get_values(self):
                return self.values

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n' or content[index] == '<arrays>\n':
                        index = index + 1

                # Process mandatory field: num_arrays
                num_arrays = int(content[index])
                index = index + 1

                # Skip empty lines and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process values (Can be one per line with index or all in one line)
                inputValues = content[index].split()

                if len(inputValues) == num_arrays:
                        # All values in a single line
                        values = inputValues
                else:
                        # Values one per line with index
                        values = [None] * num_arrays
                        num_values = 0
                        while num_values < num_arrays and index < len(content):
                                inputValues = content[index].split()
                                value_index = int(inputValues[0]) - 1
                                value_value = inputValues[1]
                                values[value_index] = value_value
                                index = index + 1
                                num_values = num_values + 1

                # Skip empty lines, any annotation, and footer
                while index < len(content) and (content[index].startswith('#') or content[index] == '\n' or content[index] == '</arrays>\n'):
                        index = index + 1

                # Build Arrays
                arrays = Arrays(values)

                # Return structure
                return arrays, index

        def write_os(self, f):
                # Print header
                print("<arrays>", file=f)

                if self.values is not None:
                        # Print number of arrays
                        print("# Number of arrays", file=f)
                        print(str(len(self.values)), file=f)

                        # Print arrays
                        print("# Mapping array-identifiers/array-names", file=f)
                        index = 1
                        for value in self.values:
                                print(str(index) + " " + str(value), file=f)
                                index = index + 1

                # Print footer
                print("</arrays>", file=f)
                print("", file=f)


#
# UNIT TESTS
#

class TestArrays(unittest.TestCase):

        def test_empty(self):
                a = Arrays()

                self.assertEqual(a.get_values(), None)

        def test_full(self):
                values = ["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"]
                a = Arrays(values)

                self.assertEqual(a.get_values(), values)

        def test_write_os(self):
                values = ["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"]
                a = Arrays(values)

                try:
                        # Generate file
                        fileName = "arrays_test.out"
                        with open(fileName, 'w') as f:
                                a.write_os(f)

                        # Check file content
                        expected = "<arrays>\n# Number of arrays\n9\n# Mapping array-identifiers/array-names\n1 i\n2 mSize\n3 j\n4 kSize\n5 k\n6 nSize\n7 c\n8 a\n9 b\n</arrays>\n\n"
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
                arraysFile = dirPath + "/tests/arrays_test.expected.scop"
                with open(arraysFile, 'r') as f:
                        content = f.readlines()

                # Read from file
                arrays, index = Arrays.read_os(content, 0)

                # Check index value
                self.assertEqual(index, len(content))

                # Check Arrays object content
                try:
                        # Write to file
                        outputFile = dirPath + "/tests/arrays_test.out.scop"
                        with open(outputFile, 'w') as f:
                                arrays.write_os(f)

                        # Check file content
                        with open(arraysFile, 'r') as f:
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
