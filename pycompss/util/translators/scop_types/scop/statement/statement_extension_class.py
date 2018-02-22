#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


class StatementExtension(object):
        """
        Represents an Extension within a Statement

        Attributes:
                - originalIterators : List of original iterators
                - expr : Statement body expression
        """

        def __init__(self, originalIterators=None, expr=None):
                self.originalIterators = originalIterators
                self.expr = expr

        def get_number_original_iterators(self):
                if self.originalIterators is not None:
                        return len(self.originalIterators)
                else:
                        return -1

        def get_original_iterators(self):
                return self.originalIterators

        def get_expr(self):
                return self.expr

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Skip body header, empty lines and annotations
                while index < len(content) and (content[index].startswith('<') or content[index].startswith('#') or content[index] == '\n'):
                        index = index + 1

                # Skip iters size
                # iters_size = int(content[index].strip())
                index = index + 1

                # Skip empty lines and annotations
                while index < len(content) and (content[index].startswith('#') or content[index] == '\n'):
                        index = index + 1

                # Process iterators
                iters = content[index].split()
                index = index + 1

                # Skip empty lines and annotations
                while index < len(content) and (content[index].startswith('#') or content[index] == '\n'):
                        index = index + 1

                # Process expression
                expr = content[index].strip()
                index = index + 1

                # Skip footer, empty lines, and any annotation
                while index < len(content) and (content[index].startswith('</') or content[index].startswith('#') or content[index] == '\n'):
                        index = index + 1

                # Build statement extension
                se = StatementExtension(iters, expr)

                # Return structure
                return se, index

        def write_os(self, f):
                # Print header
                print("<body>", file=f)

                # Print number of original iterators
                print("# Number of original iterators", file=f)
                if self.originalIterators is not None:
                        print(str(len(self.originalIterators)), file=f)
                else:
                        print("0", file=f)

                # Print original iterators
                print("# List of original iterators", file=f)
                line = ""
                if self.originalIterators is not None:
                        for elem in self.originalIterators:
                                line = line + str(elem) + " "
                print(line, file=f)

                # Print statement expression
                print("# Statement body expression", file=f)
                print(self.expr, file=f)

                # Print footer
                print("</body>", file=f)


#
# UNIT TESTS
#

class TestStatementExtension(unittest.TestCase):

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

                try:
                        # Generate file
                        fileName = "extension_test.out"
                        with open(fileName, 'w') as f:
                                extension.write_os(f)

                        # Check file content
                        expected = "<body>\n# Number of original iterators\n3\n# List of original iterators\ni j k \n# Statement body expression\nc[i][j] += a[i][k]*b[k][j];\n</body>\n"
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
                sExtFile = dirPath + "/tests/statement_extension_test.expected.scop"
                with open(sExtFile, 'r') as f:
                        content = f.readlines()

                # Read from file
                ext, index = StatementExtension.read_os(content, 0)

                # Check index value
                self.assertEqual(index, len(content))

                # Check StatementExtension object content
                try:
                        # Write to file
                        outputFile = dirPath + "/tests/statement_extension_test.out.scop"
                        with open(outputFile, 'w') as f:
                                ext.write_os(f)

                        # Check file content
                        with open(sExtFile, 'r') as f:
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
