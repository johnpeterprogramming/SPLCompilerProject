from spl_types import TokenType, Token, SPLError, ParseError
from spl_utils import ErrorReporter

# === AST Node Classes ===
# Global counter for unique node IDs
_node_id_counter = 0

def _get_next_node_id():
    """Generate unique node ID"""
    global _node_id_counter
    _node_id_counter += 1
    return _node_id_counter

class ASTNode:
    def __init__(self):
        self.node_id = _get_next_node_id()

class ProgramNode(ASTNode):
    def __init__(self, globals_, procs, funcs, main):
        super().__init__()
        self.globals = globals_
        self.procs = procs
        self.funcs = funcs
        self.main = main

class VariableListNode(ASTNode):
    def __init__(self, variables):
        super().__init__()
        self.variables = variables  # list of VariableNode

class VariableNode(ASTNode):
    def __init__(self, name, next_var=None):
        super().__init__()
        self.name = name
        self.next = next_var

class ProcDefListNode(ASTNode):
    def __init__(self, procs):
        super().__init__()
        self.procs = procs  # list of ProcDefNode

class ProcDefNode(ASTNode):
    def __init__(self, name, params, body):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body

class FuncDefListNode(ASTNode):
    def __init__(self, funcs):
        super().__init__()
        self.funcs = funcs  # list of FuncDefNode

class FuncDefNode(ASTNode):
    def __init__(self, name, params, body, return_atom):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body
        self.return_atom = return_atom

class BodyNode(ASTNode):
    def __init__(self, locals_, algo):
        super().__init__()
        self.locals = locals_
        self.algo = algo

class ParamNode(ASTNode):
    def __init__(self, params):
        super().__init__()
        self.params = params  # list of VariableNode

class MainNode(ASTNode):
    def __init__(self, vars_, algo):
        super().__init__()
        self.vars = vars_
        self.algo = algo

class AlgoNode(ASTNode):
    def __init__(self, instrs):
        super().__init__()
        self.instrs = instrs  # list of InstrNode

class InstrNode(ASTNode):
    def __init__(self, kind, value):
        super().__init__()
        self.kind = kind  # 'halt', 'print', 'call', 'assign', 'loop', 'branch'
        self.value = value

class AssignNode(ASTNode):
    def __init__(self, var, expr):
        super().__init__()
        self.var = var
        self.expr = expr

class CallNode(ASTNode):
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args

class LoopNode(ASTNode):
    def __init__(self, kind, cond, body):
        super().__init__()
        self.kind = kind  # 'while' or 'do-until'
        self.cond = cond
        self.body = body

class BranchNode(ASTNode):
    def __init__(self, cond, then_body, else_body=None):
        super().__init__()
        self.cond = cond
        self.then_body = then_body
        self.else_body = else_body

class OutputNode(ASTNode):
    def __init__(self, kind, value):
        super().__init__()
        self.kind = kind  # 'atom' or 'string'
        self.value = value

class InputNode(ASTNode):
    def __init__(self, args):
        super().__init__()
        self.args = args  # list of AtomNode (max 3)

class AtomNode(ASTNode):
    def __init__(self, kind, value):
        super().__init__()
        self.kind = kind  # 'var' or 'number'
        self.value = value

class TermNode(ASTNode):
    def __init__(self, kind, value):
        super().__init__()
        self.kind = kind  # 'atom', 'unop', or 'binop'
        self.value = value

