#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

class Scop(object):
        """
        Represents a SCOP

        Attributes:
                - globl : Global SCOP properties
                - statements : List of Statement
                - extensions : Extensions properties
        """

        def __init__(self, globl = None, statements = None, extensions = None):
                self.globl = globl
                self.statements = statements
                self.extensions = extensions

        def get_global(self):
                return self.globl

        def get_statements(self):
                return self.statements

        def get_extensions(self):
                return self.extensions

        def write(self, f):
                # Write header
                print("<OpenScop>", file = f)
                print("", file = f)

                # Print global
                if self.globl != None:
                        self.globl.write(f)

                if self.statements != None:
                        # Print number of statements
                        print("# Number of statements", file = f)
                        print(str(len(self.statements)), file = f)
                        print("", file = f)

                        # Print all statements
                        index = 1
                        for s in self.statements:
                                s.write(f, index)
                                index = index + 1

                # Print extensions
                if self.extensions != None:
                        self.extensions.write(f)

                # Write footer
                print("</OpenScop>", file = f)
                print("", file = f)


import unittest
class testScop(unittest.TestCase):

        def test_empty(self):
                scop = Scop()

                self.assertEqual(scop.get_global(), None)
                self.assertEqual(scop.get_statements(), None)
                self.assertEqual(scop.get_extensions(), None)

        def test_full(self):
                from scop import Global, Statement, Extensions
                from scop.globl import Context, ContextType, Parameters
                from scop.globl.parameters import Parameter
                g = Global("C", Context(ContextType.CONTEXT, 0, 5, 0, 0, 0, 3), Parameters([Parameter("strings", "mSize kSize nSize")]))
                s1 = Statement()
                s2 = Statement()
                statements = [s1, s2]
                e = Extensions()

                scop = Scop(g, statements, e)

                self.assertEqual(scop.get_global(), g)
                self.assertEqual(scop.get_statements(), statements)
                self.assertEqual(scop.get_extensions(), e)

        def test_empty_print(self):
                from scop import Global, Statement, Extensions
                g = Global()
                s1 = Statement()
                statements = [s1]
                e = Extensions()

                scop = Scop(g, statements, e)
 
                # Generate file
                fileName = "scop_test1.out"
                with open(fileName, 'w') as f:
                        scop.write(f)

                # Check file content
                expected = "<OpenScop>\n\n# =============================================== Global\n# Language\nNone\n\n# Context\n# Parameters are provided\n# Number of statements\n1\n\n# =============================================== Statement 1\n# Number of relations describing the statement:\n0\n\n# ----------------------------------------------  1.1 Domain\n# ----------------------------------------------  1.2 Scattering\n# ----------------------------------------------  1.3 Access\n\n# =============================================== Extensions\n</OpenScop>\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)

        def test_full_print(self):
                from scop import Global, Statement, Extensions
                
                # Generate global
                from scop.globl import Context, ContextType, Parameters
                from scop.globl.parameters import Parameter
                context = Context(ContextType.CONTEXT, 0, 5, 0, 0, 0, 3)
                params = Parameters([Parameter("strings", "mSize kSize nSize")])
                g = Global("C", context, params)
                
                # Generate statements
                from scop.statement import Relation, RelationType, StatementExtension
                s1_domain = Relation(RelationType.DOMAIN, 9, 8, 3, 0, 0, 3, [[1, 1], [1, -1]])
                s1_scattering = Relation(RelationType.SCATTERING, 7, 15, 7, 3, 0, 3, [[0, -1], [0, 0]])
                s1_a1 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s1_a2 = Relation(RelationType.WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s1_a3 = Relation(RelationType.MAY_WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s1_access = [s1_a1, s1_a2, s1_a3]
                s1_ext1 = StatementExtension(["i", "j", "k"], "c[i][j] += a[i][k]*b[k][j];")
                s1_extensions = [s1_ext1]
                s1 = Statement(s1_domain, s1_scattering, s1_access, s1_extensions)

                s2_domain = Relation(RelationType.DOMAIN, 9, 8, 3, 0, 0, 3, [[1, 1], [1, -1]])
                s2_scattering = Relation(RelationType.SCATTERING, 7, 15, 7, 3, 0, 3, [[0, -1], [0, 0]])
                s2_a1 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s2_a2 = Relation(RelationType.WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s2_a3 = Relation(RelationType.MAY_WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                s2_access = [s2_a1, s2_a2, s2_a3]
                s2_ext1 = StatementExtension(["i", "j", "k"], "c[i][j] += a[i][k]*b[k][j];")
                s2_extensions = [s2_ext1]
                s2 = Statement(s2_domain, s2_scattering, s2_access, s2_extensions)

                statements = [s1, s2]

                # Generate extensions
                from scop.extensions import Scatnames, Arrays, Coordinates
                scatnames = Scatnames(["b0", "i", "b1", "j", "b2", "k", "b3"])
                arrays = Arrays(["i", "mSize", "j", "kSize", "k", "nSize", "c", "a", "b"])
                coordinates = Coordinates("example2_src_matmul.cc", 72, 0, 80, 0, 8)
                e = Extensions(scatnames, arrays, coordinates)

                # Generate SCOP
                scop = Scop(g, statements, e)
 
                # Generate file
                fileName = "scop_test2.out"
                with open(fileName, 'w') as f:
                        scop.write(f)

                # Check file content
                expected = "<OpenScop>\n\n# =============================================== Global\n# Language\nC\n\n# Context\nCONTEXT\n0 5 0 0 0 3\n\n# Parameters are provided\n1\n<strings>\nmSize kSize nSize\n</strings>\n\n# Number of statements\n2\n\n# =============================================== Statement 1\n# Number of relations describing the statement:\n5\n\n# ----------------------------------------------  1.1 Domain\nDOMAIN\n9 8 3 0 0 3\n1\t1\t\n1\t-1\t\n\n# ----------------------------------------------  1.2 Scattering\nSCATTERING\n7 15 7 3 0 3\n0\t-1\t\n0\t0\t\n\n# ----------------------------------------------  1.3 Access\nREAD\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\nWRITE\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\nMAY_WRITE\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\n# ----------------------------------------------  1.4 Statement Extensions\n# Number of Statement Extensions\n1\n<body>\n# Number of original iterators\n3\n# List of original iterators\ni j k \n# Statement body expression\nc[i][j] += a[i][k]*b[k][j];\n</body>\n\n# =============================================== Statement 2\n# Number of relations describing the statement:\n5\n\n# ----------------------------------------------  2.1 Domain\nDOMAIN\n9 8 3 0 0 3\n1\t1\t\n1\t-1\t\n\n# ----------------------------------------------  2.2 Scattering\nSCATTERING\n7 15 7 3 0 3\n0\t-1\t\n0\t0\t\n\n# ----------------------------------------------  2.3 Access\nREAD\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\nWRITE\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\nMAY_WRITE\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\n# ----------------------------------------------  2.4 Statement Extensions\n# Number of Statement Extensions\n1\n<body>\n# Number of original iterators\n3\n# List of original iterators\ni j k \n# Statement body expression\nc[i][j] += a[i][k]*b[k][j];\n</body>\n\n# =============================================== Extensions\n<scatnames>\nb0 i b1 j b2 k b3 \n</scatnames>\n\n<arrays>\n# Number of arrays\n9\n# Mapping array-identifiers/array-names\n1 i\n2 mSize\n3 j\n4 kSize\n5 k\n6 nSize\n7 c\n8 a\n9 b\n</arrays>\n\n<coordinates>\n# File name\nexample2_src_matmul.cc\n# Starting line and column\n72 0\n# Ending line and column\n80 0\n# Identation\n8\n</coordinates>\n\n</OpenScop>\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()
        
