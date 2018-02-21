#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest
from enum import Enum


#
# RELATION TYPE ENUMERATION
#

class RelationType(Enum):
        UNDEFINED = -1
        CONTEXT = 2
        DOMAIN = 3
        SCATTERING = 4
        READ = 6
        WRITE = 7
        MAY_WRITE = 8


#
# RELATION CLASS
#

class Relation(object):
        """
        Represents a Relation within a statement

        Attributes:
                - relationType : The relation type (DOMAIN, SCATTERING, READ, WRITE)
                - rows : Number of rows
                - columns : Number of columns
                - outputDims : Number of output dimensions
                - inputDims : Number of input dimensions
                - localDims : Number of local dimensions
                - params : Number of parameters
                - constraintMatrix : Matrix of contraints
        """

        def __init__(self, relationType=RelationType.UNDEFINED, rows=-1, columns=-1, outputDims=-1, inputDims=-1, localDims=-1, params=-1, constraintMatrix=None):
                self.relationType = relationType
                self.rows = rows
                self.columns = columns
                self.outputDims = outputDims
                self.inputDims = inputDims
                self.localDims = localDims
                self.params = params
                self.constraintMatrix = constraintMatrix

        def get_relation_type(self):
                return self.relationType

        def get_rows(self):
                return self.rows

        def get_columns(self):
                return self.columns

        def get_output_dims(self):
                return self.outputDims

        def get_input_dims(self):
                return self.inputDims

        def get_local_dims(self):
                return self.localDims

        def get_params(self):
                return self.params

        def get_constraint_matrix(self):
                return self.constraintMatrix

        @staticmethod
        def read_os(content, index):
                # Skip header and any annotation
                while content[index].startswith('#') or content[index] == '\n':
                        index = index + 1

                # Process mandatory field: type
                type_ind = content[index].strip()
                index = index + 1
                relType = RelationType[type_ind]

                # Process mandatory fields: dimensions
                dims = content[index].split()
                index = index + 1
                rows = int(dims[0])
                cols = int(dims[1])
                oDims = int(dims[2])
                iDims = int(dims[3])
                lDims = int(dims[4])
                params = int(dims[5])

                # Process constraint matrix
                cMatrix = []
                for i in range(rows):
                        row_vals = content[index].split()
                        index = index + 1
                        cMatrix.append(row_vals)

                # Skip empty lines and any annotation
                while index < len(content) and (content[index].startswith('#') or content[index] == '\n'):
                        index = index + 1

                # Build relation
                rel = Relation(relType, rows, cols, oDims, iDims, lDims, params, cMatrix)

                # Return structure
                return rel, index

        def write_os(self, f):
                # Print type
                print(self.relationType.name, file=f)

                # Print value attributes
                print(str(self.rows) + " " + str(self.columns) + " " + str(self.outputDims) + " " + str(self.inputDims) + " " + str(self.localDims) + " " + str(self.params), file=f)

                # Print constraint matrix
                if self.constraintMatrix is not None:
                        for constraintRow in self.constraintMatrix:
                                line = ""
                                for value in constraintRow:
                                        line = line + str(value) + "\t"
                                print(line, file=f)
                print("", file=f)


#
# UNIT TESTS
#

class TestRelation(unittest.TestCase):

        def test_empty(self):
                relation = Relation()

                self.assertEqual(relation.get_relation_type().name, RelationType.UNDEFINED.name)
                self.assertEqual(relation.get_rows(), -1)
                self.assertEqual(relation.get_columns(), -1)
                self.assertEqual(relation.get_output_dims(), -1)
                self.assertEqual(relation.get_input_dims(), -1)
                self.assertEqual(relation.get_local_dims(), -1)
                self.assertEqual(relation.get_params(), -1)
                self.assertEqual(relation.get_constraint_matrix(), None)

        def test_full(self):
                relType = RelationType.DOMAIN
                rows = 9
                cols = 8
                od = 3
                ind = 0
                ld = 0
                params = 3
                matrix = [[1, -1], [1, -1]]
                relation = Relation(relType, rows, cols, od, ind, ld, params, matrix)

                self.assertEqual(relation.get_relation_type().name, relType.name)
                self.assertEqual(relation.get_rows(), rows)
                self.assertEqual(relation.get_columns(), cols)
                self.assertEqual(relation.get_output_dims(), od)
                self.assertEqual(relation.get_input_dims(), ind)
                self.assertEqual(relation.get_local_dims(), ld)
                self.assertEqual(relation.get_params(), params)
                self.assertEqual(relation.get_constraint_matrix(), matrix)

        def test_write_os(self):
                relType = RelationType.DOMAIN
                rows = 9
                cols = 8
                od = 3
                ind = 0
                ld = 0
                params = 3
                matrix = [[1, -1], [1, -1]]
                relation = Relation(relType, rows, cols, od, ind, ld, params, matrix)

                try:
                        # Generate file
                        fileName = "relation_test.out"
                        with open(fileName, 'w') as f:
                                relation.write_os(f)

                        # Check file content
                        expected = "DOMAIN\n9 8 3 0 0 3\n1\t-1\t\n1\t-1\t\n\n"
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
                relationFile = dirPath + "/tests/relation_test.expected.scop"
                with open(relationFile, 'r') as f:
                        content = f.readlines()

                # Read from file
                rel, index = Relation.read_os(content, 0)

                # Check index value
                self.assertEqual(index, len(content))

                # Check Relation object content
                try:
                        # Write to file
                        outputFile = dirPath + "/tests/relation_test.out.scop"
                        with open(outputFile, 'w') as f:
                                rel.write_os(f)

                        # Check file content
                        with open(relationFile, 'r') as f:
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
