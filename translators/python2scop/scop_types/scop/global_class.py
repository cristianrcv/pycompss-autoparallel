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

        def write(self, f):
                # Write header
                print("# =============================================== Global", file = f)

                # Write language
                print("# Language", file = f)
                print(str(self.language), file = f)
                print("", file = f)

                # Print context
                print("# Context", file = f)
                if self.context != None:
                        self.context.write(f)

                # Print parameters
                print("# Parameters are provided", file = f)
                if self.parameters != None:
                        self.parameters.write(f)


import unittest
class testGlobal(unittest.TestCase):

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

        def test_print(self):
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
                fileName = "global_test.out"
                with open(fileName, 'w') as f:
                        g.write(f)

                # Check file content
                expected = "# =============================================== Global\n# Language\nC\n\n# Context\nCONTEXT\n0 5 0 0 0 3\n\n# Parameters are provided\n1\n<strings>\nmSize kSize nSize\n</strings>\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()
        
