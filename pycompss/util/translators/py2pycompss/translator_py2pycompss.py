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
            task2new_args = {}
            task2ret_args = {}
            task2vars2subscripts = {}

            for statement in par_py_ast.body:
                if isinstance(statement, _ast.Import):
                    if not Py2PyCOMPSs._contains_import_statement(statement, output_imports):
                        output_imports.append(statement)
                elif isinstance(statement, _ast.FunctionDef):
                    task_func_name = statement.name
                    # Update name to avoid override between par_py files
                    task_counter_id += 1
                    new_name = "S" + str(task_counter_id)
                    task2new_name[task_func_name] = new_name

                    # Update task
                    header, code, original_args, new_args, ret_args, new_vars2subscripts = Py2PyCOMPSs._process_task(
                        statement, new_name)

                    output_task_headers.append(header)
                    output_task_functions.append(code)
                    task2original_args[task_func_name] = original_args
                    task2new_args[task_func_name] = new_args
                    task2ret_args[task_func_name] = ret_args
                    task2vars2subscripts[task_func_name] = new_vars2subscripts
                else:
                    # Generated CLooG code for parallel loop
                    # Check for calls to task methods and replace them. Leave the rest intact
                    rc = _RewriteCallees(task2new_name, task2original_args, task2new_args, task2ret_args,
                                         task2vars2subscripts)
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
            for oi in set(output_imports):
                print(astor.to_source(oi), file=f)
            # Write default PyCOMPSs imports
            print("from pycompss.api.api import compss_barrier, compss_wait_on, compss_open", file=f)
            print("from pycompss.api.task import task", file=f)
            print("from pycompss.api.parameter import *", file=f)
            print("", file=f)
            print("", file=f)
            # Write tasks
            import itertools
            for task_def, task_func in itertools.izip(output_task_headers, output_task_functions):
                print(task_def, file=f)
                print(astor.to_source(task_func), file=f)
                print("", file=f)
            # Write function
            print(astor.to_source(func_ast), file=f)
            # Write header
            print("# [COMPSs Autoparallel] End Autogenerated code", file=f)

        if __debug__:
            logger.debug("[Py2PyCOMPSs] End translation")

    @staticmethod
    def _contains_import_statement(import_statement, list_of_imports):
        for i in list_of_imports:
            if Py2PyCOMPSs._equal_imports(import_statement, i):
                return True
        return False

    @staticmethod
    def _equal_imports(import_statement1, import_statement2):
        if len(import_statement1.names) != len(import_statement2.names):
            return False
        for i in range(len(import_statement1.names)):
            import1 = import_statement1.names[i]
            import2 = import_statement2.names[i]
            if import1.name != import2.name or import1.asname != import2.asname:
                return False
        return True

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
                - original_args : List of original arguments
                - new_args : List of new arguments
                - ret_args : List of return variables
                - var2subscript : Dictionary containing the mapping of new variables to previous subscripts
        Raise:
                - Py2PyCOMPSsException
        """

        if __debug__:
            logger.debug("Original task definition")
            logger.debug(ast.dump(func))

        # Rename function
        func.name = new_name

        # Rewrite subscripts by plain variables
        rs = _RewriteSubscript()
        new_func = rs.visit(func)
        var2subscript = rs.get_var_subscripts()

        # Process direction of parameters
        in_vars, out_vars, inout_vars, return_vars = Py2PyCOMPSs._process_parameters(new_func.body[0])

        # Add non subscript variables to var2subscript
        import _ast
        for var in in_vars + out_vars + inout_vars + return_vars:
            if var not in var2subscript.keys():
                var_ast = _ast.Name(id=var)
                var2subscript[var] = var_ast

        # Rewrite function if it has a return
        import _ast
        if len(return_vars) > 0:
            new_func.body[0] = _ast.Return(value=new_func.body[0].value)

        # Create new function arguments
        new_args = []
        for var in in_vars + out_vars + inout_vars:
            if var not in new_args:
                var_ast = _ast.Name(id=var)
                new_args.append(var_ast)
        original_args = new_func.args.args
        new_func.args.args = new_args

        # Construct task header
        task_header = Py2PyCOMPSs._construct_task_header(in_vars, out_vars, inout_vars, return_vars)

        # Return task header and new function
        if __debug__:
            logger.debug("New task definition")
            logger.debug(ast.dump(new_func))
            logger.debug(return_vars)

        return task_header, new_func, original_args, new_args, return_vars, var2subscript

    @staticmethod
    def _process_parameters(statement):
        """
        Processes all the directions of the parameters found in the given statement

        Arguments:
                - statement : AST node representing the head of the statement
        Return:
                - in_vars : List of names of IN variables
                - out_vars : List of names of OUT variables
                - inout_vars : List of names of INOUT variables
                - return_vars : List of names of RETURN variables
        Raise:
                - Py2PyCOMPSsException
        """

        import _ast

        in_vars = Py2PyCOMPSs._get_access_vars(statement)

        out_vars = []
        inout_vars = []
        return_vars = []

        target_vars = Py2PyCOMPSs._get_target_vars(statement)
        if isinstance(statement.value, _ast.Call):
            # Target vars are the return of a function
            return_vars = target_vars
        else:
            # Target vars are the result of an expression
            out_vars = target_vars

        # Fix duplicate variables and directions
        fixed_in_vars = []
        fixed_out_vars = []
        fixed_inout_vars = []
        fixed_return_vars = return_vars
        for iv in in_vars:
            if iv in out_vars or iv in inout_vars:
                if iv not in fixed_inout_vars:
                    fixed_inout_vars.append(iv)
            else:
                if iv not in fixed_in_vars:
                    fixed_in_vars.append(iv)
        for ov in out_vars:
            if ov in in_vars or ov in inout_vars:
                if ov not in fixed_inout_vars:
                    fixed_inout_vars.append(ov)
            else:
                if ov not in fixed_out_vars:
                    fixed_out_vars.append(ov)
        for iov in inout_vars:
            if iov not in fixed_inout_vars:
                fixed_inout_vars.append(iov)

        # Return variables
        return fixed_in_vars, fixed_out_vars, fixed_inout_vars, fixed_return_vars

    @staticmethod
    def _get_access_vars(statement, is_target=False):
        """
        Returns the accessed variable names within the given expression

        Arguments:
                - statement : AST node representing the head of the statement
        Return:
                - in_vars : List of names of accessed variables
        Raise:
        """

        import _ast

        # Direct case
        if isinstance(statement, _ast.Name):
            if is_target:
                return []
            else:
                return [statement.id]

        # Child recursion
        in_vars = []
        for field, value in ast.iter_fields(statement):
            if field == "func" or field == "keywords":
                # Skip function names and var_args keywords
                pass
            else:
                children_are_target = is_target or (field == "targets")
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            in_vars.extend(Py2PyCOMPSs._get_access_vars(item, children_are_target))
                elif isinstance(value, ast.AST):
                    in_vars.extend(Py2PyCOMPSs._get_access_vars(value, children_are_target))
        return in_vars

    @staticmethod
    def _get_target_vars(statement):
        """
        Returns the target variables within given the expression

        Arguments:
                - statement : AST node representing the head of the statement
        Return:
                - target_vars : List of names of target variables
        Raise:
        """

        import _ast

        if isinstance(statement, _ast.Assign):
            # Assign can have more than one target var, process all
            target_vars = []
            for t in statement.targets:
                target_vars.extend(Py2PyCOMPSs._get_target_vars(t))
            return target_vars
        elif isinstance(statement, _ast.AugAssign):
            # Operations on assign have a single target var
            return Py2PyCOMPSs._get_target_vars(statement.target)
        elif isinstance(statement, _ast.Expr):
            # No target on void method call
            return []
        elif isinstance(statement, _ast.Name):
            # Add Id of used variable
            return [statement.id]
        elif isinstance(statement, _ast.Subscript):
            # On array access process value (not indexes)
            return Py2PyCOMPSs._get_target_vars(statement.value)
        elif isinstance(statement, _ast.List):
            # Process all the elements of the list
            target_vars = []
            for list_fields in statement.elts:
                target_vars.extend(Py2PyCOMPSs._get_target_vars(list_fields))
            return target_vars
        elif isinstance(statement, _ast.Tuple):
            # Process all the fields of the tuple
            target_vars = []
            for tuple_field in statement.elts:
                target_vars.extend(Py2PyCOMPSs._get_target_vars(tuple_field))
            return target_vars
        else:
            # Unrecognised statement expression
            raise Py2PyCOMPSsException("[ERROR] Unrecognised expression on write operation")

    @staticmethod
    def _construct_task_header(in_vars, out_vars, inout_vars, return_vars):
        """
        Constructs the task header corresponding to the given IN, OUT, and INOUT variables

        Arguments:
                - in_vars : List of names of IN variables
                - out_vars : List of names of OUT variables
                - inout_vars : List of names of INOUT variables
                - return_vars : List of names of RETURN variables
        Return:
                - task_header : String representing the PyCOMPSs task header
        Raise:
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
        for ov in out_vars:
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += ov + "=OUT"
        for iov in inout_vars:
            if not first:
                task_header += ", "
            else:
                first = False
            task_header += iov + "=INOUT"

        # Add return information
        if len(return_vars) > 0:
            if not first:
                task_header += ", "
            task_header += "returns=" + str(len(return_vars))

        # Close task header
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
            - task2new_args : Dictionary mapping the function name to its new arguments
            - task2ret_vars : Dictionary mapping the function name to its return values
            - task2vars2subscripts : Dictionary mapping the function name to its vars-subscripts dictionary
    """

    def __init__(self, task2new_name, task2original_args, task2new_args, task2ret_vars, task2vars2subscripts):
        self.task2new_name = task2new_name
        self.task2original_args = task2original_args
        self.task2new_args = task2new_args
        self.task2ret_vars = task2ret_vars
        self.task2vars2subscripts = task2vars2subscripts

    def visit_Call(self, node):
        original_name = node.func.id

        if original_name in self.task2new_name.keys():
            # It is a call to a task, we must replace it by the new callee
            if __debug__:
                logger.debug("Original task call")
                logger.debug(ast.dump(node))

            # Replace function name
            import _ast
            node.func = _ast.Name(id=self.task2new_name[original_name])

            # Map function arguments to call arguments
            func_args = self.task2original_args[original_name]
            func_args2callee_args = {}
            for i in range(len(node.args)):
                func_arg = func_args[i].id
                callee_arg = node.args[i]
                func_args2callee_args[func_arg] = callee_arg

            # Transform function variables to call arguments on all var2subscript
            vars2subscripts = self.task2vars2subscripts[original_name]
            vars2new_subscripts = {}
            for var, subscript in vars2subscripts.items():
                ran = _RewriteArgNames(func_args2callee_args)
                vars2new_subscripts[var] = ran.visit(subscript)

            # if __debug__:
            #    print("Vars to subscripts:")
            #    for k, v in vars2new_subscripts.items():
            #        print(str(k) + " -> " + str(ast.dump(v)))

            # Transform all the new arguments into its subscript
            transformed_new_args = []
            new_args = self.task2new_args[original_name]
            for arg in new_args:
                transformed_new_args.append(vars2new_subscripts[arg.id])

            # if __debug__:
            #    print("New function arguments")
            #    for new_arg in transformed_new_args:
            #        print(ast.dump(new_arg))

            # Change the function args by the subscript expressions
            node.args = transformed_new_args

            # Transform all the new return variables into its subscript
            transformed_return_vars = []
            return_vars = self.task2ret_vars[original_name]
            for ret_var in return_vars:
                transformed_return_vars.append(vars2new_subscripts[ret_var])

            # if __debug__:
            #    print("New function return variables")
            #    for ret_var in transformed_return_vars:
            #        print(ast.dump(ret_var))

            # Change the function call by an assignment if there are return variables
            import copy
            copied_node = copy.deepcopy(node)
            if len(transformed_return_vars) > 0:
                if len(transformed_return_vars) == 1:
                    target = transformed_return_vars[0]
                else:
                    target = _ast.Tuple(elts=transformed_return_vars)
                new_node = _ast.Assign(targets=[target], value=copied_node)
            else:
                new_node = copied_node

            if __debug__:
                logger.debug("New task call")
                logger.debug(ast.dump(new_node))

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

    def test_multiply(self):
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
        test_module = importlib.import_module("pycompss.util.translators.py2pycompss.tests.test2_multiply_func")
        func = getattr(test_module, func_name)

        # Create list of parallel py codes
        src_file0 = tests_path + "/test2_multiply.src.python"
        par_py_files = [src_file0]

        # Output file
        out_file = tests_path + "/test2_multiply.out.pycompss"

        # Translate
        Py2PyCOMPSs.translate(func, par_py_files, out_file)

        # Check file content
        expected_file = tests_path + "/test2_multiply.expected.pycompss"
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
