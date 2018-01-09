#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

class StatementExtension(object):
        """
        Represents an Extension within a Statement

        Attributes:
                - originalIterators : List of original iterators
                - expr : Statement body expression
        """

        def __init__(self, originalIterators = None, expr = None):
                self.originalIterators = originalIterators
                self.expr = expr

        def get_number_original_iterators(self):
                if self.originalIterators != None:
                        return len(self.originalIterators)
                else:
                        return -1

        def get_original_iterators(self):
                return self.originalIterators

        def get_expr(self):
                return self.expr

        @staticmethod
        def read_os(content, index):
                pass
                                                                                                                                                                                                                                                                               
        @staticmethod
        def read_py(f):
                pass

        def write_os(self, f):
                # Print header
                print("<body>", file = f)

                # Print number of original iterators
                print("# Number of original iterators", file = f)
                if self.originalIterators != None:
                        print(str(len(self.originalIterators)), file = f)
                else:
                        print("0", file = f)

                # Print original iterators
                print("# List of original iterators", file = f)
                line = ""
                if self.originalIterators != None:
                        for elem in self.originalIterators:
                                line = line + str(elem) + " "
                print(line, file = f)

                # Print statement expression
                print("# Statement body expression", file = f)
                print(self.expr, file = f)

                # Print footer
                print("</body>", file = f)

        def write_py(f):
                pass


import unittest
class testStatementExtension(unittest.TestCase):

        def test_empty(self):
                extension = StatementExtension()
                self.assertEqual(extension.get_number_original_iterators(), -1)
                self.assertEqual(extension.get_original_iterators(), None)
                self.assertEqual(extension.get_expr(), None)

        def test_full(self):
                iterators = ["i", "j", "k"]
                expr = "c[i][j] += a[i][k]*b[k][j];"
                extension = StatementExtension(iterators, expr)
                self.assertEqual(extension.get_number_original_iterators(), 3)
                self.assertEqual(extension.get_original_iterators(), iterators)
                self.assertEqual(extension.get_expr(), expr)

        def test_write_os(self):
                iterators = ["i", "j", "k"]
                expr = "c[i][j] += a[i][k]*b[k][j];"
                extension = StatementExtension(iterators, expr)

                # Generate file
                fileName = "extension_test.out"
                with open(fileName, 'w') as f:
                        extension.write_os(f)

                # Check file content
                expected = "<body>\n# Number of original iterators\n3\n# List of original iterators\ni j k \n# Statement body expression\nc[i][j] += a[i][k]*b[k][j];\n</body>\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()

