#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


class Coordinates(object):
        """
        Represents a coordinates object inside the extensions section

        Attributes:
                - fileName : Name of the original source file
                - startLine : Start line of the scop tag in the original source file
                - startCol : Start column of the scop tag in the original source file
                - endLine : End line of the scop tag in the original source file
                - endCol : End column of the scop tag in the original source file
                - ident : Identation value in the original source file
        """

        def __init__(self, fileName=None, startLine=-1, startCol=-1, endLine=-1, endCol=-1, ident=-1):
                self.fileName = fileName
                self.startLine = startLine
                self.startCol = startCol
                self.endLine = endLine
                self.endCol = endCol
                self.ident = ident

        def get_file_name(self):
                return self.fileName

        def get_start_line(self):
                return self.startLine

        def get_start_column(self):
                return self.startCol

        def get_end_line(self):
                return self.endLine

        def get_end_column(self):
                return self.endCol

        def get_identation(self):
                return self.ident

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n' or content[index] == '<coordinates>\n':
                        index = index + 1

                # Process mandatory field: fileName
                fileName = content[index]
                index = index + 1

                # Skip empty lines and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process mandatory field: start
                startLine, startCol = content[index].split()
                index = index + 1

                # Skip empty lines and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process mandatory field: end
                endLine, endCol = content[index].split()
                index = index + 1

                # Skip empty lines and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process mandatory field: identation
                identation = content[index].split()
                index = index + 1

                # Skip empty lines, any annotation, and footer
                while index < len(content) and (content[index].startswith('#') or content[index] == '\n' or content[index] == '</coordinates>\n'):
                        index = index + 1

                # Build Coordinates
                c = Coordinates(fileName, startLine, startCol, endLine, endCol, identation)

                # Return structure
                return c, index

        @staticmethod
        def read_py(f):
                pass

        def write_os(self, f):
                # Print header
                print("<coordinates>", file=f)

                # Print file name
                print("# File name", file=f)
                print(str(self.fileName), file=f)

                # Print starting line and column
                print("# Starting line and column", file=f)
                print(str(self.startLine) + " " + str(self.startCol), file=f)

                # Print ending line and column
                print("# Ending line and column", file=f)
                print(str(self.endLine) + " " + str(self.endCol), file=f)

                # Print identation
                print("# Identation", file=f)
                print(str(self.ident), file=f)

                # Print footer
                print("</coordinates>", file=f)
                print("", file=f)

        def write_py(self, f):
                pass


#
# UNIT TESTS
#

class TestCoordinates(unittest.TestCase):

        def test_empty(self):
                c = Coordinates()

                self.assertEqual(c.get_file_name(), None)
                self.assertEqual(c.get_start_line(), -1)
                self.assertEqual(c.get_start_column(), -1)
                self.assertEqual(c.get_end_line(), -1)
                self.assertEqual(c.get_end_column(), -1)
                self.assertEqual(c.get_identation(), -1)

        def test_full(self):
                fileName = "example2_src_matmul.cc"
                sl = 72
                sc = 0
                el = 80
                ec = 0
                ident = 8
                c = Coordinates(fileName, sl, sc, el, ec, ident)

                self.assertEqual(c.get_file_name(), fileName)
                self.assertEqual(c.get_start_line(), sl)
                self.assertEqual(c.get_start_column(), sc)
                self.assertEqual(c.get_end_line(), el)
                self.assertEqual(c.get_end_column(), ec)
                self.assertEqual(c.get_identation(), ident)

        def test_write_os(self):
                fn = "example2_src_matmul.cc"
                sl = 72
                sc = 0
                el = 80
                ec = 0
                ident = 8
                c = Coordinates(fn, sl, sc, el, ec, ident)

                # Generate file
                fileName = "coordinates_test.out"
                with open(fileName, 'w') as f:
                        c.write_os(f)

                # Check file content
                expected = "<coordinates>\n# File name\nexample2_src_matmul.cc\n# Starting line and column\n72 0\n# Ending line and column\n80 0\n# Identation\n8\n</coordinates>\n\n"
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
