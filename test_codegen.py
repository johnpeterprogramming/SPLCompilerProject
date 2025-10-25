#!/usr/bin/env python3
"""
Test script for code generation phase 1
"""

from lexer import tokenize_spl
from parser import parse_spl
from semantic_analyzer import analyze_semantics
from code_generator import generate_intermediate_code, generate_basic_code
import re

def test_code_generation():
    """Test code generation with a simple program"""
    
    print("=== Code Generation Test ===\n")
    
    # Simple test program
    program = """
    glob {
        x
        y
        z
    }
    
    proc {
    }
    
    func {
    }
    
    main {
        var { a b }
        a = 10;
        b = ( a plus 5 );
        x = ( b mult 2 );
        y = ( neg x );
        print "Result";
        print x;
        halt
    }
    """
    
    print("Source Program:")
    print(program)
    print("\n" + "="*60 + "\n")
    
    try:
        # Tokenize
        tokens = tokenize_spl(program)
        print("✓ Lexical analysis completed")
        
        # Parse
        ast = parse_spl(tokens)
        print("✓ Parsing completed")
        
        # Semantic analysis
        symbol_table, semantic_errors = analyze_semantics(ast)
        if semantic_errors.has_errors():
            print("✗ Semantic errors found:")
            semantic_errors.print_errors()
            return
        print("✓ Semantic analysis completed")
        
        # Code generation
        output_file = "test_output.txt"
        generated_code = generate_intermediate_code(symbol_table, ast, output_file)
        print("✓ Code generation completed")
        
        print("\n" + "="*60)
        print("Generated Target Code:")
        print("="*60)
        print(generated_code)
        print("="*60)
        print(f"\n✓ Code written to: {output_file}")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_code_generation()
    
def test_basic_code_generation():
    """Test BASIC post-processing: numbering and label inlining (GOTO/THEN)."""
    program = """
    glob { }
    proc { }
    func { }
    main {
        var { a }
        a = 2;
        if ( a > 0 ) { a = ( a minus 1 ); halt } else { halt };
        while ( a > 0 ) { a = ( a minus 1 ); halt };
        print a;
        halt
    }
    """

    # Pipeline
    tokens = tokenize_spl(program)
    ast = parse_spl(tokens)
    symtab, sem_errors = analyze_semantics(ast)
    assert not sem_errors.has_errors(), f"Semantic errors: {[str(e) for e in sem_errors.errors]}"

    basic = generate_basic_code(symtab, ast, output_file="test_output_basic.bas", line_start=130, line_step=10)

    # Basic sanity: non-empty, numbered lines, increasing by step
    lines = [ln for ln in basic.splitlines() if ln.strip()]
    assert lines, "No BASIC lines generated"
    numbers = []
    for ln in lines:
        m = re.match(r"^(\d+) ", ln)
        assert m, f"Line not numbered: {ln}"
        numbers.append(int(m.group(1)))
    # strictly increasing and step is multiple of 10
    assert all(b > a for a, b in zip(numbers, numbers[1:])), "Line numbers are not increasing"
    assert all((b - a) == 10 for a, b in zip(numbers, numbers[1:])), "Line numbers not spaced by 10"

    # Collect numbered REM label lines
    label_line_numbers = set()
    for ln in lines:
        if re.search(r"\bREM\s+[A-Za-z_][A-Za-z0-9_]*\b", ln):
            label_line_numbers.add(int(ln.split()[0]))

    # Every THEN/GOTO must reference a numeric target that exists and is a REM line
    for ln in lines:
        for kw in ("THEN", "GOTO"):
            for m in re.finditer(rf"\b{kw}\s+(\d+)\b", ln):
                target = int(m.group(1))
                assert target in label_line_numbers, f"{kw} targets non-label line: {target} in '{ln}'"

    # Optional: print for manual inspection when running as script
    print("\n=== BASIC Output ===\n" + basic)


