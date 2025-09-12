from spl_types import TokenType, LexerError, Token
from spl_utils import ErrorReporter

# === AST Node Classes ===
class ASTNode:
	pass

class ProgramNode(ASTNode):
	def __init__(self, globals_, procs, funcs, main):
		self.globals = globals_
		self.procs = procs
		self.funcs = funcs
		self.main = main

class VariableListNode(ASTNode):
	def __init__(self, variables):
		self.variables = variables  # list of VariableNode

class VariableNode(ASTNode):
	def __init__(self, name):
		self.name = name

class ProcDefListNode(ASTNode):
	def __init__(self, procs):
		self.procs = procs  # list of ProcDefNode

class ProcDefNode(ASTNode):
	def __init__(self, name, params, body):
		self.name = name
		self.params = params
		self.body = body

class FuncDefListNode(ASTNode):
	def __init__(self, funcs):
		self.funcs = funcs  # list of FuncDefNode

class FuncDefNode(ASTNode):
	def __init__(self, name, params, body, ret):
		self.name = name
		self.params = params
		self.body = body
		self.ret = ret

class BodyNode(ASTNode):
	def __init__(self, locals_, algo):
		self.locals = locals_  # VariableListNode
		self.algo = algo  # AlgoNode

class ParamNode(ASTNode):
	def __init__(self, params):
		self.params = params  # list of VariableNode

class MainNode(ASTNode):
	def __init__(self, vars_, algo):
		self.vars = vars_  # VariableListNode
		self.algo = algo  # AlgoNode

class AlgoNode(ASTNode):
	def __init__(self, instrs):
		self.instrs = instrs  # list of InstrNode

class InstrNode(ASTNode):
	def __init__(self, kind, value):
		self.kind = kind  # e.g., 'halt', 'print', 'call', 'assign', 'loop', 'branch'
		self.value = value

class AssignNode(ASTNode):
	def __init__(self, var, expr):
		self.var = var
		self.expr = expr

class CallNode(ASTNode):
	def __init__(self, name, args):
		self.name = name
		self.args = args  # list of AtomNode

class LoopNode(ASTNode):
	def __init__(self, kind, cond, body, until_cond=None):
		self.kind = kind  # 'while' or 'do-until'
		self.cond = cond
		self.body = body
		self.until_cond = until_cond

class BranchNode(ASTNode):
	def __init__(self, cond, then_body, else_body=None):
		self.cond = cond
		self.then_body = then_body
		self.else_body = else_body

class OutputNode(ASTNode):
	def __init__(self, value):
		self.value = value  # AtomNode or string

class InputNode(ASTNode):
	def __init__(self, args):
		self.args = args  # list of AtomNode

class AtomNode(ASTNode):
	def __init__(self, kind, value):
		self.kind = kind  # 'var', 'number', 'string'
		self.value = value

class TermNode(ASTNode):
	def __init__(self, kind, value):
		self.kind = kind  # 'atom', 'unop', 'binop'
		self.value = value

