#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

class Statement(object):
        """
        Represents a Statement within a SCOP

        Attributes:
                - domain : Relation domain
                - scattering : Relation scattering
                - access : List of Relation of RelationType access
                - extensions : List of Extension
        """

        def __init__(self, domain = None, scattering = None, access = None, extensions = None):
                self.domain = domain
                self.scattering = scattering
                self.access = access
                self.extensions = extensions

        def get_domain(self):
                return self.domain

        def get_scattering(self):
                return self.scattering

        def get_access(self):
                return self.access

        def get_extensions(self):
                return self.extensions

        def write(self, f, statementId):
                # Print header
                print("# =============================================== Statement " + str(statementId), file = f)
                # Print total number of relations
                print("# Number of relations describing the statement:", file = f)
                totalRelations = (self.domain != None) + (self.scattering != None)
                if self.access != None:
                        totalRelations = totalRelations + len(self.access)
                print(totalRelations, file = f)
                print("", file = f)

                # Print domain
                print("# ----------------------------------------------  " + str(statementId) + ".1 Domain", file = f)
                if self.domain != None:
                        self.domain.write(f)

                # Print scattering
                print("# ----------------------------------------------  " + str(statementId) + ".2 Scattering", file = f)
                if self.scattering != None:
                        self.scattering.write(f)

                # Print access
                print("# ----------------------------------------------  " + str(statementId) + ".3 Access", file = f)
                if self.access != None:
                        for acc in self.access:
                                acc.write(f)

                # Print extensions
                if self.extensions != None:
                        print("# ----------------------------------------------  " + str(statementId) + ".4 Statement Extensions", file = f)
                        print("# Number of Statement Extensions", file = f)
                        print(str(len(self.extensions)), file = f)
                        for ext in self.extensions:
                                ext.write(f)

                # Print end separator
                print("", file = f)


import unittest
class testStatement(unittest.TestCase):

        def test_empty(self):
                s = Statement()

                self.assertEqual(s.get_domain(), None)
                self.assertEqual(s.get_scattering(), None)
                self.assertEqual(s.get_access(), None)
                self.assertEqual(s.get_extensions(), None)

        def test_full(self):
                from statement import Relation, RelationType, StatementExtension
                domain = Relation(RelationType.DOMAIN, 9, 8, 3, 0, 0, 3, [[1, 1], [1, -1]])
                scattering = Relation(RelationType.SCATTERING, 7, 15, 7, 3, 0, 3, [[0, -1], [0, 0]])
                a1 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                a2 = Relation(RelationType.WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                a3 = Relation(RelationType.MAY_WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                access = [a1, a2, a3]
                ext1 = StatementExtension(["i", "j", "k"], "c[i][j] += a[i][k]*b[k][j];")
                extensions = [ext1]
                s = Statement(domain, scattering, access, extensions)

                self.assertEqual(s.get_domain(), domain)
                self.assertEqual(s.get_scattering(), scattering)
                self.assertEqual(s.get_access(), access)
                self.assertEqual(s.get_extensions(), extensions)

        def test_print(self):
                from statement import Relation, RelationType, StatementExtension
                domain = Relation(RelationType.DOMAIN, 9, 8, 3, 0, 0, 3, [[1, 1], [1, -1]])
                scattering = Relation(RelationType.SCATTERING, 7, 15, 7, 3, 0, 3, [[0, -1], [0, 0]])
                a1 = Relation(RelationType.READ, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                a2 = Relation(RelationType.WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                a3 = Relation(RelationType.MAY_WRITE, 3, 11, 3, 3, 0, 3, [[0, -1], [0, 0]])
                access = [a1, a2, a3]
                ext1 = StatementExtension(["i", "j", "k"], "c[i][j] += a[i][k]*b[k][j];")
                extensions = [ext1]
                s = Statement(domain, scattering, access, extensions)

                # Generate file
                fileName = "statement_test.out"
                with open(fileName, 'w') as f:
                        s.write(f, 1)

                # Check file content
                expected = "# =============================================== Statement 1\n# Number of relations describing the statement:\n5\n\n# ----------------------------------------------  1.1 Domain\nDOMAIN\n9 8 3 0 0 3\n1\t1\t\n1\t-1\t\n\n# ----------------------------------------------  1.2 Scattering\nSCATTERING\n7 15 7 3 0 3\n0\t-1\t\n0\t0\t\n\n# ----------------------------------------------  1.3 Access\nREAD\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\nWRITE\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\nMAY_WRITE\n3 11 3 3 0 3\n0\t-1\t\n0\t0\t\n\n# ----------------------------------------------  1.4 Statement Extensions\n# Number of Statement Extensions\n1\n<body>\n# Number of original iterators\n3\n# List of original iterators\ni j k \n# Statement body expression\nc[i][j] += a[i][k]*b[k][j];\n</body>\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()

