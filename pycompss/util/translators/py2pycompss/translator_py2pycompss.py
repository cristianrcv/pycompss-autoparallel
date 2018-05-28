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

logger = logging.getLogger(__name__)


#
# Translator class
#

class Py2PyCOMPSs(object):

    @staticmethod
    def translate(func, par_py_files, output, taskify_loop_level=None):
        """
        Substitutes the given parallel python files into the original
        function code and adds the required PyCOMPSs annotations. The
        result is stored in the given output file

        :param func: Python original function
        :param par_py_files: List of files containing the Python parallelization of each for block in the func_source
        :param output: PyCOMPSs file path
        :param taskify_loop_level: Loop depth to perform taskification (default None)
        :raise Py2PyCOMPSsException:
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
        task2headers = {}
        task2func_code = {}
        output_loops_code = []
        task_counter_id = 0

        # Process each par_py file
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
                if isinstance(statement, ast.Import):
                    if not Py2PyCOMPSs._contains_import_statement(statement, output_imports):
                        output_imports.append(statement)
                elif isinstance(statement, ast.FunctionDef):
                    task_func_name = statement.name
                    # Update name to avoid override between par_py files
                    task_counter_id += 1
                    task_new_name = "S" + str(task_counter_id)
                    task2new_name[task_func_name] = task_new_name

                    # Update task
                    header, code, original_args, new_args, ret_args, new_vars2subscripts = Py2PyCOMPSs._process_task(
                        statement, task_new_name)

                    task2headers[task_new_name] = header
                    task2func_code[task_new_name] = code
                    task2original_args[task_new_name] = original_args
                    task2new_args[task_new_name] = new_args
                    task2ret_args[task_new_name] = ret_args
                    task2vars2subscripts[task_new_name] = new_vars2subscripts
                else:
                    # Generated CLooG code for parallel loop
                    # Check for calls to task methods and replace them. Leave the rest intact
                    rc = _RewriteCallees(task2new_name, task2original_args, task2new_args, task2ret_args,
                                         task2vars2subscripts)
                    new_statement = rc.visit(statement)
                    # Loop tasking
                    if taskify_loop_level is not None and taskify_loop_level > 0:
                        lt = _LoopTasking(taskify_loop_level, task_counter_id, task2headers, task2func_code)
                        lt_new_statement = lt.visit(new_statement)
                        task_counter_id = lt.get_final_task_counter_id()
                        task2headers = lt.get_final_task2headers()
                        task2func_code = lt.get_final_task2func_code()
                    else:
                        lt_new_statement = new_statement
                    # Store new code
                    output_code.append(lt_new_statement)

            # Store output code
            output_loops_code.append(output_code)

        # Substitute loops code on function code
        loop_index = 0
        new_body = []
        for statement in func_ast.body:
            if isinstance(statement, ast.For):
                # Check the correctness of the number of generated loops
                if loop_index >= len(output_loops_code):
                    raise Py2PyCOMPSsException(
                        "[ERROR] The number of generated parallel FORs is < than the original number of main FORs")
                # Substitute code with all parallel loop statements
                new_body.extend(output_loops_code[loop_index])
                # Add barrier
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
            if isinstance(decorator, ast.Call):
                if decorator.func.id == "parallel":
                    func_ast.decorator_list.remove(decorator)

        # Debug
        # if __debug__:
        #    logger.debug("OUTPUT IMPORTS:")
        #    for oi in output_imports:
        #        logger.debug(ast.dump(oi))
        #    logger.debug("OUTPUT TASKS:")
        #    for task_name, task_code in task2func_code.items():
        #        task_header = task2headers.get(task_name)
        #        logger.debug(task_name)
        #        logger.debug(task_header)
        #        logger.debug(ast.dump(task_code))
        #    logger.debug("OUTPUT CODE:")
        #    logger.debug(ast.dump(func_ast.body))

        # Print content to PyCOMPSs file
        from pycompss.util.translators.astor_source_gen.pycompss_source_gen import PyCOMPSsSourceGen
        with open(output, 'w') as f:
            # Write header
            print("# [COMPSs Autoparallel] Begin Autogenerated code", file=f)
            # Write imports
            for oi in set(output_imports):
                print(astor.to_source(oi, pretty_source=PyCOMPSsSourceGen.long_line_ps), file=f)
            # Write default PyCOMPSs imports
            print("from pycompss.api.api import compss_barrier, compss_wait_on, compss_open", file=f)
            print("from pycompss.api.task import task", file=f)
            print("from pycompss.api.parameter import *", file=f)
            if taskify_loop_level is not None and taskify_loop_level > 0:
                print("from pycompss.util.translators.arg_utils.arg_utils import ArgUtils", file=f)
            print("", file=f)
            print("", file=f)
            # Write tasks
            for task_name in sorted(task2func_code, key=Py2PyCOMPSs._task_name_sort):
                task_code = task2func_code.get(task_name)
                task_header = task2headers.get(task_name)
                # Print task header if method is still a task
                if task_header is not None:
                    print(task_header, file=f)
                # Add method code
                print(astor.to_source(task_code, pretty_source=PyCOMPSsSourceGen.long_line_ps), file=f)
                print("", file=f)
            # Write function
            print(astor.to_source(func_ast, pretty_source=PyCOMPSsSourceGen.long_line_ps), file=f)
            # Write header
            print("# [COMPSs Autoparallel] End Autogenerated code", file=f)

        if __debug__:
            logger.debug("[Py2PyCOMPSs] End translation")

    @staticmethod
    def _task_name_sort(task_name):
        """
        Function used to sort the entries of a list of the form [a-zA-Z]*[0-9]*

        :param task_name: name to evaluate
        :return result: Compare value
        """

        import re
        res = []
        for c in re.split('(\d+)', task_name):
            if c.isdigit():
                res.append(int(c))
            else:
                res.append(c)
        return res

    @staticmethod
    def _contains_import_statement(import_statement, list_of_imports):
        """
        Function to determine if an import already exists in the given list of imports

        :param import_statement: Import to evaluate
        :param list_of_imports: List of saved imports
        :return: True if the import already exists, False otherwise
        """

        for i in list_of_imports:
            if Py2PyCOMPSs._equal_imports(import_statement, i):
                return True
        return False

    @staticmethod
    def _equal_imports(import_statement1, import_statement2):
        """
        Determines whether two import statements are equal or not

        :param import_statement1: Import statement 1
        :param import_statement2: Import statement 2
        :return: True if import_statement1 is equal to import_statement2, False otherwise
        """

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

        :param func: AST node representing the head of the Python function
        :param new_name: New name for the Python function
        :return task_header: String representing the function task header
        :return new_func: new AST node representing the head of the function
        :return original_args: List of original arguments
        :return new_args: List of new arguments
        :return ret_args: List of return variables
        :return var2subscript: Dictionary containing the mapping of new variables to previous subscripts
        :raise Py2PyCOMPSsException:
        """

        if __debug__:
            import astor
            from pycompss.util.translators.astor_source_gen.pycompss_source_gen import PyCOMPSsSourceGen
            logger.debug("Original task definition")
            # logger.debug(ast.dump(func))
            logger.debug(astor.to_source(func, pretty_source=PyCOMPSsSourceGen.long_line_ps))

        # Rename function
        func.name = new_name

        # Rewrite subscripts by plain variables
        rs = _RewriteSubscript()
        new_func = rs.visit(func)
        var2subscript = rs.get_var_subscripts()

        # Process direction of parameters
        in_vars, out_vars, inout_vars, return_vars = Py2PyCOMPSs._process_parameters(new_func.body[0])

        # Add non subscript variables to var2subscript
        for var in in_vars + out_vars + inout_vars + return_vars:
            if var not in var2subscript.keys():
                var_ast = ast.Name(id=var)
                var2subscript[var] = var_ast

        # Rewrite function if it has a return
        if len(return_vars) > 0:
            new_func.body[0] = ast.Return(value=new_func.body[0].value)

        # Create new function arguments
        new_args = []
        for var in in_vars + out_vars + inout_vars:
            if var not in new_args:
                var_ast = ast.Name(id=var)
                new_args.append(var_ast)
        original_args = new_func.args.args
        new_func.args.args = new_args

        # Construct task header
        task_header = Py2PyCOMPSs._construct_task_header(in_vars, out_vars, inout_vars, return_vars, [], None)

        # Return task header and new function
        if __debug__:
            import astor
            from pycompss.util.translators.astor_source_gen.pycompss_source_gen import PyCOMPSsSourceGen
            logger.debug("New task definition")
            # logger.debug(ast.dump(new_func))
            # logger.debug(return_vars)
            logger.debug(astor.to_source(new_func, pretty_source=PyCOMPSsSourceGen.long_line_ps))

        return task_header, new_func, original_args, new_args, return_vars, var2subscript

    @staticmethod
    def _process_parameters(statement):
        """
        Processes all the directions of the parameters found in the given statement

        :param statement: AST node representing the head of the statement
        :return in_vars: List of names of IN variables
        :return out_vars: List of names of OUT variables
        :return inout_vars: List of names of INOUT variables
        :return return_vars: List of names of RETURN variables
        :raise Py2PyCOMPSsException:
        """

        in_vars = Py2PyCOMPSs._get_access_vars(statement)

        out_vars = []
        inout_vars = []
        return_vars = []

        target_vars = Py2PyCOMPSs._get_target_vars(statement)
        if isinstance(statement.value, ast.Call):
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

        :param statement: AST node representing the head of the statement
        :param is_target: Boolean to indicate if we are inside a target node or not
        :return in_vars: List of names of accessed variables
        """

        # Direct case
        if isinstance(statement, ast.Name):
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

        :param statement: AST node representing the head of the statement
        :return target_vars: List of names of target variables
        """

        if isinstance(statement, ast.Assign):
            # Assign can have more than one target var, process all
            target_vars = []
            for t in statement.targets:
                target_vars.extend(Py2PyCOMPSs._get_target_vars(t))
            return target_vars
        elif isinstance(statement, ast.AugAssign):
            # Operations on assign have a single target var
            return Py2PyCOMPSs._get_target_vars(statement.target)
        elif isinstance(statement, ast.Name):
            # Add Id of used variable
            return [statement.id]
        elif isinstance(statement, ast.Subscript):
            # On array access process value (not indexes)
            return Py2PyCOMPSs._get_target_vars(statement.value)
        elif isinstance(statement, ast.Expr):
            # No target on void method call
            return []
        elif isinstance(statement, ast.List):
            # Process all the elements of the list
            target_vars = []
            for list_fields in statement.elts:
                target_vars.extend(Py2PyCOMPSs._get_target_vars(list_fields))
            return target_vars
        elif isinstance(statement, ast.Tuple):
            # Process all the fields of the tuple
            target_vars = []
            for tuple_field in statement.elts:
                target_vars.extend(Py2PyCOMPSs._get_target_vars(tuple_field))
            return target_vars
        else:
            # Unrecognised statement expression
            raise Py2PyCOMPSsException("[ERROR] Unrecognised expression on write operation " + str(type(statement)))

    @staticmethod
    def _construct_task_header(in_vars, out_vars, inout_vars, return_vars, task_star_args, len_var):
        """
        Constructs the task header corresponding to the given IN, OUT, and INOUT variables

        :param in_vars: List of names of IN variables
        :param out_vars: List of names of OUT variables
        :param inout_vars: List of names of INOUT variables
        :param return_vars: List of names of RETURN variables
        :param task_star_args: List of variables that will be passed as star arguments
        :param len_var: Variable containing the name of the global variable used for star_args length
        :return task_header: String representing the PyCOMPSs task header
        """

        # Construct task header
        task_header = "@task("

        # Add parameters information
        first = True
        for iv in in_vars:
            if iv not in task_star_args:
                if not first:
                    task_header += ", "
                else:
                    first = False
                task_header += iv + "=IN"
        for ov in out_vars:
            if ov not in task_star_args:
                if not first:
                    task_header += ", "
                else:
                    first = False
                task_header += ov + "=OUT"
        for iov in inout_vars:
            if iov not in task_star_args:
                if not first:
                    task_header += ", "
                else:
                    first = False
                task_header += iov + "=INOUT"

        # Add return information
        if len(task_star_args) > 0:
            if not first:
                task_header += ", "
            task_header += "returns=\"" + len_var + "\""
        elif len(return_vars) > 0:
            if not first:
                task_header += ", "
            task_header += "returns=" + str(len(return_vars))

        # Close task header
        task_header += ")"

        return task_header