# === Parser Implementation ===
class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0
		self.current_token = self.tokens[self.pos]
		self.errors = ErrorReporter()

	def advance(self):
		if self.pos < len(self.tokens) - 1:
			self.pos += 1
			self.current_token = self.tokens[self.pos]

	def match(self, token_type):
		if self.current_token.type == token_type:
			val = self.current_token.value
			self.advance()
			return val
		else:
			self.errors.add_error(LexerError(f"Expected {token_type}, got {self.current_token.type}", self.current_token.line, self.current_token.column))
			raise LexerError(f"Expected {token_type}, got {self.current_token.type}", self.current_token.line, self.current_token.column)

	def peek(self, token_type):
		return self.current_token.type == token_type

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

	# VARIABLES ::= nothing | VAR VARIABLES | VAR
	def parse_variables(self):
		variables = []
		while self.peek(TokenType.USER_DEFINED_NAME):
			name = self.match(TokenType.USER_DEFINED_NAME)
			variables.append(VariableNode(name))
		return VariableListNode(variables)

	# PROCDEFS ::= nothing | PDEF PROCDEFS
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

	# FUNCDEFS ::= nothing | FDEF FUNCDEFS
	def parse_funcdefs(self):
		funcs = []
		while self.peek(TokenType.USER_DEFINED_NAME):
			funcs.append(self.parse_fdef())
		return FuncDefListNode(funcs)

	# FDEF ::= NAME ( PARAM ) { BODY } ; return ATOM }
	def parse_fdef(self):
		name = self.match(TokenType.USER_DEFINED_NAME)
		self.match(TokenType.LPAREN)
		params = self.parse_param()
		self.match(TokenType.RPAREN)
		self.match(TokenType.LBRACE)
		body = self.parse_body()
		self.match(TokenType.RBRACE)
		self.match(TokenType.SEMICOLON)
		self.match(TokenType.RETURN)
		ret = self.parse_atom()
		self.match(TokenType.RBRACE)
		return FuncDefNode(name, params, body, ret)

	# BODY ::= local { MAXTHREE } ALGO
	def parse_body(self):
		self.match(TokenType.LOCAL)
		self.match(TokenType.LBRACE)
		locals_ = self.parse_maxthree()
		self.match(TokenType.RBRACE)
		algo = self.parse_algo()
		return BodyNode(locals_, algo)

	# PARAM ::= MAXTHREE
	def parse_param(self):
		return self.parse_maxthree()

	# MAXTHREE ::= nothing | VAR | VAR VAR | VAR VAR VAR
	def parse_maxthree(self):
		params = []
		for _ in range(3):
			if self.peek(TokenType.USER_DEFINED_NAME):
				params.append(VariableNode(self.match(TokenType.USER_DEFINED_NAME)))
			else:
				break
		return ParamNode(params)

	# MAINPROG ::= var { VARIABLES } ALGO
	def parse_mainprog(self):
		self.match(TokenType.VAR)
		self.match(TokenType.LBRACE)
		vars_ = self.parse_variables()
		self.match(TokenType.RBRACE)
		algo = self.parse_algo()
		return MainNode(vars_, algo)

	# ALGO ::= INSTR | INSTR ; ALGO
	def parse_algo(self):
		instrs = []
		instrs.append(self.parse_instr())
		while self.peek(TokenType.SEMICOLON):
			self.match(TokenType.SEMICOLON)
			# Only parse another instruction if the next token is not RBRACE
			if self.peek(TokenType.RBRACE):
				break
			instrs.append(self.parse_instr())
		return AlgoNode(instrs)

	# INSTR ::= halt | print OUTPUT | NAME ( INPUT ) | ASSIGN | LOOP | BRANCH
	def parse_instr(self):
		if self.peek(TokenType.HALT):
			self.match(TokenType.HALT)
			return InstrNode('halt', None)
		elif self.peek(TokenType.PRINT):
			self.match(TokenType.PRINT)
			output = self.parse_output()
			return InstrNode('print', output)
		elif self.peek(TokenType.USER_DEFINED_NAME):
			# Could be call or assign
			name = self.match(TokenType.USER_DEFINED_NAME)
			if self.peek(TokenType.LPAREN):
				self.match(TokenType.LPAREN)
				args = self.parse_input()
				self.match(TokenType.RPAREN)
				return InstrNode('call', CallNode(name, args))
			elif self.peek(TokenType.ASSIGN):
				self.match(TokenType.ASSIGN)
				# Could be function call or term
				if self.peek(TokenType.USER_DEFINED_NAME) and self.tokens[self.pos+1].type == TokenType.LPAREN:
					fname = self.match(TokenType.USER_DEFINED_NAME)
					self.match(TokenType.LPAREN)
					args = self.parse_input()
					self.match(TokenType.RPAREN)
					return InstrNode('assign', AssignNode(name, CallNode(fname, args)))
				else:
					expr = self.parse_term()
					return InstrNode('assign', AssignNode(name, expr))
			else:
				raise LexerError("Expected '(' or '=' after identifier in instruction", self.current_token.line, self.current_token.column)
		elif self.peek(TokenType.WHILE) or self.peek(TokenType.DO):
			return InstrNode('loop', self.parse_loop())
		elif self.peek(TokenType.IF):
			return InstrNode('branch', self.parse_branch())
		else:
			raise LexerError(f"Unexpected token in instruction: {self.current_token.type}", self.current_token.line, self.current_token.column)

	# ASSIGN ::= VAR = NAME ( INPUT ) | VAR = TERM
	# (Handled in parse_instr)

	# LOOP ::= while TERM { ALGO } | do { ALGO } until TERM
	def parse_loop(self):
		if self.peek(TokenType.WHILE):
			self.match(TokenType.WHILE)
			cond = self.parse_term()
			self.match(TokenType.LBRACE)
			body = self.parse_algo()
			self.match(TokenType.RBRACE)
			return LoopNode('while', cond, body)
		elif self.peek(TokenType.DO):
			self.match(TokenType.DO)
			self.match(TokenType.LBRACE)
			body = self.parse_algo()
			self.match(TokenType.RBRACE)
			self.match(TokenType.UNTIL)
			cond = self.parse_term()
			return LoopNode('do-until', cond, body)
		else:
			raise LexerError("Expected 'while' or 'do' for loop", self.current_token.line, self.current_token.column)

	# BRANCH ::= if TERM { ALGO } | if TERM { ALGO } else { ALGO }
	def parse_branch(self):
		self.match(TokenType.IF)
		cond = self.parse_term()
		self.match(TokenType.LBRACE)
		then_body = self.parse_algo()
		self.match(TokenType.RBRACE)
		if self.peek(TokenType.ELSE):
			self.match(TokenType.ELSE)
			self.match(TokenType.LBRACE)
			else_body = self.parse_algo()
			self.match(TokenType.RBRACE)
			return BranchNode(cond, then_body, else_body)
		else:
			return BranchNode(cond, then_body)

	# OUTPUT ::= ATOM | string
	def parse_output(self):
		if self.peek(TokenType.STRING):
			val = self.match(TokenType.STRING)
			return OutputNode(AtomNode('string', val))
		else:
			atom = self.parse_atom()
			return OutputNode(atom)

	# INPUT ::= nothing | ATOM | ATOM ATOM | ATOM ATOM ATOM
	def parse_input(self):
		args = []
		for _ in range(3):
			if self.peek(TokenType.USER_DEFINED_NAME) or self.peek(TokenType.NUMBER):
				args.append(self.parse_atom())
			else:
				break
		return args

	# ATOM ::= VAR | number
	def parse_atom(self):
		if self.peek(TokenType.USER_DEFINED_NAME):
			return AtomNode('var', self.match(TokenType.USER_DEFINED_NAME))
		elif self.peek(TokenType.NUMBER):
			return AtomNode('number', self.match(TokenType.NUMBER))
		else:
			raise LexerError(f"Expected variable or number for atom, got {self.current_token.type}", self.current_token.line, self.current_token.column)

	# TERM ::= ATOM | ( UNOP TERM ) | ( TERM BINOP TERM )
	def parse_term(self):
		if self.peek(TokenType.USER_DEFINED_NAME) or self.peek(TokenType.NUMBER):
			return TermNode('atom', self.parse_atom())
		elif self.peek(TokenType.LPAREN):
			self.match(TokenType.LPAREN)
			if self.peek(TokenType.NEG) or self.peek(TokenType.NOT):
				op = self.parse_unop()
				term = self.parse_term()
				self.match(TokenType.RPAREN)
				return TermNode('unop', (op, term))
			else:
				left = self.parse_term()
				op = self.parse_binop()
				right = self.parse_term()
				self.match(TokenType.RPAREN)
				return TermNode('binop', (op, left, right))
		else:
			raise LexerError(f"Invalid term at {self.current_token.type}", self.current_token.line, self.current_token.column)

	# UNOP ::= neg | not
	def parse_unop(self):
		if self.peek(TokenType.NEG):
			return self.match(TokenType.NEG)
		elif self.peek(TokenType.NOT):
			return self.match(TokenType.NOT)
		else:
			raise LexerError(f"Expected unary operator, got {self.current_token.type}", self.current_token.line, self.current_token.column)

	# BINOP ::= eq | > | or | and | plus | minus | mult | div
	def parse_binop(self):
		binops = {TokenType.EQ, TokenType.GT, TokenType.OR, TokenType.AND, TokenType.PLUS, TokenType.MINUS, TokenType.MULT, TokenType.DIV}
		if self.current_token.type in binops:
			return self.match(self.current_token.type)
		else:
			raise LexerError(f"Expected binary operator, got {self.current_token.type}", self.current_token.line, self.current_token.column)

# Entry point for parser
def parse_spl(tokens):
	parser = Parser(tokens)
	return parser.parse()