# === Parser Implementation ===

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if tokens else None
        self.errors = ErrorReporter()

    # ---- token helpers ----
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]

    def match(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            val = self.current_token.value
            self.advance()
            return val
        else:
            token_name = self.current_token.type if self.current_token else "EOF"
            err = ParseError(
                f"Expected {token_type}, got {token_name}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err

    def peek(self, token_type):
        return self.current_token and self.current_token.type == token_type

    def peek_ahead(self, offset=1):
        """Safe peek ahead; returns TokenType or None."""
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx].type
        return None

    # ---- entry ----
    def parse(self):
        return self.parse_program()

    # SPL_PROG ::= glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }
    def parse_program(self):
        self.match(TokenType.GLOB)
        self.match(TokenType.LBRACE)
        globals_ = self.parse_variables()
        self.match(TokenType.RBRACE)

        self.match(TokenType.PROC)
        self.match(TokenType.LBRACE)
        procs = self.parse_procdefs()
        self.match(TokenType.RBRACE)

        self.match(TokenType.FUNC)
        self.match(TokenType.LBRACE)
        funcs = self.parse_funcdefs()
        self.match(TokenType.RBRACE)

        self.match(TokenType.MAIN)
        self.match(TokenType.LBRACE)
        main = self.parse_mainprog()
        self.match(TokenType.RBRACE)

        return ProgramNode(globals_, procs, funcs, main)

    # ---- variables / lists ----
    # VARIABLES ::= (empty) | VAR VARIABLES
    def parse_variables(self):
        variables = []
        while self.peek(TokenType.USER_DEFINED_NAME):
            name = self.match(TokenType.USER_DEFINED_NAME)
            variables.append(VariableNode(name))
        return VariableListNode(variables)

    # PROCDEFS ::= (empty) | PDEF PROCDEFS
    def parse_procdefs(self):
        procs = []
        while self.peek(TokenType.USER_DEFINED_NAME):
            procs.append(self.parse_pdef())
        return ProcDefListNode(procs)

    # PDEF ::= NAME ( PARAM ) { BODY }
    def parse_pdef(self):
        name = self.match(TokenType.USER_DEFINED_NAME)
        self.match(TokenType.LPAREN)
        params = self.parse_param()
        self.match(TokenType.RPAREN)
        self.match(TokenType.LBRACE)
        body = self.parse_body()
        self.match(TokenType.RBRACE)
        return ProcDefNode(name, params, body)

    # FUNCDEFS ::= (empty) | FDEF FUNCDEFS
    def parse_funcdefs(self):
        funcs = []
        while self.peek(TokenType.USER_DEFINED_NAME):
            funcs.append(self.parse_fdef())
        return FuncDefListNode(funcs)

    # FDEF ::= NAME ( PARAM ) { BODY ; return ATOM }
    def parse_fdef(self):
        name = self.match(TokenType.USER_DEFINED_NAME)
        self.match(TokenType.LPAREN)
        params = self.parse_param()
        self.match(TokenType.RPAREN)
        self.match(TokenType.LBRACE)
        body = self.parse_body()
        self.match(TokenType.SEMICOLON)
        self.match(TokenType.RETURN)
        return_atom = self.parse_atom()
        self.match(TokenType.RBRACE)
        return FuncDefNode(name, params, body, return_atom)

    # BODY ::= local { MAXTHREE } ALGO
    def parse_body(self):
        locals_ = ParamNode([])
        if self.peek(TokenType.LOCAL):
            self.match(TokenType.LOCAL)
            self.match(TokenType.LBRACE)
            locals_ = self.parse_maxthree()
            self.match(TokenType.RBRACE)
        algo = self.parse_algo()
        return BodyNode(locals_, algo)

    # PARAM ::= MAXTHREE
    def parse_param(self):
        return self.parse_maxthree()

    # MAXTHREE ::= (empty) | VAR | VAR VAR | VAR VAR VAR
    def parse_maxthree(self):
        params = []
        # Parse up to 3 variables, but validate exactly
        count = 0
        while self.peek(TokenType.USER_DEFINED_NAME) and count < 3:
            params.append(VariableNode(self.match(TokenType.USER_DEFINED_NAME)))
            count += 1
        
        # Validate we don't have more than 3 parameters
        if self.peek(TokenType.USER_DEFINED_NAME):
            err = ParseError(
                "Maximum of 3 parameters allowed",
                self.current_token.line,
                self.current_token.column,
            )
            self.errors.add_error(err)
            raise err
            
        return ParamNode(params)

    # MAINPROG ::= var { VARIABLES } ALGO
    def parse_mainprog(self):
        self.match(TokenType.VAR)
        self.match(TokenType.LBRACE)
        vars_ = self.parse_variables()
        self.match(TokenType.RBRACE)
        algo = self.parse_algo()
        return MainNode(vars_, algo)

    # ---- algorithm / instruction list ----
    # ALGO ::= INSTR | INSTR ; ALGO
    def parse_algo(self):
        instrs = []
        instrs.append(self.parse_instr())

        # Continue parsing instructions separated by semicolons
        while self.peek(TokenType.SEMICOLON):
            # Look ahead to see if this semicolon is followed by 'return'
            # If so, don't consume it - let the calling context handle it
            if self.peek_ahead(1) == TokenType.RETURN:
                break
            
            self.match(TokenType.SEMICOLON)
            
            # Check if we have a valid instruction following
            if (self.peek(TokenType.RBRACE) or 
                self.peek(TokenType.EOF) or 
                self.peek(TokenType.RETURN)):
                err = ParseError(
                    "Expected instruction after semicolon",
                    self.current_token.line if self.current_token else 0,
                    self.current_token.column if self.current_token else 0,
                )
                self.errors.add_error(err)
                raise err
            
            instrs.append(self.parse_instr())

        return AlgoNode(instrs)

    # ---- instructions ----
    def parse_instr(self):
        if self.peek(TokenType.HALT):
            self.match(TokenType.HALT)
            return InstrNode('halt', None)

        elif self.peek(TokenType.PRINT):
            self.match(TokenType.PRINT)
            output = self.parse_output()
            return InstrNode('print', output)

        elif self.peek(TokenType.USER_DEFINED_NAME):
            return self.parse_name_instruction()

        elif self.peek(TokenType.WHILE) or self.peek(TokenType.DO):
            return InstrNode('loop', self.parse_loop())

        elif self.peek(TokenType.IF):
            return InstrNode('branch', self.parse_branch())

        else:
            err = ParseError(
                f"Unexpected token in instruction: {self.current_token.type if self.current_token else 'EOF'}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err

    def parse_name_instruction(self):
        """Handle instructions starting with USER_DEFINED_NAME"""
        name = self.match(TokenType.USER_DEFINED_NAME)

        if self.peek(TokenType.LPAREN):
            # NAME ( INPUT ) - procedure call
            self.match(TokenType.LPAREN)
            args = self.parse_input()
            self.match(TokenType.RPAREN)
            return InstrNode('call', CallNode(name, args))

        elif self.peek(TokenType.ASSIGN):
            # VAR = ... - assignment
            self.match(TokenType.ASSIGN)
            
            if self.peek(TokenType.USER_DEFINED_NAME) and self.peek_ahead(1) == TokenType.LPAREN:
                # VAR = NAME ( INPUT ) - function call assignment
                fname = self.match(TokenType.USER_DEFINED_NAME)
                self.match(TokenType.LPAREN)
                args = self.parse_input()
                self.match(TokenType.RPAREN)
                return InstrNode('assign', AssignNode(name, CallNode(fname, args)))
            else:
                # VAR = TERM - term assignment
                expr = self.parse_term()
                return InstrNode('assign', AssignNode(name, expr))
        else:
            err = ParseError(
                "Expected '(' or '=' after identifier",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err

    # ---- loops / branches ----
    def parse_loop(self):
        if self.peek(TokenType.WHILE):
            # LOOP ::= while TERM { ALGO }
            self.match(TokenType.WHILE)
            cond = self.parse_term()
            self.match(TokenType.LBRACE)
            body = self.parse_algo()
            self.match(TokenType.RBRACE)
            return LoopNode('while', cond, body)
            
        elif self.peek(TokenType.DO):
            # LOOP ::= do { ALGO } until TERM
            self.match(TokenType.DO)
            self.match(TokenType.LBRACE)
            body = self.parse_algo()
            self.match(TokenType.RBRACE)
            self.match(TokenType.UNTIL)
            cond = self.parse_term()
            return LoopNode('do-until', cond, body)
        else:
            err = ParseError(
                "Expected 'while' or 'do' for loop",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err

    def parse_branch(self):
        # BRANCH ::= if TERM { ALGO } | if TERM { ALGO } else { ALGO }
        self.match(TokenType.IF)
        cond = self.parse_term()
        self.match(TokenType.LBRACE)
        then_body = self.parse_algo()
        self.match(TokenType.RBRACE)
        
        else_body = None
        if self.peek(TokenType.ELSE):
            self.match(TokenType.ELSE)
            self.match(TokenType.LBRACE)
            else_body = self.parse_algo()
            self.match(TokenType.RBRACE)
            
        return BranchNode(cond, then_body, else_body)

    # ---- I/O / atoms / terms ----
    # OUTPUT ::= ATOM | string
    def parse_output(self):
        if self.peek(TokenType.STRING):
            val = self.match(TokenType.STRING)
            # Validate string length (max 15 characters)
            if len(val) > 15:
                err = ParseError(
                    f"String literal exceeds maximum length of 15 characters: {len(val)}",
                    self.current_token.line if self.current_token else 0,
                    self.current_token.column if self.current_token else 0,
                )
                self.errors.add_error(err)
                raise err
            return OutputNode('string', val)
        else:
            atom = self.parse_atom()
            return OutputNode('atom', atom)

    # INPUT ::= (empty) | ATOM | ATOM ATOM | ATOM ATOM ATOM
    def parse_input(self):
        args = []
        count = 0
        
        # Parse up to 3 atoms
        while ((self.peek(TokenType.USER_DEFINED_NAME) or self.peek(TokenType.NUMBER)) 
               and count < 3):
            args.append(self.parse_atom())
            count += 1
        
        # Validate we don't have more than 3 arguments
        if (self.peek(TokenType.USER_DEFINED_NAME) or self.peek(TokenType.NUMBER)):
            err = ParseError(
                "Maximum of 3 arguments allowed",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err
            
        return InputNode(args)

    # ATOM ::= VAR | number
    def parse_atom(self):
        if self.peek(TokenType.USER_DEFINED_NAME):
            name = self.match(TokenType.USER_DEFINED_NAME)
            # Validate that the name is not a reserved keyword
            reserved_keywords = {
                'glob', 'proc', 'func', 'main', 'var', 'local', 'halt', 'print', 
                'return', 'while', 'do', 'until', 'if', 'else', 'neg', 'not', 
                'eq', 'or', 'and', 'plus', 'minus', 'mult', 'div'
            }
            if name in reserved_keywords:
                err = ParseError(
                    f"User-defined name cannot be a reserved keyword: {name}",
                    self.current_token.line if self.current_token else 0,
                    self.current_token.column if self.current_token else 0,
                )
                self.errors.add_error(err)
                raise err
            return AtomNode('var', name)
            
        elif self.peek(TokenType.NUMBER):
            return AtomNode('number', self.match(TokenType.NUMBER))
        else:
            err = ParseError(
                f"Expected variable or number for atom, got {self.current_token.type if self.current_token else 'EOF'}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err

    # TERM ::= ATOM | ( UNOP TERM ) | ( TERM BINOP TERM )
    def parse_term(self):
        if self.peek(TokenType.USER_DEFINED_NAME) or self.peek(TokenType.NUMBER):
            # TERM ::= ATOM
            return TermNode('atom', self.parse_atom())
            
        elif self.peek(TokenType.LPAREN):
            self.match(TokenType.LPAREN)
            
            if self.peek(TokenType.NEG) or self.peek(TokenType.NOT):
                # TERM ::= ( UNOP TERM )
                op = self.parse_unop()
                operand = self.parse_term()
                self.match(TokenType.RPAREN)
                return TermNode('unop', (op, operand))
            else:
                # TERM ::= ( TERM BINOP TERM )
                left = self.parse_term()
                op = self.parse_binop()
                right = self.parse_term()
                self.match(TokenType.RPAREN)
                return TermNode('binop', (op, left, right))
        else:
            err = ParseError(
                f"Invalid term, expected atom or parenthesized expression, got {self.current_token.type if self.current_token else 'EOF'}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err

    def parse_unop(self):
        if self.peek(TokenType.NEG):
            return self.match(TokenType.NEG)
        elif self.peek(TokenType.NOT):
            return self.match(TokenType.NOT)
        else:
            err = ParseError(
                f"Expected unary operator, got {self.current_token.type if self.current_token else 'EOF'}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err

    def parse_binop(self):
        binops = {
            TokenType.EQ, TokenType.GT, TokenType.OR, TokenType.AND,
            TokenType.PLUS, TokenType.MINUS, TokenType.MULT, TokenType.DIV,
        }
        if self.current_token and self.current_token.type in binops:
            return self.match(self.current_token.type)
        else:
            err = ParseError(
                f"Expected binary operator, got {self.current_token.type if self.current_token else 'EOF'}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0,
            )
            self.errors.add_error(err)
            raise err


# Entry point
def parse_spl(tokens):
    """Parse SPL tokens into an AST"""
    if not tokens:
        raise ParseError("No tokens to parse", 0, 0)
    
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        
        # Check if we have any remaining tokens (should only be EOF)
        if parser.current_token and parser.current_token.type != TokenType.EOF:
            err = ParseError(
                f"Unexpected tokens after end of program: {parser.current_token.type}",
                parser.current_token.line,
                parser.current_token.column,
            )
            parser.errors.add_error(err)
            raise err
            
        return ast
    except ParseError as e:
        # Re-raise with error reporter context
        if parser.errors.has_errors():
            parser.errors.print_errors()
        raise e