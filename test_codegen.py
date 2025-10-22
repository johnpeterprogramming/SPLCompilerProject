#!/usr/bin/env python3
"""
Test script for code generation phase 1
"""

from lexer import tokenize_spl
from parser import parse_spl
from semantic_analyzer import analyze_semantics
from code_generator import generate_code

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
        generated_code = generate_code(symbol_table, ast, output_file)
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


