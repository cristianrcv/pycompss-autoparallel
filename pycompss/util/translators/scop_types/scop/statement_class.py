#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest


class Statement(object):
        """
        Represents a Statement within a SCOP

        Attributes:
                - domain : Relation domain
                - scattering : Relation scattering
                - access : List of Relation of RelationType access
                - extensions : List of Extension
        """

        def __init__(self, domain=None, scattering=None, access=None, extensions=None):
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

        @staticmethod
        def read_os(content, index):
                return None, index

        @staticmethod
        def read_py(f):
                pass

        def write_os(self, f, statementId):
                # Print header
                print("# =============================================== Statement " + str(statementId), file=f)
                # Print total number of relations
                print("# Number of relations describing the statement:", file=f)
                totalRelations = (self.domain is not None) + (self.scattering is not None)
                if self.access is not None:
                        totalRelations = totalRelations + len(self.access)
                print(totalRelations, file=f)
                print("", file=f)

                # Print domain
                print("# ----------------------------------------------  " + str(statementId) + ".1 Domain", file=f)
                if self.domain is not None:
                        self.domain.write_os(f)

                # Print scattering
                print("# ----------------------------------------------  " + str(statementId) + ".2 Scattering", file=f)
                if self.scattering is not None:
                        self.scattering.write_os(f)

                # Print access
                print("# ----------------------------------------------  " + str(statementId) + ".3 Access", file=f)
                if self.access is not None:
                        for acc in self.access:
                                acc.write_os(f)

                # Print extensions
                if self.extensions is not None:
                        print("# ----------------------------------------------  " + str(statementId) + ".4 Statement Extensions", file=f)
                        print("# Number of Statement Extensions", file=f)
                        print(str(len(self.extensions)), file=f)
                        for ext in self.extensions:
                                ext.write_os(f)

                # Print end separator
                print("", file=f)

        def write_py(self, f):
                pass


#
# UNIT TESTS
#

class TestStatement(unittest.TestCase):

        def test_empty(self):
                s = Statement()

                self.assertEqual(s.get_domain(), None)
                self.assertEqual(s.get_scattering(), None)
                self.assertEqual(s.get_access(), None)
                self.assertEqual(s.get_extensions(), None)

        def test_full(self):
                from pycompss.util.translators.scop_types.scop.statement.relation_class import Relation, RelationType
                from pycompss.util.translators.scop_types.scop.statement.statement_extension_class import StatementExtension
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

        def test_write_os(self):
                from pycompss.util.translators.scop_types.scop.statement.relation_class import Relation, RelationType
                from pycompss.util.translators.scop_types.scop.statement.statement_extension_class import StatementExtension
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
                import os
                dirPath = os.path.dirname(os.path.realpath(__file__))
                outputFile = dirPath + "/tests/statement_test.out.scop"
                expectedFile = dirPath + "/tests/statement_test.expected.scop"
                with open(outputFile, 'w') as f:
                        s.write_os(f, 1)

                # Check file content
                with open(expectedFile, 'r') as f:
                        expectedContent = f.read()
                with open(outputFile, 'r') as f:
                        outputContent = f.read()
                self.assertEqual(outputContent, expectedContent)

                # Erase file
                os.remove(outputFile)


#
# MAIN
#

if __name__ == '__main__':
        unittest.main()