#
# Class Node transformer for subscripts to plain variables
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
        """
        Initialize Rewrite Subscript internal structures
        """

        self.var_counter = 1
        self.var2subscript = {}

    def get_next_var(self):
        """
        Returns the next variable AST node and name

        :return var_ast: New variable AST representation
        :return var_name: New variable name
        """

        # Create new var name
        var_name = "var" + str(self.var_counter)
        var_ast = ast.Name(id=var_name)

        # Increase counter for next call
        self.var_counter += 1

        # Return var object
        return var_ast, var_name

    def get_var_subscripts(self):
        """
        Returns the mapping between detected variables and its subscripts

        :return var2subscript: Map between variable names and its subscripts
        """

        return self.var2subscript

    def visit_Subscript(self, node):
        """
        Modifies the subscript node by a plain variable and internally stores the relation between
        the new variable and the old subscript

        :param node: Subscript node to process
        :return new_node: New AST representation of a plain variable
        """

        var_ast, var_name = self.get_next_var()
        self.var2subscript[var_name] = node
        return ast.copy_location(var_ast, node)


#
# Class Node transformer for subscripts to 1D lists
#

class _RewriteSubscriptToSubscript(ast.NodeTransformer):
    """
    Node Transformer class to visit all the Subscript AST nodes and change them
    by a plain variable access. The performed modifications are stored inside the
    class object so that users can retrieve them when necessary

    Attributes:
            - loop_ind : Subscript index
            - var_counter : Number of replaced variables
            - var2subscript : Dictionary mapping replaced variables by its original expression
    """

    def __init__(self, loop_ind):
        """
        Initializes the _RewriteSubscriptToSubscript internal structures.

        :param loop_ind: Loop index AST representation
        """

        self.loop_ind = loop_ind
        self.var_counter = 1
        self.var2subscript = {}

    def get_var_subscripts(self):
        """
        Returns the mapping between detected variables and its subscripts

        :return var2subscript: Map between variable names and its subscripts
        """

        return self.var2subscript

    def visit_Subscript(self, node):
        """
        Modifies the subscript node by a 1D subscript variable and internally stores the relation between
        the new variable and the old subscript

        :param node: Subscript node to process
        :return new_node: New AST representation of a plain variable
        """

        # Check that variable has not been found previously
        for var_name, var_subscript in self.var2subscript.items():
            if _RewriteSubscriptToSubscript._compare_ast(node, var_subscript):
                var_ast = self._get_var_ast(var_name)
                return ast.copy_location(var_ast, node)

        # Register new subscript
        var_name = self._get_next_var()
        self.var2subscript[var_name] = node

        var_ast = self._get_var_ast(var_name)
        return ast.copy_location(var_ast, node)

    def _get_next_var(self):
        """
        Returns the next variable name

        :return var_name: Variable name
        """

        # Create new var name
        var_name = "var" + str(self.var_counter)

        # Increase counter for next call
        self.var_counter += 1

        # Return var object
        return var_name

    def _get_var_ast(self, var_name):
        """
        Creates an AST subscript representation of the variable var_name

        :param var_name: String containing the name of the variable
        :return var_ast: AST subscript representation of the given variable
        """

        # Create new var_ast from var_name
        # We can insert the plain loop index because offsets are computed on the callee
        var_ast = ast.Subscript(value=ast.Name(id=var_name), slice=ast.Index(value=self.loop_ind))

        return var_ast

    @staticmethod
    def _compare_ast(node1, node2):
        """
        Compares the given two AST nodes to check if they are equal or not. Does not consider lineno, col_offset,
        ctx or _pp fields

        :param node1: First node to compare
        :param node2: Second node to compare
        :return: True if node1 equals node2, False otherwise
        """

        # Check node types (so we guarantee they have the same fields)
        if type(node1) is not type(node2):
            return False

        # Do not perform recursion on subscripts but compare its expressions
        if isinstance(node1, ast.Index):
            import astor
            from sympy import simplify

            expr1 = simplify(astor.to_source(node1.value))
            expr2 = simplify(astor.to_source(node2.value))

            return expr1 == expr2

        # Regular recursion checks
        if isinstance(node1, ast.AST):
            for k, v in vars(node1).iteritems():
                if k in ('lineno', 'col_offset', 'ctx', '_pp'):
                    continue
                if not _RewriteSubscriptToSubscript._compare_ast(v, getattr(node2, k)):
                    return False
            return True
        elif isinstance(node1, list):
            import itertools
            return all(itertools.starmap(_RewriteSubscriptToSubscript._compare_ast, itertools.izip(node1, node2)))
        else:
            return node1 == node2


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
        """
        Initializes _RewriteCallees internal structures

        :param task2new_name: Dictionary mapping the function variable original and new names
        :param task2original_args: Dictionary mapping the function name to its original arguments
        :param task2new_args: Dictionary mapping the function name to its new arguments
        :param task2ret_vars: Dictionary mapping the function name to its return values
        :param task2vars2subscripts: Dictionary mapping the function name to its vars-subscripts dictionary
        """

        self.task2new_name = task2new_name
        self.task2original_args = task2original_args
        self.task2new_args = task2new_args
        self.task2ret_vars = task2ret_vars
        self.task2vars2subscripts = task2vars2subscripts

    def visit_Call(self, node):
        """
        Process the call node to modify the callee with the new task_function parameters

        :param node: Call AST node
        :return new_call: New Call AST node containing the modified task call
        """

        original_name = node.func.id

        if original_name in self.task2new_name.keys():
            # It is a call to a task, we must replace it by the new callee
            if __debug__:
                import astor
                from pycompss.util.translators.astor_source_gen.pycompss_source_gen import PyCOMPSsSourceGen
                logger.debug("Original task call")
                # logger.debug(ast.dump(node))
                logger.debug(astor.to_source(node, pretty_source=PyCOMPSsSourceGen.long_line_ps))

            # Function new name
            new_name = self.task2new_name[original_name]

            # Replace function name
            node.func = ast.Name(id=new_name)

            # Map function arguments to call arguments
            import copy
            func_args = self.task2original_args[new_name]
            func_args2callee_args = {}
            for i in range(len(node.args)):
                func_arg = func_args[i].id
                callee_arg = copy.deepcopy(node.args[i])
                func_args2callee_args[func_arg] = callee_arg

            # Transform function variables to call arguments on all var2subscript
            vars2subscripts = copy.deepcopy(self.task2vars2subscripts[new_name])
            vars2new_subscripts = {}
            for var, subscript in vars2subscripts.items():
                ran = _RewriteArgNames(func_args2callee_args)
                vars2new_subscripts[var] = ran.visit(subscript)

            # if __debug__:
            #    logger.debug("Vars to subscripts:")
            #    for k, v in vars2new_subscripts.items():
            #        logger.debug(str(k) + " -> " + str(ast.dump(v)))

            # Transform all the new arguments into its subscript
            transformed_new_args = []
            new_args = self.task2new_args[new_name]
            for arg in new_args:
                transformed_new_args.append(vars2new_subscripts[arg.id])

            # if __debug__:
            #    logger.debug("New function arguments")
            #    for new_arg in transformed_new_args:
            #        logger.debug(ast.dump(new_arg))

            # Change the function args by the subscript expressions
            node.args = transformed_new_args

            # Transform all the new return variables into its subscript
            transformed_return_vars = []
            return_vars = self.task2ret_vars[new_name]
            for ret_var in return_vars:
                transformed_return_vars.append(vars2new_subscripts[ret_var])

            # if __debug__:
            #    logger.debug("New function return variables")
            #    for ret_var in transformed_return_vars:
            #        logger.debug(ast.dump(ret_var))

            # Change the function call by an assignment if there are return variables
            import copy
            copied_node = copy.deepcopy(node)
            if len(transformed_return_vars) > 0:
                if len(transformed_return_vars) == 1:
                    target = transformed_return_vars[0]
                else:
                    target = ast.Tuple(elts=transformed_return_vars)
                new_node = ast.Assign(targets=[target], value=copied_node)
            else:
                new_node = copied_node

            if __debug__:
                import astor
                from pycompss.util.translators.astor_source_gen.pycompss_source_gen import PyCOMPSsSourceGen
                logger.debug("New task call")
                # logger.debug(ast.dump(new_node))
                logger.debug(astor.to_source(new_node, pretty_source=PyCOMPSsSourceGen.long_line_ps))

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
        - func_args2callee_args : Dictionary mapping the function variable names and its callee expression
    """

    def __init__(self, func_args2callee_args):
        """
        Initializes _RewriteArgNames internal structures

        :param func_args2callee_args: Dictionary mapping the function variable names and its callee expression
        """

        self.func_args2callee_args = func_args2callee_args

    def visit_Name(self, node):
        """
        Rewrites each variable node with the new variable name

        :param node: Variable AST name node
        :return new_node: AST Node representing the new name of the variable
        """

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
# Class Node transformer for loop tasking
#

class _LoopTasking(ast.NodeTransformer):
    """
    Node Transformer class to visit all the FOR loops and taskify them if required

    Attributes:
        - taskify_loop_level : Depth level of for loop to taskify
        - task_counter_id : Task counter
        - task2headers : Map containing the task name and its header
        - task2func_code : Map containing the task name and its AST code representation
    """

    def __init__(self, taskify_loop_level, task_counter_id, task2headers, task2func_code):
        """
        Initializes the _LoopTasking internal structures

        :param taskify_loop_level: Depth level of for loop to taskify
        :param task_counter_id: Task counter
        :param task2headers: Map containing the task names and their headers
        :param task2func_code: Map containing the task names and their AST code representations
        """

        self.taskify_loop_level = taskify_loop_level
        self.task_counter_id = task_counter_id
        self.task2headers = task2headers
        self.task2func_code = task2func_code

    def get_final_task_counter_id(self):
        """
        Returns the task counter

        :return task_counter_id: task counter
        """

        return self.task_counter_id

    def get_final_task2headers(self):
        """
        Returns the map containing the task names and their headers

        :return task2headers: Map containing the task names and their headers
        """

        return self.task2headers

    def get_final_task2func_code(self):
        """
        Returns the map containing the task names and their AST code representations

        :return task2func_code: Map containing the task names and their AST code representations
        """

        return self.task2func_code

    def visit_For(self, node):
        """
        Checks whether the node is a ast.For instance and it is valid for taskification. If so, creates the
        corresponding taskification task, and modifies the current node with a call to a it

        :param node: For AST node representation
        :return new_node: If the node is valid for taskification, a AST Call node. Otherwise the same node
        """

        # Compute for level
        for_level = _LoopTasking._get_for_level(node)

        # Taskify for loop if it has the right depth-level
        # TODO: Support N-depth taskification (currently, 1D)
        if for_level == self.taskify_loop_level:
            if __debug__:
                import astor
                from pycompss.util.translators.astor_source_gen.pycompss_source_gen import PyCOMPSsSourceGen
                logger.debug("Original Taskified loop:")
                # logger.debug(ast.dump(node))
                logger.debug(astor.to_source(node, pretty_source=PyCOMPSsSourceGen.long_line_ps))

            # Obtain loop index
            loop_ind = node.target
            loop_bounds = node.iter

            # Rebuild loop body with plain variables
            import copy
            func_node = copy.deepcopy(node)
            rs = _RewriteSubscriptToSubscript(loop_ind)
            func_node = rs.visit(func_node)
            var2subscript = rs.get_var_subscripts()

            # Process direction of parameters
            in_vars, out_vars, inout_vars, return_vars = self._process_parameters(func_node)

            # Add non subscript variables to var2subscript
            for var in in_vars + out_vars + inout_vars + return_vars:
                if var not in var2subscript.keys():
                    var_ast = ast.Name(id=var)
                    var2subscript[var] = var_ast

            # Create new function arguments
            task_args = []
            task_star_args = []
            for var in in_vars + out_vars + inout_vars:
                var_ast = ast.Name(id=var)
                # Add subscript variables to star_args. Add the rest of variables to task header
                if isinstance(var2subscript[var], ast.Name):
                    # Do not repeat variables
                    if var not in task_args:
                        task_args.append(var_ast)
                else:
                    # Do not repeat variables
                    if var not in task_star_args:
                        task_star_args.append(var)

            # if __debug__:
            #    logger.debug("Task function arguments:")
            #    for ta in task_args:
            #        logger.debug(ast.dump(ta))
            #        logger.debug(astor.to_source(ta))
            #    logger.debug("Task function star arguments:")
            #    for tsa in task_star_args:
            #        logger.debug(ast.dump(tsa))
            #        logger.debug(astor.to_source(tsa))

            # New task variables
            self.task_counter_id += 1
            task_name = "LT" + str(self.task_counter_id)
            task_vararg = "args" if len(task_star_args) > 0 else None
            len_var = task_name + "_args_size"

            # Construct task header
            task_header = Py2PyCOMPSs._construct_task_header(in_vars, out_vars, inout_vars, return_vars, task_star_args,
                                                             len_var)

            # Create task definition node
            func_node = _LoopTasking._fix_loop_bounds(func_node)
            task_body = _LoopTasking._create_task_body_with_argutils(func_node, task_star_args, len_var)
            new_task = ast.FunctionDef(name=task_name,
                                       args=ast.arguments(args=task_args, vararg=task_vararg, kwarg=None, defaults=[]),
                                       body=task_body,
                                       decorator_list=[])
            self.task2func_code[task_name] = new_task
            self.task2headers[task_name] = task_header

            # Modify the task call arguments
            call_func = ast.Name(id=task_name)
            call_args = []
            for ta in task_args:
                arg_name = ta.id
                orig_call_arg = var2subscript[arg_name]
                if isinstance(orig_call_arg, ast.Name):
                    # Argument is a plain variable, no changes
                    call_args.append(orig_call_arg)
                elif isinstance(orig_call_arg, ast.Subscript):
                    # Argument is a subscript
                    call_arg = ast.ListComp(elt=orig_call_arg,
                                            generators=[ast.comprehension(target=loop_ind, iter=loop_bounds, ifs=[])])
                    call_args.append(call_arg)
                else:
                    # Unrecognised argument type
                    raise Py2PyCOMPSsException("[ERROR] Unrecognised call argument type " + str(type(orig_call_arg)))

            # Replace the current node by a task callee
            if len(task_star_args) == 0:
                # Regular callee expression
                new_node = ast.Expr(value=ast.Call(func=call_func,
                                                   args=call_args,
                                                   keywords=[],
                                                   starargs=None,
                                                   kwargs=None))
            else:
                # Loop Tasking callee expression
                new_nodes = []

                # Store operations for build and destroy chunks
                # Add assign build chunks to new_nodes
                chunked_task_star_args = []
                unassign_loop_var = ast.Name(id=task_name + "_index")
                unassign_nodes = []
                star_arg_ind = 0
                for var_name in task_star_args:
                    orig_call_arg = var2subscript[var_name]
                    if isinstance(orig_call_arg, ast.Name):
                        # Argument is a plain variable, no changes
                        chunked_task_star_args.append(orig_call_arg)
                    elif isinstance(orig_call_arg, ast.Subscript):
                        # Argument is a subscript
                        star_arg_name = task_name + "_aux_" + str(star_arg_ind)
                        star_arg_ind = star_arg_ind + 1
                        star_arg = ast.Name(id=star_arg_name)
                        # Store star_arg name
                        chunked_task_star_args.append(star_arg)
                        # Insert build assignation to new_nodes
                        assign_node = ast.Assign(targets=[star_arg],
                                                 value=ast.ListComp(elt=orig_call_arg,
                                                                    generators=[ast.comprehension(target=loop_ind,
                                                                                                  iter=loop_bounds,
                                                                                                  ifs=[])]))
                        new_nodes.append(assign_node)
                        # Store destroy assignation to later append to new_nodes
                        unassign_node = ast.Assign(targets=[orig_call_arg],
                                                   value=ast.Subscript(value=star_arg,
                                                                       slice=ast.Index(value=unassign_loop_var)))
                        unassign_nodes.append(unassign_node)

                    else:
                        # Unrecognised argument type
                        raise Py2PyCOMPSsException(
                            "[ERROR] Unrecognised call argument type " + str(type(orig_call_arg)))

                # Insert ArgUtils instantiation
                argutils_var = ast.Name(id=task_name + "_argutils")
                argutils_node = ast.Assign(targets=[argutils_var],
                                           value=ast.Call(func=ast.Name(id="ArgUtils"),
                                                          args=[],
                                                          keywords=[],
                                                          starargs=None,
                                                          kwargs=None))
                new_nodes.append(argutils_node)

                # Flatten args
                flat_args_var = ast.Name(id=task_name + "_flat_args")
                flat_args_node = ast.Assign(targets=[flat_args_var],
                                            value=ast.Call(func=ast.Attribute(value=argutils_var, attr="flatten"),
                                                           args=chunked_task_star_args,
                                                           keywords=[],
                                                           starargs=None,
                                                           kwargs=None))
                new_nodes.append(flat_args_node)

                # Insert Compute length
                global_node = ast.Global(names=[len_var])
                assign_global_node = ast.Assign(targets=[ast.Name(id=len_var)],
                                                value=ast.Call(func=ast.Name(id="len"),
                                                               args=[flat_args_var],
                                                               keywords=[],
                                                               starargs=None,
                                                               kwargs=None))
                new_nodes.append(global_node)
                new_nodes.append(assign_global_node)

                # Insert task call
                new_args_var = ast.Name(id=task_name + "_new_args")
                task_call_node = ast.Assign(targets=[new_args_var],
                                            value=ast.Call(func=call_func,
                                                           args=call_args,
                                                           keywords=[],
                                                           starargs=flat_args_var,
                                                           kwargs=None))
                new_nodes.append(task_call_node)

                # Rebuild chunks from flat new arguments
                rebuild_node = ast.Assign(targets=[ast.Tuple(elts=chunked_task_star_args)],
                                          value=ast.Call(func=ast.Attribute(value=argutils_var, attr="rebuild"),
                                                         args=[new_args_var],
                                                         keywords=[],
                                                         starargs=None,
                                                         kwargs=None))
                new_nodes.append(rebuild_node)

                # Undo chunks to user subscripts
                loop_var_init_node = ast.Assign(targets=[unassign_loop_var], value=ast.Num(n=0))
                new_nodes.append(loop_var_init_node)

                incr_index_node = ast.Assign(targets=[unassign_loop_var],
                                             value=ast.BinOp(left=unassign_loop_var,
                                                             op=ast.Add(),
                                                             right=ast.Num(n=1)))
                unassign_nodes.append(incr_index_node)
                loop_unassign_node = ast.For(target=loop_ind, iter=loop_bounds, body=unassign_nodes, orelse=[])
                new_nodes.append(loop_unassign_node)

                # Assign to function return
                new_node = new_nodes

            if __debug__:
                import astor
                from pycompss.util.translators.astor_source_gen.pycompss_source_gen import PyCOMPSsSourceGen
                logger.debug("New Taskified task:")
                # logger.debug(ast.dump(new_task))
                logger.debug(astor.to_source(new_task, pretty_source=PyCOMPSsSourceGen.long_line_ps))
                logger.debug("New Taskified loop:")
                if isinstance(new_node, list):
                    for internal_op in new_node:
                        logger.debug(astor.to_source(internal_op, pretty_source=PyCOMPSsSourceGen.long_line_ps))
                else:
                    logger.debug(astor.to_source(new_node, pretty_source=PyCOMPSsSourceGen.long_line_ps))

            # Remove internal loop statements from task headers
            self._remove_statements_from_tasks(node)
        else:
            new_node = node

        # Process children
        self.generic_visit(node)

        # Return modified node
        return new_node

    @staticmethod
    def _get_for_level(node):
        """
        Returns the number of nested for loops inside the current node

        :param node: Node to evaluate
        :return current_for_level: Number of nested for loops
        """

        # Child recursion
        current_for_level = 0
        for _, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        children_for_level = _LoopTasking._get_for_level(item)
                        if children_for_level > current_for_level:
                            current_for_level = children_for_level
            elif isinstance(value, ast.AST):
                children_for_level = _LoopTasking._get_for_level(value)
                if children_for_level > current_for_level:
                    current_for_level = children_for_level

        # Process current node
        if isinstance(node, ast.For):
            current_for_level = current_for_level + 1

        # Return all the outermost loops
        return current_for_level

    def _remove_statements_from_tasks(self, node):
        """
        If present, removes the current node from the task list

        :param node: Node to remove from the task list
        """
        # Process current node
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                task_name = node.func.id
                # Erase call if marked as task (it might be a non-task function call)
                if task_name in self.task2headers.keys():
                    del self.task2headers[task_name]

        # Child recursion
        for _, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self._remove_statements_from_tasks(item)
            elif isinstance(value, ast.AST):
                self._remove_statements_from_tasks(value)

    def _process_parameters(self, statement):
        """
        Processes all the directions of the parameters found in the given statement considering that they
         might be calls to existing tasks

        :param statement: AST node representing the head of the statement
        :return fixed_in_vars: List of names of IN variables
        :return fixed_out_vars: List of names of OUT variables
        :return fixed_inout_vars: List of names of INOUT variables
        :return fixed_return_vars: List of names of RETURN variables
        :raise Py2PyCOMPSsException:
        """

        in_vars, inout_vars, out_vars = self._get_access_vars(statement)
        out_vars.extend(_LoopTasking._get_target_vars(statement))

        # Fix duplicate variables and directions
        fixed_in_vars = []
        fixed_out_vars = []
        fixed_inout_vars = []
        fixed_return_vars = []
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
    def _fix_loop_bounds(func_node):
        """
        Fixes the loop bounds inside the task code when using Loop Tasking

        :param func_node: Node representing the for loop inside the task call
        :return func_node: Same node with modified loop bounds if required
        """

        # Get loop bounds
        iter_bounds = func_node.iter.args

        # Patch bounds when necessary
        if len(iter_bounds) != 1:
            # Loop bounds are of the form Min,Max or Min,Max,Step value
            import copy
            lb = copy.deepcopy(iter_bounds[0])
            ub = copy.deepcopy(iter_bounds[1])
            # Replace lower bound by 0
            iter_bounds[0] = ast.Num(n=0)
            # Replace upper bound by ub - lb
            iter_bounds[1] = ast.BinOp(left=ub, op=ast.Sub(), right=lb)

        return func_node

    @staticmethod
    def _create_task_body_with_argutils(func_node, var_list, len_var):
        """
        Creates the body of a LoopTasking function by adding the rebuild and flatten calls before and after the loop
        execution

        :param func_node: Node containing the loop execution
        :param var_list: List of stared variables
        :param len_var: Name of the global length variable
        :return: <List<ast.Node>> Containing the task body representation
        """

        # Construct an ast var list
        ast_var_list = []
        for var_name in var_list:
            ast_var_list.append(ast.Name(id=var_name))

        # Construct the global length  node
        global_node = ast.Global(names=[len_var])

        # Construct the rebuild arguments node
        rebuild_args_call = ast.Call(func=ast.Attribute(value=ast.Name(id="ArgUtils"), attr="rebuild_args"),
                                     args=[ast.Name(id="args")],
                                     keywords=[],
                                     starargs=None,
                                     kwargs=None)
        rebuild_node = ast.Assign(targets=[ast.Tuple(elts=ast_var_list)], value=rebuild_args_call)

        # Construct the flatten variables for return node
        flatten_args_call = ast.Call(func=ast.Attribute(value=ast.Name(id="ArgUtils"), attr="flatten_args"),
                                     args=ast_var_list,
                                     keywords=[],
                                     starargs=None,
                                     kwargs=None)
        flatten_node = ast.Return(value=flatten_args_call)

        # Construct the task body
        task_body = [global_node, rebuild_node, func_node, flatten_node]
        return task_body

    def _get_access_vars(self, statement, is_target=False):
        """
        Returns the accessed variable names within the given expression

        :param statement: AST node representing the head of the statement
        :param is_target: Indicates whether the current node belongs to a target node or not

        :return in_vars: List of names of accessed variables
        :return out_vars: List of names of OUT variables
        :return inout_vars: List of names of INOUT variables
        :raise Py2PyCOMPSsException: For unrecognised types as task arguments
        """

        in_vars = []
        inout_vars = []
        out_vars = []

        # Direct case
        if isinstance(statement, ast.Name):
            if not is_target:
                in_vars.append(statement.id)

            return in_vars, inout_vars, out_vars

        # Direct case
        if isinstance(statement, ast.Call):
            # Maybe its a call to a task we want to remove
            call_name = statement.func.id
            if call_name in self.task2headers.keys():
                # Retrieve task definition arguments and directions
                task_def_arguments = self.task2func_code[call_name].args.args
                task_def_args2directions = _LoopTasking._split_header(self.task2headers[call_name])
                # Get callee arguments
                task_call_args = statement.args
                # Process all arguments
                for position, task_def_arg in enumerate(task_def_arguments):
                    arg_name = task_def_arg.id
                    arg_direction = task_def_args2directions[arg_name]
                    call_name = _LoopTasking._get_var_name(task_call_args[position])
                    if arg_direction == "IN":
                        in_vars.append(call_name)
                    elif arg_direction == "INOUT":
                        inout_vars.append(call_name)
                    else:
                        out_vars.append(call_name)

                return in_vars, inout_vars, out_vars

        # Child recursion
        for field, value in ast.iter_fields(statement):
            if field == "func" or field == "keywords" or (isinstance(statement, ast.For) and field == "target"):
                # Skip function names, var_args keywords, and loop indexes
                pass
            else:
                children_are_target = is_target or (field == "targets")
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            iv, iov, ov = self._get_access_vars(item, children_are_target)
                            in_vars.extend(iv)
                            inout_vars.extend(iov)
                            out_vars.extend(ov)
                elif isinstance(value, ast.AST):
                    iv, iov, ov = self._get_access_vars(value, children_are_target)
                    in_vars.extend(iv)
                    inout_vars.extend(iov)
                    out_vars.extend(ov)
        return in_vars, inout_vars, out_vars

    @staticmethod
    def _get_var_name(node):
        """
        Returns the variable name of a Subscript or Name AST node

        :param node: Head node of the Subscript/Name statement
        :return: String containing the name of the variable
        """

        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return _LoopTasking._get_var_name(node.value)
        else:
            raise Py2PyCOMPSsException("[ERROR] Unrecognised type " + str(type(node)) + " on task argument")

    @staticmethod
    def _split_header(header):
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

    @staticmethod
    def _get_target_vars(statement):
        """
        Returns the target variables within given the expression

        :param statement: AST node representing the head of the statement
        :return target_vars: List of names of target variables
        """

        if isinstance(statement, ast.Assign):
            # Assign can have more than one target var, process all
            target_vars = []
            for t in statement.targets:
                target_vars.extend(_LoopTasking._get_target_vars(t))
            return target_vars
        elif isinstance(statement, ast.AugAssign):
            # Operations on assign have a single target var
            return _LoopTasking._get_target_vars(statement.target)
        elif isinstance(statement, ast.Name):
            # Add Id of used variable
            return [statement.id]
        elif isinstance(statement, ast.Subscript):
            # On array access process value (not indexes)
            return _LoopTasking._get_target_vars(statement.value)
        elif isinstance(statement, ast.List):
            # Process all the elements of the list
            target_vars = []
            for list_fields in statement.elts:
                target_vars.extend(_LoopTasking._get_target_vars(list_fields))
            return target_vars
        elif isinstance(statement, ast.Tuple):
            # Process all the fields of the tuple
            target_vars = []
            for tuple_field in statement.elts:
                target_vars.extend(_LoopTasking._get_target_vars(tuple_field))
            return target_vars
        elif isinstance(statement, ast.For):
            # Process each for body statement
            target_vars = []
            for loop_body_statement in statement.body:
                target_vars.extend(_LoopTasking._get_target_vars(loop_body_statement))
            return target_vars
        elif isinstance(statement, ast.Expr):
            # Process the value assignation
            return _LoopTasking._get_target_vars(statement.value)
        elif isinstance(statement, ast.Call):
            # When calling a function there are no written values
            return []
        else:
            # Unrecognised statement expression
            raise Py2PyCOMPSsException("[ERROR] Unrecognised expression on write operation " + str(type(statement)))


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

    def test_matmul_taskified(self):
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
        test_module = importlib.import_module("pycompss.util.translators.py2pycompss.tests.test2_matmul_taskified_func")
        func = getattr(test_module, func_name)

        # Create list of parallel py codes
        src_file0 = tests_path + "/test2_matmul_taskified.src.python"
        par_py_files = [src_file0]

        # Output file
        out_file = tests_path + "/test2_matmul_taskified.out.pycompss"

        # Translate
        Py2PyCOMPSs.translate(func, par_py_files, out_file, taskify_loop_level=1)

        # Check file content
        expected_file = tests_path + "/test2_matmul_taskified.expected.pycompss"
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
        test_module = importlib.import_module("pycompss.util.translators.py2pycompss.tests.test3_multiply_func")
        func = getattr(test_module, func_name)

        # Create list of parallel py codes
        src_file0 = tests_path + "/test3_multiply.src.python"
        par_py_files = [src_file0]

        # Output file
        out_file = tests_path + "/test3_multiply.out.pycompss"

        # Translate
        Py2PyCOMPSs.translate(func, par_py_files, out_file)

        # Check file content
        expected_file = tests_path + "/test3_multiply.expected.pycompss"
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

    def test_multiply_taskified(self):
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
        test_module = importlib.import_module(
            "pycompss.util.translators.py2pycompss.tests.test4_multiply_taskified_func")
        func = getattr(test_module, func_name)

        # Create list of parallel py codes
        src_file0 = tests_path + "/test4_multiply_taskified.src.python"
        par_py_files = [src_file0]

        # Output file
        out_file = tests_path + "/test4_multiply_taskified.out.pycompss"

        # Translate
        Py2PyCOMPSs.translate(func, par_py_files, out_file, taskify_loop_level=1)

        # Check file content
        expected_file = tests_path + "/test4_multiply_taskified.expected.pycompss"
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
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s - %(message)s')
    unittest.main()
