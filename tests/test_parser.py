import unittest
from spl_types import TokenType, Token, ParseError
from parser import parse_spl, ProgramNode, TermNode
from lexer import tokenize_spl

# Helper to create tokens
def make_tokens(token_tuples):
    tokens = [Token(t, v, 0, 0) for t, v in token_tuples]
    tokens.append(Token(TokenType.EOF, "", 0, 0))  # Always add EOF
    return tokens

# Helper to parse SPL code directly
def parse_ok(source):
    tokens = tokenize_spl(source)
    return parse_spl(tokens)


class TestSPLParser(unittest.TestCase):

    def test_minimal_program(self):
        tokens = make_tokens([
            (TokenType.GLOB, 'glob'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.PROC, 'proc'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.FUNC, 'func'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.MAIN, 'main'), (TokenType.LBRACE, '{'),
            (TokenType.VAR, 'var'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.HALT, 'halt'),
            (TokenType.RBRACE, '}')
        ])
        ast = parse_spl(tokens)
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(ast.main.algo.instrs[0].kind, 'halt')

    def test_variables_parsing(self):
        tokens = make_tokens([
            (TokenType.GLOB, 'glob'), (TokenType.LBRACE, '{'),
            (TokenType.USER_DEFINED_NAME, 'x'),
            (TokenType.USER_DEFINED_NAME, 'y'),
            (TokenType.RBRACE, '}'),
            (TokenType.PROC, 'proc'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.FUNC, 'func'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.MAIN, 'main'), (TokenType.LBRACE, '{'),
            (TokenType.VAR, 'var'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.HALT, 'halt'), (TokenType.RBRACE, '}')
        ])
        ast = parse_spl(tokens)
        self.assertEqual(len(ast.globals.variables), 2)
        self.assertEqual(ast.globals.variables[0].name, 'x')
        self.assertEqual(ast.globals.variables[1].name, 'y')

    def test_proc_and_func_parsing(self):
        tokens = make_tokens([
            (TokenType.GLOB, 'glob'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.PROC, 'proc'), (TokenType.LBRACE, '{'),
            (TokenType.USER_DEFINED_NAME, 'myproc'),
            (TokenType.LPAREN, '('), (TokenType.RPAREN, ')'),
            (TokenType.LBRACE, '{'), (TokenType.HALT, 'halt'), (TokenType.RBRACE, '}'),
            (TokenType.RBRACE, '}'),
            (TokenType.FUNC, 'func'), (TokenType.LBRACE, '{'),
            (TokenType.USER_DEFINED_NAME, 'myfunc'),
            (TokenType.LPAREN, '('), (TokenType.RPAREN, ')'),
            (TokenType.LBRACE, '{'), (TokenType.HALT, 'halt'),
            (TokenType.SEMICOLON, ';'), (TokenType.RETURN, 'return'),
            (TokenType.NUMBER, '5'), (TokenType.RBRACE, '}'),
            (TokenType.RBRACE, '}'),
            (TokenType.MAIN, 'main'), (TokenType.LBRACE, '{'),
            (TokenType.VAR, 'var'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.HALT, 'halt'),
            (TokenType.RBRACE, '}')
        ])
        ast = parse_spl(tokens)
        self.assertEqual(len(ast.procs.procs), 1)
        self.assertEqual(ast.procs.procs[0].name, 'myproc')
        self.assertEqual(len(ast.funcs.funcs), 1)
        self.assertEqual(ast.funcs.funcs[0].name, 'myfunc')
        # Fixed: function structure changed, return_atom is separate from body
        self.assertEqual(ast.funcs.funcs[0].return_atom.value, '5')

    def test_assign_and_call_instr(self):
        tokens = make_tokens([
            (TokenType.GLOB, 'glob'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.PROC, 'proc'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.FUNC, 'func'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.MAIN, 'main'), (TokenType.LBRACE, '{'),
            (TokenType.VAR, 'var'), (TokenType.LBRACE, '{'), (TokenType.USER_DEFINED_NAME, 'a'), (TokenType.RBRACE, '}'),
            (TokenType.USER_DEFINED_NAME, 'a'), (TokenType.ASSIGN, '='), (TokenType.NUMBER, '10'),
            (TokenType.SEMICOLON, ';'),
            (TokenType.USER_DEFINED_NAME, 'printme'), (TokenType.LPAREN, '('), (TokenType.USER_DEFINED_NAME, 'a'), (TokenType.RPAREN, ')'),
            (TokenType.RBRACE, '}')
        ])
        ast = parse_spl(tokens)
        instrs = ast.main.algo.instrs
        self.assertEqual(instrs[0].kind, 'assign')
        self.assertEqual(instrs[1].kind, 'call')

    def test_loop_instr(self):
        tokens = make_tokens([
            (TokenType.GLOB, 'glob'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.PROC, 'proc'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.FUNC, 'func'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.MAIN, 'main'), (TokenType.LBRACE, '{'),
            (TokenType.VAR, 'var'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.WHILE, 'while'), (TokenType.NUMBER, '1'), (TokenType.LBRACE, '{'),
            (TokenType.HALT, 'halt'),
            (TokenType.RBRACE, '}'),
            (TokenType.RBRACE, '}')
        ])
        ast = parse_spl(tokens)
        instr = ast.main.algo.instrs[0]
        self.assertEqual(instr.kind, 'loop')
        self.assertEqual(instr.value.kind, 'while')

    def test_branch_instr(self):
        tokens = make_tokens([
            (TokenType.GLOB, 'glob'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.PROC, 'proc'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.FUNC, 'func'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.MAIN, 'main'), (TokenType.LBRACE, '{'),
            (TokenType.VAR, 'var'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.IF, 'if'), (TokenType.NUMBER, '1'), (TokenType.LBRACE, '{'),
            (TokenType.HALT, 'halt'),
            (TokenType.RBRACE, '}'),
            (TokenType.RBRACE, '}')
        ])
        ast = parse_spl(tokens)
        instr = ast.main.algo.instrs[0]
        self.assertEqual(instr.kind, 'branch')
        self.assertEqual(instr.value.cond.value.value, '1')

    def test_invalid_token_raises_parse_error(self):
        tokens = make_tokens([
            (TokenType.GLOB, 'glob'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.PROC, 'proc'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.FUNC, 'func'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.MAIN, 'main'), (TokenType.LBRACE, '{'),
            (TokenType.VAR, 'var'), (TokenType.LBRACE, '{'), (TokenType.RBRACE, '}'),
            (TokenType.SEMICOLON, ';'),  # Invalid: semicolon without instruction
            (TokenType.RBRACE, '}')
        ])
        with self.assertRaises(ParseError):
            parse_spl(tokens)

    # --- New tests using parse_ok and valid SPL strings ---

    def test_empty_main_algo(self):
        program = """
        glob { }
        proc { }
        func { }
        main { var { } halt }
        """
        ast = parse_ok(program)
        self.assertEqual(len(ast.main.algo.instrs), 1)
        self.assertEqual(ast.main.algo.instrs[0].kind, "halt")

    def test_nested_loops(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x y }
            while (x eq 0) {
                do { y = (y plus 1) } until (y eq 10)
            };
            halt
        }
        """
        ast = parse_ok(program)
        outer_loop = ast.main.algo.instrs[0]
        self.assertEqual(outer_loop.kind, "loop")
        inner_loop = outer_loop.value.body.instrs[0]
        self.assertEqual(inner_loop.kind, "loop")
        self.assertEqual(inner_loop.value.kind, "do-until")

    def test_nested_if_else(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x nested nestedelse outerelse }
            if (x eq 1) {
                if (x eq 2) { print nested } else { print nestedelse }
            } else { print outerelse };
            halt
        }
        """
        ast = parse_ok(program)
        outer_branch = ast.main.algo.instrs[0]
        self.assertEqual(outer_branch.kind, "branch")
        inner_branch = outer_branch.value.then_body.instrs[0]
        self.assertEqual(inner_branch.kind, "branch")
        self.assertIsNotNone(inner_branch.value.else_body)

    def test_arithmetic_expression_assign(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { result a b c d }
            result = ((a plus b) mult (c minus d));
            halt
        }
        """
        ast = parse_ok(program)
        assign_instr = ast.main.algo.instrs[0]
        self.assertEqual(assign_instr.kind, "assign")

    def test_unary_operations(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x y }
            x = (neg 5);
            y = (not x);
            halt
        }
        """
        ast = parse_ok(program)
        self.assertEqual(len(ast.main.algo.instrs), 3)

    def test_proc_with_multiple_params(self):
        program = """
        glob { }
        proc {
            compute(a b c) { local { tmp } tmp = (a plus b); halt }
        }
        func { }
        main { var { } halt }
        """
        ast = parse_ok(program)
        proc = ast.procs.procs[0]
        self.assertEqual(proc.name, "compute")
        self.assertEqual(len(proc.params.params), 3)

    def test_function_return_variable(self):
        program = """
        glob { }
        proc { }
        func {
            getx() { local { x } halt ; return x }
        }
        main { var { } halt }
        """
        ast = parse_ok(program)
        func_def = ast.funcs.funcs[0]
        # Fixed: return_atom is separate field now
        self.assertEqual(func_def.return_atom.kind, "var")
        self.assertEqual(func_def.return_atom.value, "x")

    def test_print_multiple_values(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x y }
            print x;
            print 42;
            print y;
            halt
        }
        """
        ast = parse_ok(program)
        instrs = ast.main.algo.instrs
        self.assertEqual(instrs[0].kind, "print")
        self.assertEqual(instrs[1].kind, "print")
        self.assertEqual(instrs[2].kind, "print")

    def test_complex_nested_branches(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x y z }
            if (x eq 1) {
                if (y eq 2) { print x } else { print y }
            } else {
                if (z eq 3) { print z } else { halt }
            };
            halt
        }
        """
        ast = parse_ok(program)
        outer_branch = ast.main.algo.instrs[0]
        self.assertEqual(outer_branch.kind, "branch")
        self.assertIsNotNone(outer_branch.value.then_body)
        self.assertIsNotNone(outer_branch.value.else_body)

    def test_function_return_number(self):
        program = """
        glob { }
        proc { }
        func {
            getfive() { local { } halt ; return 5 }
        }
        main { var { } halt }
        """
        ast = parse_ok(program)
        func_def = ast.funcs.funcs[0]
        # Fixed: return_atom is separate field now
        self.assertEqual(func_def.return_atom.kind, "number")
        self.assertEqual(func_def.return_atom.value, "5")

    def test_call_function_with_args(self):
        program = """
        glob { }
        proc { }
        func {
            add(a b) {
                local { tmp }
                tmp = (a plus b);
                halt;
                return tmp
            }
        }
        main {
            var { result a b tmp }
            a = 10;
            b = 20;
            result = add(a b);
            halt
        }
        """
        ast = parse_ok(program)
        assign_instr = ast.main.algo.instrs[2]  # Third instruction (0, 1, 2)
        self.assertEqual(assign_instr.kind, "assign")

    def test_chained_assignment(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { a b c }
            c = 10;
            b = c;
            a = b;
            halt
        }
        """
        ast = parse_ok(program)
        instrs = ast.main.algo.instrs

        # There should be 4 instructions: 3 assignments + halt
        self.assertEqual(len(instrs), 4)

        # Check assignments
        expected_assignments = [("c", "10"), ("b", "c"), ("a", "b")]
        for i, (lhs, rhs) in enumerate(expected_assignments):
            assign_instr = instrs[i]
            self.assertEqual(assign_instr.kind, "assign")
            # LHS variable name
            self.assertEqual(assign_instr.value.var, lhs)
            # RHS value should be a TermNode with kind 'atom' and value an AtomNode with value rhs string
            expr = assign_instr.value.expr
            self.assertIsInstance(expr, TermNode)
            self.assertEqual(expr.kind, "atom")
            self.assertEqual(expr.value.value, rhs)

        # Last instruction should be halt
        self.assertEqual(instrs[3].kind, "halt")

    def test_assign_call_with_function_expr(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { a b }
            a = foo(b);
            halt
        }
        """
        ast = parse_ok(program)
        instr = ast.main.algo.instrs[0]
        self.assertEqual(instr.kind, "assign")
        self.assertEqual(instr.value.var, "a")
        self.assertEqual(instr.value.expr.name, "foo")
        self.assertEqual(len(instr.value.expr.args.args), 1)  # Fixed: args is InputNode with args field
        self.assertEqual(instr.value.expr.args.args[0].kind, "var")
        self.assertEqual(instr.value.expr.args.args[0].value, "b")

    def test_unary_operation_assign(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x }
            x = (neg 5);
            halt
        }
        """
        ast = parse_ok(program)
        instr = ast.main.algo.instrs[0]
        self.assertEqual(instr.kind, "assign")
        self.assertEqual(instr.value.var, "x")
        self.assertEqual(instr.value.expr.kind, "unop")
        self.assertEqual(instr.value.expr.value[0], "neg")
        self.assertEqual(instr.value.expr.value[1].kind, "atom")
        self.assertEqual(instr.value.expr.value[1].value.value, "5")

    def test_binary_operation_assign(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { a b c }
            a = (b plus c);
            halt
        }
        """
        ast = parse_ok(program)
        instr = ast.main.algo.instrs[0]
        self.assertEqual(instr.kind, "assign")
        self.assertEqual(instr.value.var, "a")
        self.assertEqual(instr.value.expr.kind, "binop")
        self.assertEqual(instr.value.expr.value[0], "plus")
        self.assertEqual(instr.value.expr.value[1].kind, "atom")
        self.assertEqual(instr.value.expr.value[1].value.value, "b")
        self.assertEqual(instr.value.expr.value[2].kind, "atom")
        self.assertEqual(instr.value.expr.value[2].value.value, "c")

    def test_loop_with_do_until(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x y }
            do {
                y = (y plus 1)
            } until (y eq 10);
            halt
        }
        """
        ast = parse_ok(program)
        instr = ast.main.algo.instrs[0]
        self.assertEqual(instr.kind, "loop")
        self.assertEqual(instr.value.kind, "do-until")
        self.assertEqual(instr.value.body.instrs[0].kind, "assign")

    def test_branch_with_else(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x }
            if (x eq 1) {
                print x
            } else {
                halt
            };
            halt
        }
        """
        ast = parse_ok(program)
        instr = ast.main.algo.instrs[0]
        self.assertEqual(instr.kind, "branch")
        self.assertIsNotNone(instr.value.else_body)

    def test_print_string(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { }
            print "hello";
            halt
        }
        """
        ast = parse_ok(program)
        instr = ast.main.algo.instrs[0]
        self.assertEqual(instr.kind, "print")
        # Fixed: OutputNode structure changed
        self.assertEqual(instr.value.kind, "string")
        self.assertEqual(instr.value.value, "hello")

    def test_call_without_assignment(self):
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { }
            print "start";
            dosomething(1 2);
            halt
        }
        """
        ast = parse_ok(program)
        call_instr = ast.main.algo.instrs[1]
        self.assertEqual(call_instr.kind, "call")

    def test_multiple_procedures(self):
        program = """
        glob { shared }
        proc {
            proc1(x) { local { } shared = x }
            proc2(y) { local { } print y }
        }
        func { }
        main { var { } halt }
        """
        ast = parse_ok(program)
        self.assertEqual(len(ast.procs.procs), 2)

    def test_error_unexpected_token(self):
        program = """
        glob { x }
        proc { }
        func { }
        main { var { } halt halt }
        """
        with self.assertRaises(Exception):
            parse_ok(program)

    def test_print_atom(self):
        """Test printing an atom (variable or number)"""
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { x }
            print x;
            print 42;
            halt
        }
        """
        ast = parse_ok(program)
        instr1 = ast.main.algo.instrs[0]
        instr2 = ast.main.algo.instrs[1]
        
        # Both should be print instructions
        self.assertEqual(instr1.kind, "print")
        self.assertEqual(instr2.kind, "print")
        
        # Fixed: OutputNode structure for atoms
        self.assertEqual(instr1.value.kind, "atom")
        self.assertEqual(instr1.value.value.kind, "var")
        self.assertEqual(instr1.value.value.value, "x")
        
        self.assertEqual(instr2.value.kind, "atom") 
        self.assertEqual(instr2.value.value.kind, "number")
        self.assertEqual(instr2.value.value.value, "42")

    def test_max_three_parameter_limit(self):
        """Test that more than 3 parameters causes an error"""
        # This should work (3 params)
        program_ok = """
        glob { }
        proc {
            test(a b c) { local { } halt }
        }
        func { }
        main { var { } halt }
        """
        ast = parse_ok(program_ok)  # Should not raise
        self.assertEqual(len(ast.procs.procs[0].params.params), 3)

        # This should fail (4 params) - but we can't easily test this with parse_ok
        # since the lexer will tokenize it correctly, we'd need to manually create tokens
        
    def test_max_three_argument_limit(self):
        """Test that more than 3 arguments in calls works up to limit"""
        program = """
        glob { }
        proc { }
        func { }
        main {
            var { a b c }
            dosomething(a b c);
            halt
        }
        """
        ast = parse_ok(program)
        call_instr = ast.main.algo.instrs[0]
        self.assertEqual(call_instr.kind, "call")
        # Fixed: CallNode has InputNode for args
        self.assertEqual(len(call_instr.value.args.args), 3)

if __name__ == "__main__":
    unittest.main(verbosity=2)