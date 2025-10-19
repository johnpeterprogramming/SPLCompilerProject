from typing import List, Optional, LiteralString, cast
from spl_types import SemanticError
from spl_utils import ErrorReporter
from symbol_table import SymbolTable, ScopeType, SymbolType
from parser import (
    ProgramNode, ProcDefListNode, ProcDefNode, FuncDefListNode, FuncDefNode,
    MainNode, ParamNode, BodyNode, AlgoNode, InstrNode, AssignNode, CallNode,
    OutputNode, InputNode, TermNode, AtomNode, LoopNode, BranchNode, VariableNode
)
from enum import Enum


class DataType(Enum):
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    COMPARISON = "comparison"
    TYPELESS = "typeless"


class TypeChecker:
    def __init__(self, symbol_table: SymbolTable, ast_root: ProgramNode, error_reporter: ErrorReporter):
        self.symbol_table = symbol_table
        self.ast_root = ast_root
        self.errors = error_reporter

        # scope tracking for potential lookups (variables are numeric by fact)
        self.current_scope: ScopeType = ScopeType.GLOBAL
        self.current_parent_scope_id: Optional[int] = None

    def type_error(self, message: LiteralString, node_id: int = 0):
        self.errors.add_error(SemanticError("Type error: " + message, node_id, 0))

    def check_program(self):
        self.check_proc_defs(self.ast_root.procs)
        self.check_func_defs(self.ast_root.funcs)
        self.check_main(self.ast_root.main)

    def check_proc_defs(self, proc_defs: ProcDefListNode):
        for proc in proc_defs.procs:
            self.check_pdef(proc)

    def check_func_defs(self, func_defs: FuncDefListNode):
        for f in func_defs.funcs:
            self.check_fdef(f)

    def check_main(self, main: MainNode):
        old = self.current_scope
        self.current_scope = ScopeType.MAIN
        self.check_algo(main.algo)
        self.current_scope = old

    def check_pdef(self, pdef_node: ProcDefNode):
        if not self.is_typeless_name(pdef_node.name, SymbolType.PROCEDURE):
            self.type_error(f"Procedure '{pdef_node.name}' must be type-less", pdef_node.node_id)

        old_scope, old_parent = self.current_scope, self.current_parent_scope_id
        self.current_scope, self.current_parent_scope_id = ScopeType.LOCAL, pdef_node.node_id
        self.check_params(pdef_node.params)
        self.check_body(pdef_node.body)
        self.current_scope, self.current_parent_scope_id = old_scope, old_parent

    def check_fdef(self, fdef_node: FuncDefNode):
        if not self.is_typeless_name(fdef_node.name, SymbolType.FUNCTION):
            self.type_error(f"Function '{fdef_node.name}' must be type-less", fdef_node.node_id)

        old_scope, old_parent = self.current_scope, self.current_parent_scope_id
        self.current_scope, self.current_parent_scope_id = ScopeType.LOCAL, fdef_node.node_id
        self.check_params(fdef_node.params)
        self.check_body(fdef_node.body)
        if fdef_node.return_atom:
            ret_ty = self.check_atom(fdef_node.return_atom)
            if ret_ty != DataType.NUMERIC:
                self.type_error("function return must be numeric", fdef_node.return_atom.node_id)
        self.current_scope, self.current_parent_scope_id = old_scope, old_parent

    def check_params(self, param_node: ParamNode):
        # Ensure params exist in symbol table; all numeric by fact
        for v in param_node.params:
            if self.symbol_table.lookup(v.node_id) is None:
                self.type_error(f"Parameter '{v.name}' missing from symbol table", v.node_id)

    def check_body(self, body_node: BodyNode):
        for v in body_node.locals.params:
            if self.symbol_table.lookup(v.node_id) is None:
                self.type_error(f"Local '{v.name}' missing from symbol table", v.node_id)
        self.check_algo(body_node.algo)

    def check_algo(self, algo_node: AlgoNode):
        for instr in algo_node.instrs:
            self.check_instruction(instr)

    def check_instruction(self, instruction: InstrNode):
        if instruction.kind == 'halt':
            return
        if instruction.kind == 'print':
            assert isinstance(instruction.value, OutputNode)
            self.check_output(instruction.value)
            return
        if instruction.kind == 'call':
            assert isinstance(instruction.value, CallNode)
            if not self.is_typeless_name(instruction.value.name, SymbolType.PROCEDURE):
                self.type_error(f"'{instruction.value.name}' must be a procedure", instruction.node_id)
            self.check_input(instruction.value.args)
            return
        if instruction.kind == 'assign':
            assert isinstance(instruction.value, AssignNode)
            self.check_assign(instruction.value)
            return
        if instruction.kind == 'loop':
            assert isinstance(instruction.value, LoopNode)
            self.check_loop(instruction.value)
            return
        if instruction.kind == 'branch':
            assert isinstance(instruction.value, BranchNode)
            self.check_branch(instruction.value)
            return

    def check_assign(self, assign_node: AssignNode):
        if isinstance(assign_node.expr, CallNode):
            if not self.is_typeless_name(assign_node.expr.name, SymbolType.FUNCTION):
                self.type_error(f"'{assign_node.expr.name}' must be a function in assignment", assign_node.node_id)
            self.check_input(assign_node.expr.args)
        elif isinstance(assign_node.expr, TermNode):
            rhs_ty = self.check_term(assign_node.expr)
            if rhs_ty != DataType.NUMERIC:
                self.type_error("assignment RHS must be numeric", assign_node.node_id)

    def check_loop(self, loop_node: LoopNode):
        cond_ty = self.check_term(loop_node.cond)
        if cond_ty != DataType.BOOLEAN:
            self.type_error("loop condition must be boolean", loop_node.node_id)
        self.check_algo(loop_node.body)

    def check_branch(self, branch_node: BranchNode):
        cond_ty = self.check_term(branch_node.cond)
        if cond_ty != DataType.BOOLEAN:
            self.type_error("if condition must be boolean", branch_node.node_id)
        self.check_algo(branch_node.then_body)
        if branch_node.else_body:
            self.check_algo(branch_node.else_body)

    def check_output(self, output_node: OutputNode):
        if output_node.kind == 'string':
            return
        if output_node.kind == 'atom':
            ty = self.check_atom(output_node.value)
            if ty != DataType.NUMERIC:
                self.type_error("print atom must be numeric", output_node.value.node_id)

    def check_input(self, input_node: InputNode):
        for atom in input_node.args:
            if self.check_atom(atom) != DataType.NUMERIC:
                self.type_error("call arguments must be numeric", atom.node_id)

    def check_term(self, term_node: TermNode) -> Optional[DataType]:
        if term_node.kind == 'atom':
            return self.check_atom(term_node.value)
        if term_node.kind == 'unop':
            op, operand = term_node.value
            expected = self.get_unop_type(op)
            got = self.check_term(operand)
            if got != expected:
                self.type_error(f"unary '{cast(LiteralString, op)}' expects {expected.value}", term_node.node_id)
            return expected
        if term_node.kind == 'binop':
            op, left, right = term_node.value
            category = self.get_binop_category(op)
            lt = self.check_term(left)
            rt = self.check_term(right)
            if category == DataType.NUMERIC:
                if lt != DataType.NUMERIC or rt != DataType.NUMERIC:
                    self.type_error(f"arithmetic '{cast(LiteralString, op)}' expects numeric operands", term_node.node_id)
                return DataType.NUMERIC
            if category == DataType.BOOLEAN:
                if lt != DataType.BOOLEAN or rt != DataType.BOOLEAN:
                    self.type_error(f"logical '{cast(LiteralString, op)}' expects boolean operands", term_node.node_id)
                return DataType.BOOLEAN
            # comparison: operands numeric, result boolean
            if lt != DataType.NUMERIC or rt != DataType.NUMERIC:
                self.type_error(f"comparison '{cast(LiteralString, op)}' expects numeric operands", term_node.node_id)
            return DataType.BOOLEAN
        return None

    def check_atom(self, atom_node: AtomNode) -> Optional[DataType]:
        if atom_node.kind == 'number':
            return DataType.NUMERIC
        if atom_node.kind == 'var':
            # variables are numeric by fact
            return DataType.NUMERIC
        return None

    def get_unop_type(self, unop: str) -> DataType:
        if unop == 'neg':
            return DataType.NUMERIC
        if unop == 'not':
            return DataType.BOOLEAN
        return DataType.NUMERIC

    def get_binop_category(self, binop: str) -> DataType:
        # token lexemes from lexer via parser.match(...).value
        if binop in ('plus', 'minus', 'mult', 'div'):
            return DataType.NUMERIC
        if binop in ('and', 'or'):
            return DataType.BOOLEAN
        if binop in ('eq', '>', 'gt'):
            return DataType.COMPARISON
        return DataType.NUMERIC

    def is_typeless_name(self, name: str, expected_kind: SymbolType) -> bool:
        entries = self.symbol_table.lookup_by_name(name)
        for e in entries:
            # Procedures/functions must be typeless: data_type is None in symbol table
            if e.symbol_type == expected_kind and getattr(e, "data_type", None) is None:
                return True
        return False

        

