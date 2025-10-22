#!/usr/bin/env python3
"""
Test script for Phase 2: Boolean operators (and, or, not)
"""

from lexer import tokenize_spl
from parser import parse_spl
from semantic_analyzer import analyze_semantics
from code_generator import generate_code

def test_and_operator():
    """Test AND operator with cascading"""
    
    print("=== Test: AND Operator ===\n")
    
    program = """
    glob {
        x
        y
        result
    }
    
    proc {
    }
    
    func {
    }
    
    main {
        var { }
        x = 1;
        y = 1;
        if ((x eq 1) and (y eq 1)) {
            result = 1;
            print "bothone"
        } else {
            result = 0;
            print "notboth"
        };
        halt
    }
    """
    
    print("Source:")
    print(program)
    print("\n" + "="*60 + "\n")
    
    try:
        tokens = tokenize_spl(program)
        ast = parse_spl(tokens)
        symbol_table, semantic_errors = analyze_semantics(ast)
        
        if semantic_errors.has_errors():
            print("Semantic errors found:")
            semantic_errors.print_errors()
            return
        
        output_file = "test_and.txt"
        generated_code = generate_code(symbol_table, ast, output_file)
        
        print("Generated Target Code:")
        print("="*60)
        print(generated_code)
        print("="*60)
        print(f"\nCode written to: {output_file}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_or_operator():
    """Test OR operator with cascading"""
    
    print("\n=== Test: OR Operator ===\n")
    
    program = """
    glob {
        x
        y
        result
    }
    
    proc {
    }
    
    func {
    }
    
    main {
        var { }
        x = 1;
        y = 0;
        if ((x eq 1) or (y eq 1)) {
            result = 1;
            print "atleastone"
        } else {
            result = 0;
            print "neither"
        };
        halt
    }
    """
    
    print("Source:")
    print(program)
    print("\n" + "="*60 + "\n")
    
    try:
        tokens = tokenize_spl(program)
        ast = parse_spl(tokens)
        symbol_table, semantic_errors = analyze_semantics(ast)
        
        if semantic_errors.has_errors():
            print("Semantic errors found:")
            semantic_errors.print_errors()
            return
        
        output_file = "test_or.txt"
        generated_code = generate_code(symbol_table, ast, output_file)
        
        print("Generated Target Code:")
        print("="*60)
        print(generated_code)
        print("="*60)
        print(f"\nCode written to: {output_file}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_complex_condition():
    """Test complex nested conditions"""
    
    print("\n=== Test: Complex Nested Conditions ===\n")
    
    program = """
    glob {
        a
        b
        c
    }
    
    proc {
    }
    
    func {
    }
    
    main {
        var { }
        a = 1;
        b = 1;
        c = 0;
        if (((a eq 1) and (b eq 1)) or (c eq 1)) {
            print "true"
        } else {
            print "false"
        };
        halt
    }
    """
    
    print("Source:")
    print(program)
    print("\n" + "="*60 + "\n")
    
    try:
        tokens = tokenize_spl(program)
        ast = parse_spl(tokens)
        symbol_table, semantic_errors = analyze_semantics(ast)
        
        if semantic_errors.has_errors():
            print("Semantic errors found:")
            semantic_errors.print_errors()
            return
        
        output_file = "test_complex.txt"
        generated_code = generate_code(symbol_table, ast, output_file)
        
        print("Generated Target Code:")
        print("="*60)
        print(generated_code)
        print("="*60)
        print(f"\nCode written to: {output_file}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_and_operator()
    test_or_operator()
    test_complex_condition()
    print("\n" + "="*60)
    print("All boolean operator tests completed!")
    print("="*60)

