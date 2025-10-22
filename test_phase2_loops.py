#!/usr/bin/env python3
"""
Test script for Phase 2: Loops (while, do-until)
"""

from lexer import tokenize_spl
from parser import parse_spl
from semantic_analyzer import analyze_semantics
from code_generator import generate_code

def test_while_loop():
    """Test while loop"""
    
    print("=== Test: While Loop ===\n")
    
    program = """
    glob {
        counter
        sum
    }
    
    proc {
    }
    
    func {
    }
    
    main {
        var { }
        counter = 0;
        sum = 0;
        while (counter > 5) {
            sum = (sum plus counter);
            counter = (counter plus 1)
        };
        print sum;
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
        
        output_file = "test_while.txt"
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

def test_do_until_loop():
    """Test do-until loop"""
    
    print("\n=== Test: Do-Until Loop ===\n")
    
    program = """
    glob {
        counter
    }
    
    proc {
    }
    
    func {
    }
    
    main {
        var { }
        counter = 0;
        do {
            print counter;
            counter = (counter plus 1)
        } until (counter eq 5);
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
        
        output_file = "test_do_until.txt"
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
    test_while_loop()
    test_do_until_loop()
    print("\n" + "="*60)
    print("All loop tests completed!")
    print("="*60)


