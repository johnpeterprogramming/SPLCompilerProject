#!/usr/bin/env python3
"""
Comprehensive test for all code generation features (Phases 1 & 2)
"""

from lexer import tokenize_spl
from parser import parse_spl
from semantic_analyzer import analyze_semantics
from code_generator import generate_intermediate_code

def test_comprehensive():
    """Test all features together"""
    
    print("=== Comprehensive Code Generation Test ===\n")
    
    program = """
    glob {
        result
        counter
    }
    
    proc {
        init() {
            local { temp }
            result = 0;
            counter = 0;
            temp = 1
        }
    }
    
    func {
        add(x y) {
            local { sum }
            sum = (x plus y);
            return sum
        }
        
        ispositive(n) {
            local { res }
            if (n > 0) {
                res = 1
            } else {
                res = 0
            };
            return res
        }
    }
    
    main {
        var { a b c }
        
        init();
        
        a = 10;
        b = 20;
        result = add(a b);
        
        if (result > 25) {
            print "large"
        } else {
            print "small"
        };
        
        counter = 0;
        while (counter > 3) {
            counter = (counter plus 1)
        };
        
        do {
            counter = (counter minus 1)
        } until (counter eq 0);
        
        if ((result > 20) and (counter eq 0)) {
            print result
        };
        
        halt
    }
    """
    
    print("Source Program:")
    print(program)
    print("\n" + "="*60 + "\n")
    
    try:
        # Tokenize
        print("Phase 1: Lexical Analysis...")
        tokens = tokenize_spl(program)
        print(f"  Generated {len([t for t in tokens if t.type.name != 'EOF'])} tokens")
        
        # Parse
        print("Phase 2: Parsing...")
        ast = parse_spl(tokens)
        print("  AST constructed successfully")
        
        # Semantic analysis
        print("Phase 3: Semantic Analysis...")
        symbol_table, semantic_errors = analyze_semantics(ast)
        
        if semantic_errors.has_errors():
            print("  Semantic errors found:")
            semantic_errors.print_errors()
            return
        print(f"  {len(symbol_table.symbols)} symbols in symbol table")
        
        # Code generation
        print("Phase 4: Code Generation...")
        output_file = "comprehensive_output.txt"
        generated_code = generate_intermediate_code(symbol_table, ast, output_file)
        
        print("\n" + "="*60)
        print("Generated Target Code:")
        print("="*60)
        print(generated_code)
        print("="*60)
        print(f"\nCode written to: {output_file}")
        
        # Count different constructs in generated code
        lines = generated_code.split('\n')
        if_count = sum(1 for line in lines if line.strip().startswith('IF'))
        goto_count = sum(1 for line in lines if line.strip().startswith('GOTO'))
        rem_count = sum(1 for line in lines if line.strip().startswith('REM'))
        call_count = sum(1 for line in lines if line.strip().startswith('CALL'))
        print_count = sum(1 for line in lines if line.strip().startswith('PRINT'))
        
        print("\nCode Statistics:")
        print(f"  Total lines: {len(lines)}")
        print(f"  IF statements: {if_count}")
        print(f"  GOTO statements: {goto_count}")
        print(f"  REM labels: {rem_count}")
        print(f"  CALL instructions: {call_count}")
        print(f"  PRINT statements: {print_count}")
        
        print("\nAll compilation phases completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive()

