#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import unittest
import logging
import ast

#
# Logger definition
#

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s - %(message)s')
logger = logging.getLogger(__name__)


#
# Translator class
#

class Py2PyCOMPSs(object):

    @staticmethod
    def translate(func, par_py_files, output):
        """
        Substitutes the given parallel python files into the original
        function code and adds the required PyCOMPSs annotations. The
        result is stored in the given output file

        Arguments:
                - func : Python original function
                - par_py_files : List of files containing the Python parallelization
                        of each for block in the func_source
                - output : PyCOMPSs file path
        Return:
        Raise:
                - Py2PyCOMPSsException
        """

        if __debug__:
            logger.debug("[Py2PyCOMPSs] Initialize translation")
            logger.debug("[Py2PyCOMPSs]  - Function: " + str(func))
            for par_f in par_py_files:
                logger.debug("[Py2PyCOMPSs]  - File: " + str(par_f))
            logger.debug("[Py2PyCOMPSs]  - Output: " + str(output))

        # Load user function code
        import astor
        func_ast = astor.code_to_ast(func)

        # Initialize output content
        output_imports = []
        output_task_headers = []
        output_task_functions = []
        output_loops_code = []
        task_counter_id = 0

        # Process each par_py file
        import _ast
        for par_py in par_py_files:
            # Retrieve file AST
            par_py_ast = astor.code_to_ast.parse_file(par_py)

            # Process ast
            output_code = []
            task2new_name = {}
            task2original_args = {}
            task2new_args2subscripts = {}

            for statement in par_py_ast.body:
                if isinstance(statement, _ast.Import):
                    output_imports.append(statement)
                elif isinstance(statement, _ast.FunctionDef):
                    task_func_name = statement.name
                    # Update name to avoid override between par_py files
                    task_counter_id += 1
                    new_name = "S" + str(task_counter_id)
                    task2new_name[task_func_name] = new_name

                    # Update task
                    header, code, original_args, new_args2subscripts = Py2PyCOMPSs._process_task(statement, new_name)

                    output_task_headers.append(header)
                    output_task_functions.append(code)
                    task2original_args[task_func_name] = original_args
                    task2new_args2subscripts[task_func_name] = new_args2subscripts
                else:
                    # Generated CLooG code for parallel loop
                    # Check for calls to task methods and replace them. Leave the rest intact
                    rc = _RewriteCallees(task2new_name, task2original_args, task2new_args2subscripts)
                    new_statement = rc.visit(statement)
                    output_code.append(new_statement)
            # Store output code
            output_loops_code.append(output_code)

        # Substitute loops code on function code
        loop_index = 0
        new_body = []
        for statement in func_ast.body:
            if isinstance(statement, _ast.For):
                # Check the correctness of the number of generated loops
                if loop_index >= len(output_loops_code):
                    raise Py2PyCOMPSsException(
                        "[ERROR] The number of generated parallel FORs is < than the original number of main FORs")
                # Substitute code with all parallel loop statements
                new_body.extend(output_loops_code[loop_index])
                # Add barrier
                import ast
                barrier = ast.parse("compss_barrier()")
                new_body.append(barrier.body[0])
                # Mark next loop
                loop_index = loop_index + 1
            else:
                # Store the same statement to new body
                new_body.append(statement)
        func_ast.body = new_body
        # Check that we have substituted all loops
        if loop_index != len(output_loops_code):
            raise Py2PyCOMPSsException(
                "[ERROR] The number of generated parallel FORs is > than the original number of main FORs")

        # Remove the parallel decorator
        for decorator in func_ast.decorator_list:
            if isinstance(decorator, _ast.Call):
                if decorator.func.id == "parallel":
                    func_ast.decorator_list.remove(decorator)

        # Debug
        # if __debug__:
        # print("OUTPUT IMPORTS:")
        # for oi in output_imports:
        # print(astor.dump_tree(oi))
        # print("OUTPUT TASKS:")
        # import itertools
        # for task_def, task_func in itertools.izip(output_task_headers, output_task_functions):
        # print(task_def)
        # print(astor.dump_tree(task_func))
        # print("OUTPUT CODE:")
        # print(astor.dump_tree(func_ast.body))

        # Print content to PyCOMPSs file
        with open(output, 'w') as f:
            # Write header
            print("# [COMPSs Autoparallel] Begin Autogenerated code", file=f)
            # Write imports
            for oi in output_imports:
                print(astor.to_source(oi), file=f)
            # Write default PyCOMPSs imports
            print("from pycompss.api.api import compss_barrier, compss_wait_on, compss_open", file=f)
            print("from pycompss.api.task import task", file=f)
            print("from pycompss.api.parameter import *", file=f)
            print("", file=f)
            # Write tasks
            import itertools
            for task_def, task_func in itertools.izip(output_task_headers, output_task_functions):
                print(task_def, file=f)
                print(astor.to_source(task_func), file=f)
            # Write function
            print(astor.to_source(func_ast), file=f)
            # Write header
            print("# [COMPSs Autoparallel] End Autogenerated code", file=f)

        if __debug__:
            logger.debug("[Py2PyCOMPSs] End translation")

    @staticmethod
    def _process_task(func, new_name):
        """
        Processes the current function to obtain its task header, its
        PyCOMPSs equivalent function and the callee modification. Renames
        it with the given new_name

        Arguments:
                - func : AST node representing the head of the Python function
                - new_name : New name for the Python function
        Return:
                - task_header : String representing the function task header
                - new_func : new AST node representing the head of the function
                - original_func_arguments : List of original arguments
                - new_arguments2subscript : Dictionary containing the callee modifications of each new argument
        Raise:
                - Py2PyCOMPSsException
        """

        # Rename function
        func.name = new_name

        # Rewrite subscripts by plain variables
        rs = _RewriteSubscript()
        new_func = rs.visit(func)
        var2subscript = rs.get_var_subscripts()

        # Change function arguments
        original_args = new_func.args.args
        new_func.args.args = var2subscript.keys()

        # Process direction of parameters
        in_vars, out_vars, inout_vars = Py2PyCOMPSs._process_parameters_direction(new_func.body[0])

        # Construct task header
        task_header = Py2PyCOMPSs._construct_task_header(in_vars, out_vars, inout_vars)

        # Return task header and new function
        return task_header, new_func, original_args, var2subscript

    @staticmethod
    def _process_parameters_direction(statement):
        """
        Processes all the directions of the parameters found in the given statement

        Arguments:
                - statement : AST node representing the head of the statement
        Return:
                - in_vars : List of names of IN variables
                - out_vars : List of names of OUT variables
                - inout_vars : List of names of INOUT variables
        Raise:
                - Py2PyCOMPSsException
        """

        import _ast

        in_vars = []
        out_vars = []
        inout_vars = []

        if isinstance(statement, _ast.Assign):
            # Process targets
            for t in statement.targets:
                ov = Py2PyCOMPSs._process_write_var(t)
                out_vars.append(ov)
                # TODO: Possible BUG - target will be recognised as INOUT not OUT
                ivs = Py2PyCOMPSs._process_vars(t)
                in_vars.extend(ivs)
            # Process values
            ivs = Py2PyCOMPSs._process_vars(statement.value)
            in_vars.extend(ivs)
        elif isinstance(statement, _ast.AugAssign):
            # Process target
            iov = Py2PyCOMPSs._process_write_var(statement.target)
            inout_vars.append(iov)
            ivs = Py2PyCOMPSs._process_vars(statement.target)
            in_vars.extend(ivs)
            # Process values
            ivs = Py2PyCOMPSs._process_vars(statement.value)
            in_vars.extend(ivs)
        else:
            raise Py2PyCOMPSsException("[ERROR] Unrecognised statement inside task")

        # Fix duplicate variables and directions
        out_vars = list(set(out_vars))
        inout_vars = list(set(inout_vars))
        in_vars = list(set(in_vars))
        for iv in in_vars:
            if iv in out_vars:
                in_vars.remove(iv)
                out_vars.remove(iv)
                inout_vars.append(iv)
        for iv in in_vars:
            if iv in inout_vars:
                in_vars.remove(iv)
        for ov in out_vars:
            if ov in inout_vars:
                out_vars.remove(ov)

        # Return variables
        return in_vars, out_vars, inout_vars

    @staticmethod
    def _process_write_var(node):
        """
        Searches for the name of the write accessed variable

        Arguments:
                - node : Head AST node of the write access
        Return:
                - var_name : Name of the write accessed variable (string)
        Raise:
                - Py2PyCOMPSsException
        """

        # A write variable can only be a subscript or the write variable id itself
        import _ast
        if isinstance(node, _ast.Name):
            return node.id
        elif isinstance(node, _ast.Subscript):
            return Py2PyCOMPSs._process_write_var(node.value)
        else:
            raise Py2PyCOMPSsException("[ERROR] Unrecognised expression on write operation")

    @staticmethod
    def _process_vars(node):
        """
        Searches all the accessed variable names

        Arguments:
                - node : Head AST node
        Return:
                - in_vars : List of names of accessed variables (list of strings)
        Raise:
        """

        import _ast

        # Direct case
        if isinstance(node, _ast.Name):
            return [node.id]

        # Child recursion
        in_vars = []
        for _, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        in_vars.extend(Py2PyCOMPSs._process_vars(item))
            elif isinstance(value, ast.AST):
                in_vars.extend(Py2PyCOMPSs._process_vars(value))
        return in_vars

    @staticmethod
    def _construct_task_header(in_vars, out_vars, inout_vars):
        """
        Constructs the task header corresponding to the given IN, OUT, and INOUT variables

        Arguments:
                - in_vars : List of names of IN variables
                - out_vars : List of names of OUT variables
                - inout_vars : List of names of INOUT variables
        Return:
                - task_header : String representing the PyCOMPSs task header
        Raise:
        """
        # Construct task header
        task_header = "@task("
        first = True
        for iv in in_vars:
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += iv + " = IN"
        for ov in out_vars:
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += ov + " = OUT"
        for iov in inout_vars:
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += iov + " = INOUT"
        task_header += ")"

        return task_header


