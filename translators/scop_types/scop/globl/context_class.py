#!/usr/bin/python
# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

from enum import Enum
class ContextType(Enum):
        UNDEFINED = -1
        CONTEXT = 2


class Context(object):
        """
        Represents a global context

        Attributes:
                - contextType : The context type (CONTEXT or UNDEFINED)
                - rows : Number of rows
                - columns : Number of columns
                - outputDims : Number of output dimensions
                - inputDims : Number of input dimensions
                - localDims : Number of local dimensions
                - params : Number of parameters
        """

        def __init__(self, contextType = ContextType.UNDEFINED, rows = -1, columns = -1, outputDims = -1, inputDims = -1, localDims = -1, params = -1):
                self.contextType = contextType
                self.rows = rows
                self.columns = columns
                self.outputDims = outputDims
                self.inputDims = inputDims
                self.localDims = localDims
                self.params = params

        def get_context_type(self):
                return self.contextType

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

        def write(self, f):
                # Print type
                print(self.contextType.name, file = f)

                # Print value attributes
                print(str(self.rows) + " " + str(self.columns) + " " + str(self.outputDims) + " " + str(self.inputDims) + " " + str(self.localDims) + " " + str(self.params), file = f)

                # Separator
                print("", file = f)


import unittest
class testContext(unittest.TestCase):

        def test_empty(self):
                context = Context()

                self.assertEqual(context.get_context_type().name, ContextType.UNDEFINED.name)
                self.assertEqual(context.get_rows(), -1)
                self.assertEqual(context.get_columns(), -1)
                self.assertEqual(context.get_output_dims(), -1)
                self.assertEqual(context.get_input_dims(), -1)
                self.assertEqual(context.get_local_dims(), -1)
                self.assertEqual(context.get_params(), -1)

        def test_full(self):
                contextType = ContextType.CONTEXT
                rows = 0
                cols = 5
                od = 0
                ind = 0
                ld = 0
                params = 3
                context = Context(contextType, rows, cols, od, ind, ld, params)

                self.assertEqual(context.get_context_type().name, contextType.name)
                self.assertEqual(context.get_rows(), rows)
                self.assertEqual(context.get_columns(), cols)
                self.assertEqual(context.get_output_dims(), od)
                self.assertEqual(context.get_input_dims(), ind)
                self.assertEqual(context.get_local_dims(), ld)
                self.assertEqual(context.get_params(), params)

        def test_print(self):
                contextType = ContextType.CONTEXT
                rows = 0
                cols = 5
                od = 0
                ind = 0
                ld = 0
                params = 3
                context = Context(contextType, rows, cols, od, ind, ld, params)

                # Generate file
                fileName = "context_test.out"
                with open(fileName, 'w') as f:
                        context.write(f)

                # Check file content
                expected = "CONTEXT\n0 5 0 0 0 3\n\n"
                with open(fileName, 'r') as f:
                        content = f.read()
                self.assertEqual(content, expected)

                # Erase file
                import os
                os.remove(fileName)


if __name__ == '__main__':
        unittest.main()

