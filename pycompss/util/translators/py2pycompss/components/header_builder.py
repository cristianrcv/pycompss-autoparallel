#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import logging
import unittest

#
# Logger definition
#

logger = logging.getLogger("pycompss.api.autoparallel")


#
# Header Builder class
#

class HeaderBuilder(object):

    @staticmethod
    def build_task_header(in_vars, in_collection_vars, out_vars, out_collection_vars, inout_vars,
                          inout_collection_vars, return_vars):
        """
        Constructs the task header corresponding to the given IN, OUT, and INOUT variables

        :param in_vars: List of names of IN variables
            + type: List<str>
        :param in_collection_vars: Dictionary of IN collection variables and its dimension
            + type: Dict<str, int>
        :param out_vars: List of names of OUT variables
            + type: List<str>
        :param out_collection_vars: Dictionary of OUT collection variables and its dimension
            + type: Dict<str, int>
        :param inout_vars: List of names of INOUT variables
            + type: List<str>
        :param inout_collection_vars: Dictionary of INOUT collection variables and its dimension
            + type: Dict<str, int>
        :param return_vars: List of names of RETURN variables
            + type: List<str>
        :return task_header: String representing the PyCOMPSs task header
            + type: str
        """

        # Construct task header
        task_header = "@task("

        # Add parameters information
        first = True
        for iv in in_vars:
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += iv + "=IN"
        for icv, dim in in_collection_vars.items():
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += icv + "={Type: COLLECTION_IN, Depth: " + str(dim) + "}"

        for ov in out_vars:
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += ov + "=OUT"
        for ocv, dim in out_collection_vars.items():
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += ocv + "={Type: COLLECTION_OUT, Depth: " + str(dim) + "}"

        for iov in inout_vars:
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += iov + "=INOUT"
        for iocv, dim in inout_collection_vars.items():
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += iocv + "={Type: COLLECTION_INOUT, Depth: " + str(dim) + "}"

        # Add return information
        if len(return_vars) > 0:
            if not first:
                task_header += ", "
            task_header += "returns=" + str(len(return_vars))

        # Close task header
        task_header += ")"

        return task_header

    @staticmethod
    def split_task_header(header):
        """
        Constructs a map containing all the variables of the task header and its directionality (IN, OUT, INOUT)

        :param header: String containing the task header
        :return args2dirs: Map containing the task variables and its directionality
        """

        header = header.replace("@task(", "")
        header = header.replace(")", "")

        args2dirs = {}
        arguments = header.split(", ")
        for entry in arguments:
            argument, direction = entry.split("=")
            args2dirs[argument] = direction

        return args2dirs


#
# UNIT TESTS
#

class TestHeaderBuilder(unittest.TestCase):

    def test_regular_header(self):
        in_vars = ["in1", "in2"]
        in_collection_vars = {}
        out_vars = ["out1", "out2"]
        out_collection_vars = {}
        inout_vars = ["inout1", "inout2"]
        inout_collection_vars = {}
        return_vars = ["r1", "r2", "r3"]

        header_got = HeaderBuilder.build_task_header(in_vars, in_collection_vars, out_vars, out_collection_vars,
                                                     inout_vars, inout_collection_vars, return_vars)
        header_expected = "@task(in1=IN, in2=IN, out1=OUT, out2=OUT, inout1=INOUT, inout2=INOUT, returns=3)"
        self.assertEqual(header_got, header_expected)

    def test_collections_header(self):
        in_vars = ["in1", "in2"]
        in_collection_vars = {"var1": 1}
        out_vars = []
        out_collection_vars = {}
        inout_vars = ["inout1", "inout2"]
        inout_collection_vars = {"var2": 2}
        return_vars = []

        header_got = HeaderBuilder.build_task_header(in_vars, in_collection_vars, out_vars, out_collection_vars,
                                                     inout_vars, inout_collection_vars, return_vars)

        header_expected = "@task(in1=IN, in2=IN, var1={Type: COLLECTION_IN, Depth: 1}, inout1=INOUT, inout2=INOUT, " \
                          "var2={Type: COLLECTION_INOUT, Depth: 2})"
        self.assertEqual(header_got, header_expected)


#
# MAIN
#

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s - %(message)s')
    unittest.main()