#
# Class Node transformer for subscripts
#

class _RewriteSubscript(ast.NodeTransformer):
    """
    Node Transformer class to visit all the Subscript AST nodes and change them
    by a plain variable access. The performed modifications are stored inside the
    class object so that users can retrieve them when necessary

    Attributes:
            - var_counter : Number of replaced variables
            - var2subscript : Dictionary mapping replaced variables by its original expression
    """

    def __init__(self):
        self.var_counter = 1
        self.var2subscript = {}

    def get_next_var_name(self):
        # Create new var name
        import _ast
        var_name = "var" + str(self.var_counter)
        var_ast = _ast.Name(id=var_name)

        # Increase counter for next call
        self.var_counter += 1

        # Return var object
        return var_ast, var_name

    def get_var_subscripts(self):
        return self.var2subscript

    def visit_Subscript(self, node):
        var_ast, var_name = self.get_next_var_name()
        self.var2subscript[var_name] = node
        return ast.copy_location(var_ast, node)


#
# Class Node transformer for tasks' callees
#

class _RewriteCallees(ast.NodeTransformer):
    """
    Node Transformer class to visit all the callees and change them

    Attributes:
            - task2new_name : Dictionary mapping the function variable original and new names
            - task2original_args : Dictionary mapping the function name to its original arguments
            - task2new_args2subscripts : Dictionary mapping the function name to its arg-subscript dictionary
    """

    def __init__(self, task2new_name, task2original_args, task2new_args2subscripts):
        self.task2new_name = task2new_name
        self.task2original_args = task2original_args
        self.task2new_args2subscripts = task2new_args2subscripts

    def visit_Call(self, node):
        original_name = node.func.id
        if original_name in self.task2new_name.keys():
            # It is a call to a task, we must replace it by the new callee
            import copy
            new_node = copy.deepcopy(node)

            # Replace function name
            import _ast
            new_node.func = _ast.Name(id=self.task2new_name[original_name])

            # Map function arguments to callee arguments
            func_args = self.task2original_args[original_name]
            func_args2callee_args = {}
            for i in range(len(node.args)):
                func_arg = func_args[i].id
                callee_arg = node.args[i]
                func_args2callee_args[func_arg] = callee_arg

            # Modify new arguments subscripts by callee parameters
            args2subscripts = self.task2new_args2subscripts[original_name]
            new_subscripts = []
            for subscript in args2subscripts.values():
                ran = _RewriteArgNames(func_args2callee_args)
                new_subscript = ran.visit(subscript)
                new_subscripts.append(new_subscript)

            # Change the node args by the subscripts expressions
            new_node.args = new_subscripts

            return ast.copy_location(new_node, node)
        else:
            # Generic call to a function. No modifications required
            return node


