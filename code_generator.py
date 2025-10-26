"""
SPL Code Generator
COS341 Semester Project 2025

Translates SPL AST to target code following the specification.
"""

from typing import Tuple, Optional
from spl_types import CodeGenError
from symbol_table import SymbolTable, SymbolType, ScopeType
from parser import (
    ProgramNode, MainNode, AlgoNode, InstrNode, AssignNode, CallNode,
    TermNode, AtomNode, OutputNode, BranchNode, LoopNode
)
import re


class CodeGenerator:
    """Code generator for SPL"""
    
    def __init__(self, symbol_table: SymbolTable, ast: ProgramNode):
        self.symbol_table = symbol_table
        self.ast = ast
        self.temp_counter = 0
        self.label_counter = 0

        # Function name -> FuncDefNode (for inlining)
        self.func_map = {f.name: f for f in getattr(ast.funcs, "funcs", [])}
        # Per-inlining renaming stack: [{original_name: unique_internal_name}]
        self.rename_stack: list[dict[str, str]] = []
        # Unique counter for inlined instances
        self.inline_counter = 0
    
    def new_temp(self) -> str:
        """Generate a new temporary variable name"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self, prefix: str = "L") -> str:
        """Generate a new label name"""
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"
    
    def lookup_variable(self, var_name: str) -> str:
        """
        Lookup a variable in the symbol table and return its internal name.
        Using the variable name as is.
        """
        # If we are inside an inlined function instance, apply renaming first
        for mapping in reversed(self.rename_stack):
            if var_name in mapping:
                return mapping[var_name]
        # Otherwise, confirm variable exists in some scope (for debug) and return its name
        entries = self.symbol_table.lookup_by_name(var_name)
        if entries:
            return var_name
        raise CodeGenError(f"Variable '{var_name}' not found in symbol table", 0, 0)
    
    def generate(self) -> str:
        """
        Main entry point for code generation.
        Returns the generated target code as a string.
        """
        # Only translate the main program's ALGO
        code = self.translate_main(self.ast.main)
        return code
    
    def translate_main(self, main: MainNode) -> str:
        """
        Translate the main program.
        Only translate the ALGO
        """
        return self.translate_algo(main.algo)
    
    def translate_algo(self, algo: AlgoNode) -> str:
        """
        Translate an algorithm (sequence of instructions).
        Returns generated code with instructions separated by newlines.
        """
        code_lines = []
        for instr in algo.instrs:
            instr_code = self.translate_instr(instr)
            if instr_code:
                code_lines.append(instr_code)
        return "\n".join(code_lines)
    
    def translate_instr(self, instr: InstrNode) -> str:
        """Translate a single instruction"""
        if instr.kind == 'halt':
            return self.translate_halt()
        elif instr.kind == 'print':
            return self.translate_print(instr.value)
        elif instr.kind == 'assign':
            return self.translate_assign(instr.value)
        elif instr.kind == 'call':
            # Procedure call (no return value)
            call_code, _ = self.translate_call(instr.value)
            return call_code
        elif instr.kind == 'branch':
            return self.translate_branch(instr.value)
        elif instr.kind == 'loop':
            return self.translate_loop(instr.value)
        else:
            raise CodeGenError(f"Unknown instruction type '{instr.kind}'", 0, 0)
    
    def translate_halt(self) -> str:
        """Translate halt instruction to STOP"""
        return "STOP"
    
    def translate_print(self, output: OutputNode) -> str:
        """
        Translate print statement.
        OUTPUT ::= string | ATOM
        """
        if output.kind == 'string':
            # Print string literal
            return f'PRINT "{output.value}"'
        elif output.kind == 'atom':
            # Print atom (number or variable)
            atom = output.value
            if atom.kind == 'number':
                return f"PRINT {atom.value}"
            elif atom.kind == 'var':
                internal_name = self.lookup_variable(atom.value)
                return f"PRINT {internal_name}"
        raise CodeGenError(f"Unknown output kind: {output.kind}", 0, 0)
    
    def translate_assign(self, assign: AssignNode) -> str:
        """
        Translate assignment: VAR = TERM or VAR = CALL
        """
        var_internal = self.lookup_variable(assign.var)
        
        if isinstance(assign.expr, CallNode):
            # Function call with return value
            call_code, result_temp = self.translate_call(assign.expr)
            # Inline function if available; otherwise error (assignment expects a function)
            if assign.expr.name in self.func_map:
                call_code, result_temp = self.inline_function(assign.expr)
            else:
                raise CodeGenError(f"'{assign.expr.name}' is not a function (cannot assign CALL)", 0, 0)
            code = call_code + "\n" + f"{var_internal} = {result_temp}"
            return code
        elif isinstance(assign.expr, TermNode):
            # Regular term assignment
            term_code, result_temp = self.translate_term(assign.expr)
            if term_code:
                code = term_code + "\n" + f"{var_internal} = {result_temp}"
            else:
                code = f"{var_internal} = {result_temp}"
            return code
        else:
            raise CodeGenError(f"Unknown assignment expression type", 0, 0)
    

    def inline_function(self, call: CallNode) -> Tuple[str, str]:
        """
        Inline a function call:
          - evaluate arguments,
          - assign them to fresh per-invocation parameter vars,
          - translate the function body with renamed params/locals,
          - evaluate the return atom and produce its temp.
        Returns (generated_code, result_temp).
        """
        func = self.func_map.get(call.name)
        if func is None:
            raise CodeGenError(f"Function '{call.name}' not found for inlining", 0, 0)

        # 1) Evaluate arguments to temps
        arg_eval_lines: list[str] = []
        arg_temps: list[str] = []
        for arg_atom in call.args.args:
            c, t = self.translate_atom(arg_atom)
            if c:
                arg_eval_lines.append(c)
            arg_temps.append(t)

        # 2) Build a fresh rename mapping for this inlined instance
        self.inline_counter += 1
        prefix = f"{func.name}_{self.inline_counter}"
        mapping: dict[str, str] = {}
        # Map parameters
        formal_params = list(func.params.params)
        for i, p in enumerate(formal_params):
            mapping[p.name] = f"{prefix}_{p.name}"
        # Map locals
        for loc in func.body.locals.params:
            mapping[loc.name] = f"{prefix}_{loc.name}"

        # 3) Assign evaluated args into the fresh parameter variables
        param_assign_lines: list[str] = []
        for i, p in enumerate(formal_params):
            src_temp = arg_temps[i] if i < len(arg_temps) else "0"
            param_assign_lines.append(f"{mapping[p.name]} = {src_temp}")

        # 4) Translate function body under this mapping
        self.rename_stack.append(mapping)
        try:
            body_code = self.translate_algo(func.body.algo)
            # 5) Evaluate the return atom under the same mapping
            ret_code, ret_temp = self.translate_atom(func.return_atom)
        finally:
            self.rename_stack.pop()

        # 6) Stitch code together
        parts: list[str] = []
        if arg_eval_lines:
            parts.append("\n".join(arg_eval_lines))
        if param_assign_lines:
            parts.append("\n".join(param_assign_lines))
        if body_code:
            parts.append(body_code)
        if ret_code:
            parts.append(ret_code)

        return ("\n".join(parts), ret_temp)

    def translate_call(self, call: CallNode) -> Tuple[str, str]:
        """
        Translate procedure/function call.
        Returns (generated_code, result_temp)
        Result temp holds the return value for functions.
        """
        # Translate arguments
        arg_code_lines = []
        arg_vars = []
        
        for arg_atom in call.args.args:
            arg_code, arg_var = self.translate_atom(arg_atom)
            if arg_code:
                arg_code_lines.append(arg_code)
            arg_vars.append(arg_var)
        
        # Generate CALL instruction
        args_str = " ".join(arg_vars)
        call_line = f"CALL {call.name} {args_str}" if args_str else f"CALL {call.name}"
        
        # Combine argument code with call
        if arg_code_lines:
            code = "\n".join(arg_code_lines) + "\n" + call_line
        else:
            code = call_line
        
        # Create a temp for the return value
        result_temp = self.new_temp()
        
        return (code, result_temp)
    
    def translate_term(self, term: TermNode) -> Tuple[str, str]:
        """
        Translate a term (expression).
        Returns (generated_code, result_temp)
        
        TERM ::= ATOM
              | ( UNOP TERM )
              | ( TERM BINOP TERM )
        """
        if term.kind == 'atom':
            return self.translate_atom(term.value)
        
        elif term.kind == 'unop':
            op, operand = term.value
            if op == 'neg':
                # Translate operand
                operand_code, operand_temp = self.translate_term(operand)
                # Generate negation
                result_temp = self.new_temp()
                neg_line = f"{result_temp} = - {operand_temp}"
                
                if operand_code:
                    code = operand_code + "\n" + neg_line
                else:
                    code = neg_line
                
                return (code, result_temp)
            else:
                raise CodeGenError(f"Unary operator '{op}' not implemented in Phase 1", 0, 0)
        
        elif term.kind == 'binop':
            op, left, right = term.value
            
            # Map SPL operators to target language operators
            op_map = {
                'plus': '+',
                'minus': '-',
                'mult': '*',
                'div': '/',
                'eq': '=',
                '>': '>'
            }
            
            if op in op_map:
                # Arithmetic and comparison operators
                target_op = op_map[op]
                
                left_code, left_temp = self.translate_term(left)
                right_code, right_temp = self.translate_term(right)
                
                result_temp = self.new_temp()
                op_line = f"{result_temp} = {left_temp} {target_op} {right_temp}"
                
                code_parts = []
                if left_code:
                    code_parts.append(left_code)
                if right_code:
                    code_parts.append(right_code)
                code_parts.append(op_line)
                
                code = "\n".join(code_parts)
                return (code, result_temp)
            
            elif op in ['and', 'or']:
                # Need to evaluate to 0 or 1
                label_true = self.new_label("LTrue")
                label_end = self.new_label("LEnd")
                result_temp = self.new_temp()
                
                if op == 'and':
                    # Evaluate AND
                    label_false = self.new_label("LFalse")
                    left_code, left_temp = self.translate_term(left)
                    right_code, right_temp = self.translate_term(right)
                    
                    code_parts = []
                    if left_code:
                        code_parts.append(left_code)
                    code_parts.append(f"IF {left_temp} = 0 THEN {label_false}")
                    if right_code:
                        code_parts.append(right_code)
                    code_parts.append(f"IF {right_temp} = 0 THEN {label_false}")
                    # Both true
                    code_parts.append(f"{result_temp} = 1")
                    code_parts.append(f"GOTO {label_end}")
                    code_parts.append(f"REM {label_false}")
                    code_parts.append(f"{result_temp} = 0")
                    code_parts.append(f"REM {label_end}")
                    
                    return ("\n".join(code_parts), result_temp)
                
                elif op == 'or':
                    # Evaluate OR
                    label_false = self.new_label("LFalse")
                    left_code, left_temp = self.translate_term(left)
                    right_code, right_temp = self.translate_term(right)
                    
                    code_parts = []
                    if left_code:
                        code_parts.append(left_code)
                    code_parts.append(f"IF {left_temp} = 1 THEN {label_true}")
                    if right_code:
                        code_parts.append(right_code)
                    code_parts.append(f"IF {right_temp} = 1 THEN {label_true}")
                    # Both false
                    code_parts.append(f"{result_temp} = 0")
                    code_parts.append(f"GOTO {label_end}")
                    code_parts.append(f"REM {label_true}")
                    code_parts.append(f"{result_temp} = 1")
                    code_parts.append(f"REM {label_end}")
                    
                    return ("\n".join(code_parts), result_temp)
            
            else:
                raise CodeGenError(f"Binary operator '{op}' not implemented", 0, 0)
        
        else:
            raise CodeGenError(f"Unknown term kind: {term.kind}", 0, 0)
    
    def translate_atom(self, atom: AtomNode) -> Tuple[str, str]:
        """
        Translate an atom (number or variable).
        Returns (generated_code, result_var)
        
        For atoms, we often don't need to generate code, just return the value/variable.
        However, following the textbook approach, we assign to a temp.
        """
        if atom.kind == 'number':
            # Generate: t = number
            temp = self.new_temp()
            code = f"{temp} = {atom.value}"
            return (code, temp)
        
        elif atom.kind == 'var':
            # Generate: t = internal_name
            internal_name = self.lookup_variable(atom.value)
            temp = self.new_temp()
            code = f"{temp} = {internal_name}"
            return (code, temp)
        
        else:
            raise CodeGenError(f"Unknown atom kind: {atom.kind}", 0, 0)
    
    # =====  Flow  Control and Boolean Operations =====
    
    def translate_branch(self, branch: BranchNode) -> str:
        """
        Translate branch (if-then-else or if-then).
        
        Spec for if-then-else:
            IF t1 op t2 THEN labelT
            <code_of_else_ALGO>
            GOTO labelExit
            REM labelT
            <code_of_then_ALGO>
            REM labelExit
            
        Spec for if-then:
            IF t1 op t2 THEN labelT
            GOTO labelExit
            REM labelT
            <code_of_then_ALGO>
            REM labelExit
        """
        label_t = self.new_label("LT")
        label_exit = self.new_label("LExit")
        
        # Check if condition has 'not' at top level - if so, swap branches
        cond_term = branch.cond
        swap_branches = False
        
        if cond_term.kind == 'unop':
            op, operand = cond_term.value
            if op == 'not':
                # Handle not by swapping branches
                swap_branches = True
                cond_term = operand
        
        # Translate condition to IF statement
        cond_code = self.translate_condition(cond_term, label_t)
        
        # Translate then and else bodies
        then_code = self.translate_algo(branch.then_body)
        else_code = self.translate_algo(branch.else_body) if branch.else_body else None
        
        # Swap if we found 'not'
        if swap_branches:
            then_code, else_code = else_code, then_code
        
        # Build the branch structure
        code_parts = [cond_code]
        
        if else_code:
            # if-then-else: else code comes first
            code_parts.append(else_code)
        
        code_parts.append(f"GOTO {label_exit}")
        code_parts.append(f"REM {label_t}")
        code_parts.append(then_code)
        code_parts.append(f"REM {label_exit}")
        
        return "\n".join(code_parts)
    
    def translate_loop(self, loop: LoopNode) -> str:
        """
        Translate loops (while or do-until).
        
        Spec for while:
            REM labelBegin
            IF t1 op t2 THEN labelBody
            GOTO labelExit
            REM labelBody
            <code_of_ALGO>
            GOTO labelBegin
            REM labelExit
            
        Spec for do-until:
            REM labelBegin
            <code_of_ALGO>
            IF t1 op t2 THEN labelExit
            GOTO labelBegin
            REM labelExit
        """
        label_begin = self.new_label("LBegin")

        if loop.kind == 'while':
            label_body = self.new_label("LBody")
            label_exit = self.new_label("LExit")
            
            # Translate condition
            cond_code = self.translate_condition(loop.cond, label_body)
            
            # Translate body
            body_code = self.translate_algo(loop.body)
            
            # Build while loop
            code_parts = [
                f"REM {label_begin}",
                cond_code,
                f"GOTO {label_exit}",
                f"REM {label_body}",
                body_code,
                f"GOTO {label_begin}",
                f"REM {label_exit}"
            ]
            
            return "\n".join(code_parts)
        
        elif loop.kind == 'do-until':
            # Translate body
            body_code = self.translate_algo(loop.body)

            label_exit = self.new_label("LExit")
            
            # Translate condition
            cond_code = self.translate_condition(loop.cond, label_exit)
            
            # Build do-until loop
            code_parts = [
                f"REM {label_begin}",
                body_code,
                cond_code,
                f"GOTO {label_begin}",
                f"REM {label_exit}"
            ]
            
            return "\n".join(code_parts)
        
        else:
            raise CodeGenError(f"Unknown loop kind: {loop.kind}", 0, 0)
    
    def translate_condition(self, term: TermNode, true_label: str) -> str:
        """
        Translate a condition for IF statements.
        Generates: IF t1 op t2 THEN true_label
        
        Handles comparison operators (eq, >) and boolean operators (and, or).
        """
        if term.kind == 'binop':
            op, left, right = term.value
            
            # Handle boolean operators specially
            if op == 'and':
                return self.translate_boolean_and(left, right, true_label)
            elif op == 'or':
                return self.translate_boolean_or(left, right, true_label)
            
            # Handle comparison operators
            elif op in ['eq', '>']:
                # Translate operands
                left_code, left_temp = self.translate_term(left)
                right_code, right_temp = self.translate_term(right)
                
                # Map operator
                target_op = '=' if op == 'eq' else '>'
                
                # Generate IF statement
                code_parts = []
                if left_code:
                    code_parts.append(left_code)
                if right_code:
                    code_parts.append(right_code)
                code_parts.append(f"IF {left_temp} {target_op} {right_temp} THEN {true_label}")
                
                return "\n".join(code_parts)
            else:
                raise CodeGenError(f"Operator '{op}' not valid in condition", 0, 0)
        
        else:
            # For non-binop terms, we need to check if it's true (non-zero)
            # Generate: IF term = 1 THEN true_label
            term_code, term_temp = self.translate_term(term)
            
            code_parts = []
            if term_code:
                code_parts.append(term_code)
            code_parts.append(f"IF {term_temp} = 1 THEN {true_label}")
            
            return "\n".join(code_parts)
    
    def translate_boolean_and(self, left: TermNode, right: TermNode, true_label: str) -> str:
        """
        Translate boolean AND using cascading technique.
        
        Both operands must be true for result to be true.
        Short-circuit: if left is false, skip right evaluation.
        
        Spec pattern:
            <eval left to t1>
            IF t1 = 0 THEN labelFalse
            <eval right to t2>
            IF t2 = 0 THEN labelFalse
            GOTO labelTrue
            REM labelFalse
            GOTO labelEnd
            REM labelTrue
            <true code>
            REM labelEnd
            
        For condition context, we simplify:
            <eval left>
            IF left = 0 THEN labelSkip
            <eval right>
            IF right = 0 THEN labelSkip
            GOTO true_label
            REM labelSkip
        """
        label_skip = self.new_label("LSkip")
        
        # Translate left operand
        left_code, left_temp = self.translate_term(left)
        
        # Translate right operand
        right_code, right_temp = self.translate_term(right)
        
        # Build cascading AND
        code_parts = []
        if left_code:
            code_parts.append(left_code)
        code_parts.append(f"IF {left_temp} = 0 THEN {label_skip}")
        if right_code:
            code_parts.append(right_code)
        code_parts.append(f"IF {right_temp} = 0 THEN {label_skip}")
        code_parts.append(f"GOTO {true_label}")
        code_parts.append(f"REM {label_skip}")
        
        return "\n".join(code_parts)
    
    def translate_boolean_or(self, left: TermNode, right: TermNode, true_label: str) -> str:
        """
        Translate boolean OR using cascading technique.
        
        At least one operand must be true for result to be true.
        Short-circuit: if left is true, skip right evaluation.
        
        Spec pattern:
            <eval left to t1>
            IF t1 = 1 THEN labelTrue
            <eval right to t2>
            IF t2 = 1 THEN labelTrue
            GOTO labelFalse
            REM labelTrue
            <true code>
            GOTO labelEnd
            REM labelFalse
            <false code>
            REM labelEnd
            
        For condition context, we simplify:
            <eval left>
            IF left = 1 THEN true_label
            <eval right>
            IF right = 1 THEN true_label
        """
        # Translate left operand
        left_code, left_temp = self.translate_term(left)
        
        # Translate right operand
        right_code, right_temp = self.translate_term(right)
        
        # Build cascading OR
        code_parts = []
        if left_code:
            code_parts.append(left_code)
        code_parts.append(f"IF {left_temp} = 1 THEN {true_label}")
        if right_code:
            code_parts.append(right_code)
        code_parts.append(f"IF {right_temp} = 1 THEN {true_label}")
        
        return "\n".join(code_parts)
    
    def write_output(self, filename: str, code: str):
        """Write generated code to a file"""
        with open(filename, 'w') as f:
            f.write(code)
            f.write("\n")  # Ensure file ends with newline

    def to_basic(self, intermediate: str, start: int = 10, step: int = 10) -> str:
        """
        Convert unnumbered intermediate code to numbered BASIC.
        - Numbers each non-empty line with start, start+step, ...
        - Inlines labels: replaces 'GOTO Lx'/'THEN Lx' with target line numbers
          where 'REM Lx' denotes the target label line.
        """
        # Normalize and collect non-empty lines
        raw_lines = [ln.rstrip() for ln in intermediate.splitlines() if ln.strip() != ""]
        if not raw_lines:
            return ""

        # Pass 1: assign line numbers and capture label positions
        line_no_for_index = {}
        label_to_line = {}
        label_re = re.compile(r"^\s*REM\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
        for i, line in enumerate(raw_lines):
            line_no = start + step * i
            line_no_for_index[i] = line_no
            m = label_re.match(line)
            if m:
                label_to_line[m.group(1)] = line_no

        # Pass 2: rewrite GOTOs and THENs to concrete numbers
        goto_re = re.compile(r"\bGOTO\s+([A-Za-z_][A-Za-z0-9_]*)\b")
        then_re = re.compile(r"\bTHEN\s+([A-Za-z_][A-Za-z0-9_]*)\b")

        numbered_lines: list[str] = []
        for i, line in enumerate(raw_lines):
            def _subst(m: re.Match) -> str:
                label = m.group(1)
                target = label_to_line.get(label)
                # If label unknown, leave as-is (helps debugging).
                return f"{m.group(0).split()[0]} {target}" if target is not None else m.group(0)

            line_rewritten = goto_re.sub(_subst, then_re.sub(_subst, line))
            numbered_lines.append(f"{line_no_for_index[i]} {line_rewritten}")

        return "\n".join(numbered_lines)


def generate_intermediate_code(symbol_table: SymbolTable, ast: ProgramNode, output_file: str = "output.txt") -> str:
    """
    Convenience function to generate code from AST.
    Returns the generated code and writes it to output_file.
    """
    generator = CodeGenerator(symbol_table, ast)
    code = generator.generate()
    generator.write_output(output_file, code)
    return code

def generate_basic_code(symbol_table: SymbolTable, ast: ProgramNode,
                        output_file: str = "output_basic.bas",
                        line_start: int = 10, line_step: int = 10) -> str:
    """
    Generate final BASIC code:
      1) Produce intermediate code from main ALGO
      2) Number lines and inline labels into GOTO/THEN targets
    """
    gen = CodeGenerator(symbol_table, ast)
    intermediate = gen.generate()
    basic = gen.to_basic(intermediate, start=line_start, step=line_step)
    gen.write_output(output_file, basic)
    return basic
