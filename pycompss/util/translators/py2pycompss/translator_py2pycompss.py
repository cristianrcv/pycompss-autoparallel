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
    def translate(func, par_py_files, output, taskify_loop_level=None):
        """
        Substitutes the given parallel python files into the original
        function code and adds the required PyCOMPSs annotations. The
        result is stored in the given output file

        Arguments:
                - func : Python original function
                - par_py_files : List of files containing the Python parallelization
                        of each for block in the func_source
                - output : PyCOMPSs file path
                - taskify_loop_level : Loop depth to perform taskification (default None)
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
                    new_name = "S" + str(task_counter_id)
                    task2new_name[task_func_name] = new_name

                    # Update task
                    header, code, original_args, new_args, ret_args, new_vars2subscripts = Py2PyCOMPSs._process_task(
                        statement, new_name)

                    task2headers[task_func_name] = header
                    task2func_code[task_func_name] = code
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
        # logger.debug("OUTPUT IMPORTS:")
        # for oi in output_imports:
        #    logger.debug(astor.dump_tree(oi))
        # logger.debug("OUTPUT TASKS:")
        # for task_name, task_code in task2func_code.items():
        #    task_header = task2headers.get(task_name)
        #    logger.debug(task_name)
        #    logger.debug(task_header)
        #    logger.debug(astor.dump_tree(task_code))
        # logger.debug("OUTPUT CODE:")
        # logger.debug(astor.dump_tree(func_ast.body))

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
            for task_name, task_code in sorted(task2func_code.items()):
                task_header = task2headers.get(task_name)
                # Print task header if method is still a task
                if task_header is not None:
                    print(task_header, file=f)
                # Add method code
                print(astor.to_source(task_code), file=f)
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
            # logger.debug(ast.dump(func))
            import astor
            logger.debug(astor.to_source(func))

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
        task_header = Py2PyCOMPSs._construct_task_header(in_vars, out_vars, inout_vars, return_vars)

        # Return task header and new function
        if __debug__:
            logger.debug("New task definition")
            # logger.debug(ast.dump(new_func))
            # logger.debug(return_vars)
            import astor
            logger.debug(astor.to_source(new_func))

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

        Arguments:
                - statement : AST node representing the head of the statement
        Return:
                - in_vars : List of names of accessed variables
        Raise:
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

        Arguments:
                - statement : AST node representing the head of the statement
        Return:
                - target_vars : List of names of target variables
        Raise:
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
        self.var_counter = 1
        self.var2subscript = {}

    def get_next_var(self):
        # Create new var name
        var_name = "var" + str(self.var_counter)
        var_ast = ast.Name(id=var_name)

        # Increase counter for next call
        self.var_counter += 1

        # Return var object
        return var_ast, var_name

    def get_var_subscripts(self):
        return self.var2subscript

    def visit_Subscript(self, node):
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
        self.loop_ind = loop_ind
        self.var_counter = 1
        self.var2subscript = {}

    def get_next_var(self):
        # Create new var name
        var_name = "var" + str(self.var_counter)
        var_ast = ast.Subscript(value=ast.Name(id=var_name), slice=ast.Index(value=self.loop_ind))

        # Increase counter for next call
        self.var_counter += 1

        # Return var object
        return var_ast, var_name

    def get_var_subscripts(self):
        return self.var2subscript

    def visit_Subscript(self, node):
        var_ast, var_name = self.get_next_var()
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
                # logger.debug(ast.dump(node))
                import astor
                logger.debug(astor.to_source(node))

            # Replace function name
            node.func = ast.Name(id=self.task2new_name[original_name])

            # Map function arguments to call arguments
            import copy
            func_args = self.task2original_args[original_name]
            func_args2callee_args = {}
            for i in range(len(node.args)):
                func_arg = func_args[i].id
                callee_arg = copy.deepcopy(node.args[i])
                func_args2callee_args[func_arg] = callee_arg

            # Transform function variables to call arguments on all var2subscript
            vars2subscripts = copy.deepcopy(self.task2vars2subscripts[original_name])
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
            new_args = self.task2new_args[original_name]
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
            return_vars = self.task2ret_vars[original_name]
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
                logger.debug("New task call")
                # logger.debug(ast.dump(new_node))
                import astor
                logger.debug(astor.to_source(new_node))

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
        self.taskify_loop_level = taskify_loop_level
        self.task_counter_id = task_counter_id
        self.task2headers = task2headers
        self.task2func_code = task2func_code

    def get_final_task_counter_id(self):
        return self.task_counter_id

    def get_final_task2headers(self):
        return self.task2headers

    def get_final_task2func_code(self):
        return self.task2func_code

    def visit_For(self, node):
        import astor

        # Compute for level
        for_level = _LoopTasking._get_for_level(node)

        # Taskify for loop if it has the right depth-level
        if for_level == self.taskify_loop_level:
            if __debug__:
                logger.debug("Original Taskified loop:")
                # logger.debug(astor.dump_tree(node))
                logger.debug(astor.to_source(node))

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
            for var in in_vars + out_vars + inout_vars:
                if var not in task_args:
                    var_ast = ast.Name(id=var)
                    task_args.append(var_ast)

            # Construct task header
            task_header = Py2PyCOMPSs._construct_task_header(in_vars, out_vars, inout_vars, return_vars)

            # Create task definition node
            import copy
            self.task_counter_id += 1
            task_name = "LT" + str(self.task_counter_id)
            task_body = [func_node]
            new_task = ast.FunctionDef(name=task_name,
                                       args=ast.arguments(args=task_args, vararg=None, kwarg=None, defaults=[]),
                                       body=task_body,
                                       decorator_list=[])
            self.task2func_code[task_name] = new_task
            self.task2headers[task_name] = task_header

            # Modify current for node by a task callee
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

            new_node = ast.Expr(value=ast.Call(func=call_func, args=call_args, keywords=[], starargs=None, kwargs=None))

            if __debug__:
                logger.debug("New Taskified loop:")
                # logger.debug(astor.dump_tree(new_node))
                logger.debug(astor.to_source(new_node))

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
        Processes all the directions of the parameters found in the given statement
        considering that they might be calls to existing tasks

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

    def _get_access_vars(self, statement, is_target=False):
        """
        Returns the accessed variable names within the given expression

        Arguments:
                - statement : AST node representing the head of the statement
        Return:
                - in_vars : List of names of accessed variables
                - out_vars : List of names of OUT variables
                - inout_vars : List of names of INOUT variables
        Raise:
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
                    call_name = task_call_args[position].value.id
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
    def _split_header(header):
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

        Arguments:
                - statement : AST node representing the head of the statement
        Return:
                - target_vars : List of names of target variables
        Raise:
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
            # TODO os.remove(out_file)
            pass

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


#
# MAIN
#

if __name__ == '__main__':
    unittest.main()
