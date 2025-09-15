import pytest
from lexer import tokenize_spl
from parser import parse_spl
from spl_types import TokenType, LexerError

# Helper to parse code
def parse_ok(source):
    tokens = tokenize_spl(source)
    return parse_spl(tokens)


def test_global_variables():
    program = """
    glob { x y z }
    proc { }
    func { }
    main { var { } halt }
    """
    ast = parse_ok(program)
    assert len(ast.globals.variables) == 3
    assert ast.procs.procs == []
    assert ast.funcs.funcs == []


def test_proc_with_multiple_params_and_body():
    program = """
    glob { }
    proc {
        compute(x y z) { local { tmp } tmp = (x plus y); print tmp }
    }
    func { }
    main { var { } halt }
    """
    ast = parse_ok(program)
    assert len(ast.procs.procs) == 1
    proc = ast.procs.procs[0]
    assert proc.name == "compute"
    assert len(proc.params.params) == 3
    assert len(proc.body.algo.instrs) == 2


def test_while_loop():
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { x }
        while (x eq 0) { x = (x plus 1); print x };
        halt
    }
    """
    ast = parse_ok(program)
    loop_instr = ast.main.algo.instrs[0]
    assert loop_instr.kind == "loop"
    assert loop_instr.value.kind == "while"


def test_do_until_loop():
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { x }
        do { x = (x plus 1) } until (x eq 5);
        halt
    }
    """
    ast = parse_ok(program)
    loop_instr = ast.main.algo.instrs[0]
    assert loop_instr.kind == "loop"
    assert loop_instr.value.kind == "do-until"


def test_if_branch():
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { x }
        if (x eq 1) { print x };
        halt
    }
    """
    ast = parse_ok(program)
    branch_instr = ast.main.algo.instrs[0]
    assert branch_instr.kind == "branch"


def test_if_else_branch():
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { x }
        if (x eq 1) { print "yes" } else { print "no" };
        halt
    }
    """
    ast = parse_ok(program)
    branch_instr = ast.main.algo.instrs[0]
    assert branch_instr.value.else_body is not None


def test_variable_assignment():
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { x y }
        x = 1;
        y = (x plus 2);
        halt
    }
    """
    ast = parse_ok(program)
    assign_instr = ast.main.algo.instrs[0]
    assert assign_instr.kind == "assign"


def test_function_call_assignment():
    program = """
    glob { }
    proc { }
    func {
        add(a b) { local { sum } sum = (a plus b); halt ; return sum
    }
    main {
        var { x }
        x = add(2 3);
        halt
    }
    """
    ast = parse_ok(program)
    assign_instr = ast.main.algo.instrs[0]
    assert assign_instr.kind == "assign"
    assert assign_instr.value.expr.args[0].value == "2"


def test_call_without_assignment():
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
    assert call_instr.kind == "call"


def test_arithmetic_expression():
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { result }
        result = ((a plus b) mult (c minus d));
        halt
    }
    """
    ast = parse_ok(program)
    assign_instr = ast.main.algo.instrs[0]
    assert assign_instr.kind == "assign"


def test_unary_operations():
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { x y }
        x = neg 5;
        y = not x;
        halt
    }
    """
    ast = parse_ok(program)
    assert len(ast.main.algo.instrs) == 3


def test_string_print():
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { }
        print "helloworld";
        halt
    }
    """
    ast = parse_ok(program)
    print_instr = ast.main.algo.instrs[0]
    assert print_instr.kind == "print"


def test_multiple_procedures():
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
    assert len(ast.procs.procs) == 2


def test_minimal_program():
    program = """
    glob { }
    proc { }
    func { }
    main { var { } halt }
    """
    ast = parse_ok(program)
    assert ast.globals.variables == []
    assert ast.procs.procs == []
    assert ast.funcs.funcs == []
    assert ast.main.vars.variables == []


def test_error_invalid_syntax():
    program = """
    glob { x }
    proc { }
    func { }
    main { var { } x = ; halt }
    """
    with pytest.raises(Exception):
        parse_ok(program)


def test_error_unexpected_token():
    program = """
    glob { x }
    proc { }
    func { }
    main { var { } halt halt }
    """
    with pytest.raises(Exception):
        parse_ok(program)