#
# Class Node transformer for Arguments Names
#

class _RewriteArgNames(ast.NodeTransformer):
    """
    Node Transformer class to visit all the Names AST nodes and change them
    by a its new arguments callee

    Attributes:
            - func_args2callee_args : Dictionary mapping the function variable names and
            its callee expression
    """

    def __init__(self, func_args2callee_args):
        self.func_args2callee_args = func_args2callee_args

    def visit_Name(self, node):
        if node.id in self.func_args2callee_args.keys():
            # Accessed variable is a function parameter
            # Modify it by its callee value
            import copy
            callee_expr = copy.deepcopy(self.func_args2callee_args[node.id])
            return ast.copy_location(callee_expr, node)
        else:
            # Accessed variable is not a parameter. Leave it intact
            return node


#
# Exception Class
#

class Py2PyCOMPSsException(Exception):

    def __init__(self, msg=None, nested_exception=None):
        self.msg = msg
        self.nested_exception = nested_exception

    def __str__(self):
        s = "Exception on Py2PyCOMPSs.translate method.\n"
        if self.msg is not None:
            s = s + "Message: " + str(self.msg) + "\n"
        if self.nested_exception is not None:
            s = s + "Nested Exception: " + str(self.nested_exception) + "\n"
        return s


#
# UNIT TESTS
#

class TestPy2PyCOMPSs(unittest.TestCase):

    def test_matmul(self):
        # Base variables
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))
        tests_path = dir_path + "/tests"

        # Insert function file into pythonpath
        import sys
        sys.path.insert(0, tests_path)

        # Import function to replace
        import importlib
        func_name = "matmul"
        test_module = importlib.import_module("pycompss.util.translators.py2pycompss.tests.test1_matmul_func")
        func = getattr(test_module, func_name)

        # Create list of parallel py codes
        src_file0 = tests_path + "/test1_matmul.src.python"
        par_py_files = [src_file0]

        # Output file
        out_file = tests_path + "/test1_matmul.out.pycompss"

        # Translate
        Py2PyCOMPSs.translate(func, par_py_files, out_file)

        # Check file content
        expected_file = tests_path + "/test1_matmul.expected.pycompss"
        try:
            with open(expected_file, 'r') as f:
                expected_content = f.read()
            with open(out_file, 'r') as f:
                out_content = f.read()
            self.assertEqual(out_content, expected_content)
        except Exception:
            raise
        finally:
            # Erase file
            os.remove(out_file)


#
# MAIN
#

if __name__ == '__main__':
    unittest.main()
