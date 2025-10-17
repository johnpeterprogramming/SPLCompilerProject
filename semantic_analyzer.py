"""
SPL Semantic Analyzer
COS341 Semester Project 2025

Static semantic checker that validates name-scope rules for SPL.
Implements tree-crawling algorithm to check:
- Name conflicts in Everywhere scope
- Duplicate declarations in same scope
- Parameter shadowing
- Variable resolution (parameter -> local -> global)
- Undeclared variables
"""

from typing import Optional, List, Set
from spl_types import SemanticError
from spl_utils import ErrorReporter
from symbol_table import SymbolTable, SymbolType, ScopeType
from parser import (
    ASTNode, ProgramNode, VariableListNode, VariableNode,
    ProcDefListNode, ProcDefNode, FuncDefListNode, FuncDefNode,
    ParamNode, BodyNode, MainNode, AlgoNode, InstrNode,
    AssignNode, CallNode, AtomNode, TermNode, OutputNode
)


class SemanticAnalyzer:
    """Static semantic analyzer for SPL"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = ErrorReporter()
        
        # Track current scope context during tree traversal
        self.current_proc_or_func_id: Optional[int] = None
        self.current_scope_type: ScopeType = ScopeType.EVERYWHERE
    
    def analyze(self, ast: ProgramNode) -> SymbolTable:
        """
        Analyze the AST and build symbol table.
        Returns the symbol table. Check self.errors for any semantic errors.
        """
        if not isinstance(ast, ProgramNode):
            self.errors.add_error(SemanticError("Expected ProgramNode as root", 0, 0))
            return self.symbol_table
        
        try:
            self._analyze_program(ast)
        except SemanticError as e:
            self.errors.add_error(e)
        
        return self.symbol_table
    
    def _analyze_program(self, node: ProgramNode):
        """Analyze the entire program structure"""
        
        # Step 1: Collect all global variable names, procedure names, and function names
        global_vars = self._collect_variable_names(node.globals)
        proc_names = self._collect_proc_names(node.procs)
        func_names = self._collect_func_names(node.funcs)
        
        # Step 2: Check Everywhere scope rules
        # - No variable name may be identical with any function name
        # - No variable name may be identical with any procedure name
        # - No function name may be identical with any procedure name
        self._check_everywhere_scope_conflicts(global_vars, proc_names, func_names)
        
        # Step 3: Analyze global variables
        self._analyze_global_variables(node.globals)
        
        # Step 4: Analyze procedures
        self._analyze_procedures(node.procs)
        
        # Step 5: Analyze functions
        self._analyze_functions(node.funcs)
        
        # Step 6: Analyze main
        self._analyze_main(node.main)
    
    def _collect_variable_names(self, var_list: VariableListNode) -> Set[str]:
        """Collect all variable names from a variable list"""
        names = set()
        for var in var_list.variables:
            names.add(var.name)
        return names
    
    def _collect_proc_names(self, proc_list: ProcDefListNode) -> Set[str]:
        """Collect all procedure names"""
        names = set()
        for proc in proc_list.procs:
            names.add(proc.name)
        return names
    
    def _collect_func_names(self, func_list: FuncDefListNode) -> Set[str]:
        """Collect all function names"""
        names = set()
        for func in func_list.funcs:
            names.add(func.name)
        return names
    
    def _check_everywhere_scope_conflicts(self, global_vars: Set[str], 
                                         proc_names: Set[str], 
                                         func_names: Set[str]):
        """Check for name conflicts in the Everywhere scope"""
        
        # Check variables vs procedures
        var_proc_conflicts = global_vars & proc_names
        for name in var_proc_conflicts:
            self.errors.add_error(SemanticError(
                f"Name-rule violation: Variable '{name}' conflicts with procedure name in Everywhere scope",
                0, 0
            ))
        
        # Check variables vs functions
        var_func_conflicts = global_vars & func_names
        for name in var_func_conflicts:
            self.errors.add_error(SemanticError(
                f"Name-rule violation: Variable '{name}' conflicts with function name in Everywhere scope",
                0, 0
            ))
        
        # Check procedures vs functions
        proc_func_conflicts = proc_names & func_names
        for name in proc_func_conflicts:
            self.errors.add_error(SemanticError(
                f"Name-rule violation: Procedure '{name}' conflicts with function name in Everywhere scope",
                0, 0
            ))
    
    def _analyze_global_variables(self, var_list: VariableListNode):
        """Analyze global variables - check for duplicates"""
        seen_names = set()
        
        for var in var_list.variables:
            if var.name in seen_names:
                self.errors.add_error(SemanticError(
                    f"Name-rule violation: Duplicate global variable declaration '{var.name}'",
                    0, 0
                ))
            else:
                seen_names.add(var.name)
                # Add to symbol table
                self.symbol_table.add_symbol(
                    var.node_id, var.name, SymbolType.VARIABLE,
                    ScopeType.GLOBAL, var.node_id
                )
    
    def _analyze_procedures(self, proc_list: ProcDefListNode):
        """Analyze all procedure definitions"""
        seen_names = set()
        
        for proc in proc_list.procs:
            # Check for duplicate procedure names
            if proc.name in seen_names:
                self.errors.add_error(SemanticError(
                    f"Name-rule violation: Duplicate procedure declaration '{proc.name}'",
                    0, 0
                ))
            else:
                seen_names.add(proc.name)
                # Add procedure to symbol table
                self.symbol_table.add_symbol(
                    proc.node_id, proc.name, SymbolType.PROCEDURE,
                    ScopeType.PROCEDURE, proc.node_id
                )
            
            # Analyze procedure body
            self._analyze_proc_def(proc)
    
    def _analyze_functions(self, func_list: FuncDefListNode):
        """Analyze all function definitions"""
        seen_names = set()
        
        for func in func_list.funcs:
            # Check for duplicate function names
            if func.name in seen_names:
                self.errors.add_error(SemanticError(
                    f"Name-rule violation: Duplicate function declaration '{func.name}'",
                    0, 0
                ))
            else:
                seen_names.add(func.name)
                # Add function to symbol table
                self.symbol_table.add_symbol(
                    func.node_id, func.name, SymbolType.FUNCTION,
                    ScopeType.FUNCTION, func.node_id
                )
            
            # Analyze function body
            self._analyze_func_def(func)
    
    def _analyze_proc_def(self, proc: ProcDefNode):
        """Analyze a single procedure definition"""
        # Set context
        old_context = self.current_proc_or_func_id
        old_scope = self.current_scope_type
        self.current_proc_or_func_id = proc.node_id
        self.current_scope_type = ScopeType.LOCAL
        
        # Get parameter names
        param_names = set()
        for param in proc.params.params:
            if param.name in param_names:
                self.errors.add_error(SemanticError(
                    f"Name-rule violation: Duplicate parameter '{param.name}' in procedure '{proc.name}'",
                    0, 0
                ))
            else:
                param_names.add(param.name)
                # Add parameter to symbol table as local variable
                self.symbol_table.add_symbol(
                    param.node_id, param.name, SymbolType.VARIABLE,
                    ScopeType.LOCAL, param.node_id, proc.node_id
                )
        
        # Analyze body
        self._analyze_body(proc.body, param_names, proc.node_id, proc.name)
        
        # Restore context
        self.current_proc_or_func_id = old_context
        self.current_scope_type = old_scope
    
    def _analyze_func_def(self, func: FuncDefNode):
        """Analyze a single function definition"""
        # Set context
        old_context = self.current_proc_or_func_id
        old_scope = self.current_scope_type
        self.current_proc_or_func_id = func.node_id
        self.current_scope_type = ScopeType.LOCAL
        
        # Get parameter names
        param_names = set()
        for param in func.params.params:
            if param.name in param_names:
                self.errors.add_error(SemanticError(
                    f"Name-rule violation: Duplicate parameter '{param.name}' in function '{func.name}'",
                    0, 0
                ))
            else:
                param_names.add(param.name)
                # Add parameter to symbol table as local variable
                self.symbol_table.add_symbol(
                    param.node_id, param.name, SymbolType.VARIABLE,
                    ScopeType.LOCAL, param.node_id, func.node_id
                )
        
        # Get local variable names
        local_vars = set()
        for var in func.body.locals.params:  # locals are stored in a ParamNode
            local_vars.add(var.name)
        
        # Analyze body
        self._analyze_body(func.body, param_names, func.node_id, func.name)
        
        # Analyze return atom (needs access to param_names and local_vars)
        if func.return_atom:
            self._analyze_atom(func.return_atom, param_names, local_vars, func.node_id)
        
        # Restore context
        self.current_proc_or_func_id = old_context
        self.current_scope_type = old_scope
    
    def _analyze_body(self, body: BodyNode, param_names: Set[str], 
                     parent_id: int, parent_name: str):
        """Analyze procedure/function body"""
        
        # Get local variable names
        local_vars = set()
        for var in body.locals.params:  # locals are stored in a ParamNode
            # Check for shadowing of parameters
            if var.name in param_names:
                self.errors.add_error(SemanticError(
                    f"Name-rule violation: Local variable '{var.name}' shadows parameter in '{parent_name}'",
                    0, 0
                ))
            
            # Check for duplicate local variables
            if var.name in local_vars:
                self.errors.add_error(SemanticError(
                    f"Name-rule violation: Duplicate local variable '{var.name}' in '{parent_name}'",
                    0, 0
                ))
            else:
                local_vars.add(var.name)
                # Add to symbol table
                self.symbol_table.add_symbol(
                    var.node_id, var.name, SymbolType.VARIABLE,
                    ScopeType.LOCAL, var.node_id, parent_id
                )
        
        # Analyze algorithm
        self._analyze_algo(body.algo, param_names, local_vars, parent_id)
    
    def _analyze_main(self, main: MainNode):
        """Analyze main program"""
        # Set context
        old_scope = self.current_scope_type
        self.current_scope_type = ScopeType.MAIN
        
        # Get main's variables
        main_vars = set()
        for var in main.vars.variables:
            if var.name in main_vars:
                self.errors.add_error(SemanticError(
                    f"Name-rule violation: Duplicate variable '{var.name}' in main",
                    0, 0
                ))
            else:
                main_vars.add(var.name)
                # Add to symbol table
                self.symbol_table.add_symbol(
                    var.node_id, var.name, SymbolType.VARIABLE,
                    ScopeType.MAIN, var.node_id
                )
        
        # Analyze algorithm (main has no parameters, no local vars beyond its own declarations)
        self._analyze_algo(main.algo, set(), main_vars, main.node_id)
        
        # Restore context
        self.current_scope_type = old_scope
    
    def _analyze_algo(self, algo: AlgoNode, param_names: Set[str], 
                     local_vars: Set[str], parent_id: int):
        """Analyze an algorithm (sequence of instructions)"""
        for instr in algo.instrs:
            self._analyze_instruction(instr, param_names, local_vars, parent_id)
    
    def _analyze_instruction(self, instr: InstrNode, param_names: Set[str],
                            local_vars: Set[str], parent_id: int):
        """Analyze a single instruction"""
        if instr.kind == 'assign':
            self._analyze_assignment(instr.value, param_names, local_vars, parent_id)
        elif instr.kind == 'call':
            self._analyze_call(instr.value, param_names, local_vars, parent_id)
        elif instr.kind == 'print':
            self._analyze_output(instr.value, param_names, local_vars, parent_id)
        elif instr.kind == 'loop':
            self._analyze_loop(instr.value, param_names, local_vars, parent_id)
        elif instr.kind == 'branch':
            self._analyze_branch(instr.value, param_names, local_vars, parent_id)
        # 'halt' has no variables to check
    
    def _analyze_assignment(self, assign: AssignNode, param_names: Set[str],
                           local_vars: Set[str], parent_id: int):
        """Analyze an assignment instruction"""
        # Check if the variable on the left is declared
        self._check_variable_declared(assign.var, param_names, local_vars, parent_id)
        
        # Analyze the right side (could be a term or a call)
        if isinstance(assign.expr, CallNode):
            self._analyze_call(assign.expr, param_names, local_vars, parent_id)
        elif isinstance(assign.expr, TermNode):
            self._analyze_term(assign.expr, param_names, local_vars, parent_id)
    
    def _analyze_call(self, call: CallNode, param_names: Set[str],
                     local_vars: Set[str], parent_id: int):
        """Analyze a procedure/function call"""
        # Analyze arguments
        for arg in call.args.args:
            self._analyze_atom(arg, param_names, local_vars, parent_id)
    
    def _analyze_output(self, output: OutputNode, param_names: Set[str],
                       local_vars: Set[str], parent_id: int):
        """Analyze a print statement"""
        if output.kind == 'atom':
            self._analyze_atom(output.value, param_names, local_vars, parent_id)
        # String literals don't need checking
    
    def _analyze_loop(self, loop, param_names: Set[str],
                     local_vars: Set[str], parent_id: int):
        """Analyze a loop"""
        # Analyze condition
        self._analyze_term(loop.cond, param_names, local_vars, parent_id)
        # Analyze body
        self._analyze_algo(loop.body, param_names, local_vars, parent_id)
    
    def _analyze_branch(self, branch, param_names: Set[str],
                       local_vars: Set[str], parent_id: int):
        """Analyze a branch (if-else)"""
        # Analyze condition
        self._analyze_term(branch.cond, param_names, local_vars, parent_id)
        # Analyze then body
        self._analyze_algo(branch.then_body, param_names, local_vars, parent_id)
        # Analyze else body if present
        if branch.else_body:
            self._analyze_algo(branch.else_body, param_names, local_vars, parent_id)
    
    def _analyze_term(self, term: TermNode, param_names: Set[str],
                     local_vars: Set[str], parent_id: int):
        """Analyze a term (expression)"""
        if term.kind == 'atom':
            self._analyze_atom(term.value, param_names, local_vars, parent_id)
        elif term.kind == 'unop':
            op, operand = term.value
            self._analyze_term(operand, param_names, local_vars, parent_id)
        elif term.kind == 'binop':
            op, left, right = term.value
            self._analyze_term(left, param_names, local_vars, parent_id)
            self._analyze_term(right, param_names, local_vars, parent_id)
    
    def _analyze_atom(self, atom: AtomNode, param_names: Set[str],
                     local_vars: Set[str], parent_id: int):
        """Analyze an atom (variable or number)"""
        if atom.kind == 'var':
            self._check_variable_declared(atom.value, param_names, local_vars, parent_id)
        # Numbers don't need checking
    
    def _check_variable_declared(self, var_name: str, param_names: Set[str],
                                 local_vars: Set[str], parent_id: int):
        """
        Check if a variable is declared following the resolution order:
        1. Parameters (if in procedure/function)
        2. Local variables (if in procedure/function)
        3. Main variables (if in main)
        4. Global variables
        """
        if self.current_scope_type == ScopeType.LOCAL:
            # In a procedure or function
            # Check parameter -> local -> global
            if var_name in param_names:
                # Variable is a parameter - OK
                return
            elif var_name in local_vars:
                # Variable is a local variable - OK
                return
            elif self._is_global_variable(var_name):
                # Variable is global - OK
                return
            else:
                # Undeclared variable
                self.errors.add_error(SemanticError(
                    f"Undeclared variable '{var_name}' used in local scope",
                    0, 0
                ))
        
        elif self.current_scope_type == ScopeType.MAIN:
            # In main
            # Check main's variables -> global
            if var_name in local_vars:  # local_vars contains main's variables in this context
                # Variable is declared in main - OK
                return
            elif self._is_global_variable(var_name):
                # Variable is global - OK
                return
            else:
                # Undeclared variable
                self.errors.add_error(SemanticError(
                    f"Undeclared variable '{var_name}' used in main",
                    0, 0
                ))
    
    def _is_global_variable(self, var_name: str) -> bool:
        """Check if a variable is declared in global scope"""
        global_vars = self.symbol_table.get_symbols_in_scope(ScopeType.GLOBAL)
        return any(var.name == var_name for var in global_vars)
    
    def has_errors(self) -> bool:
        """Check if any semantic errors were found"""
        return self.errors.has_errors()
    
    def print_errors(self):
        """Print all semantic errors"""
        if self.errors.has_errors():
            print("\n=== Semantic Errors ===")
            self.errors.print_errors()
        else:
            print("\n✅ No semantic errors found!")
    
    def get_error_count(self) -> int:
        """Get the number of semantic errors"""
        return len(self.errors.errors)


def analyze_semantics(ast: ProgramNode) -> tuple[SymbolTable, ErrorReporter]:
    """
    Convenience function to perform semantic analysis.
    Returns (symbol_table, error_reporter)
    """
    analyzer = SemanticAnalyzer()
    symbol_table = analyzer.analyze(ast)
    return symbol_table, analyzer.errors

