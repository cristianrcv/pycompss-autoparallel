#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

class Global(object):
        """
        Represents a Global clause within a SCOP

        Attributes:
                - language : Language
                - context : Global context
                - parameters : Global list of parameters
        """

        def __init__(self, language = None, context = None, parameters = None):
                self.language = language
                self.context = context
                self.parameters = parameters

        def get_language(self):
                return self.language

        def get_context(self):
                return self.context

        def get_parameters(self):
                return self.parameters

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process mandatory field: language
                language = content[index]
                index = index + 1

                # Process context
                from globl import Context
                context, index = Context.read_os(content, index)

                # Process parameters
                from globl import Parameters
                parameters, index = Parameters.read_os(content, index)

                # Build Global
                g = Global(language, context, parameters)

                # Return structure
                return g, index

        @staticmethod
        def read_py(f):
                pass

        def write_os(self, f):
                # Write header
                print("# =============================================== Global", file = f)

                # Write language
                print("# Language", file = f)
                print(str(self.language), file = f)
                print("", file = f)

                # Print context
                print("# Context", file = f)
                if self.context != None:
                        self.context.write_os(f)

                # Print parameters
                print("# Parameters are provided", file = f)
                if self.parameters != None:
                        self.parameters.write_os(f)

        def write_py(self, f):
                pass


#
# UNIT TESTS
#

import unittest
class TestGlobal(unittest.TestCase):

        def test_empty(self):
                g = Global()

                self.assertEqual(g.get_language(), None)
                self.assertEqual(g.get_context(), None)
                self.assertEqual(g.get_parameters(), None)

        def test_full(self):
                lang = "C"

                from globl import Context, ContextType
                context = Context(ContextType.CONTEXT, 0, 5, 0, 0, 0, 3)

                from globl.parameters import Parameter
                from globl import Parameters
                t = "strings"
                val = "mSize kSize nSize"
                p1 = Parameter(t, val)
                params = Parameters([p1])

                g = Global(lang, context, params)

                self.assertEqual(g.get_language(), lang)
                self.assertEqual(g.get_context(), context)
                self.assertEqual(g.get_parameters(), params)

        def test_write_os(self):
                lang = "C"

                from globl import Context, ContextType
                context = Context(ContextType.CONTEXT, 0, 5, 0, 0, 0, 3)

                from globl.parameters import Parameter
                from globl import Parameters
                t = "strings"
                val = "mSize kSize nSize"
                p1 = Parameter(t, val)
                params = Parameters([p1])

                g = Global(lang, context, params)

                # Generate file
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                outputFile = dirPath + "/tests/global_test.out.scop"
                expectedFile = dirPath + "/tests/global_test.expected.scop"
                with open(outputFile, 'w') as f:
                        g.write_os(f)

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

