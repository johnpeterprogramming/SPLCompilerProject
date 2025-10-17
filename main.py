#!/usr/bin/env python3
"""
SPL Compiler - Main Entry Point
COS341 Semester Project 2025

This is the main entry point for the SPL compiler.
Currently demonstrates the lexer functionality with modular architecture.
"""


from lexer import tokenize_spl
from spl_types import LexerError, SemanticError, TokenType
from spl_utils import format_token_list, config
from parser import parse_spl
from semantic_analyzer import analyze_semantics


def print_tokens(tokens):
    """Print tokens in a readable format"""
    print(f"{'Token Type':<20} {'Value':<15} {'Line':<5} {'Column':<6}")
    print("-" * 50)
    for token in tokens:
        if token.type != TokenType.EOF:
            print(f"{token.type.name:<20} {repr(token.value):<15} {token.line:<5} {token.column:<6}")
    print("-" * 50)
    print(f"Total tokens: {len([t for t in tokens if t.type != TokenType.EOF])}")



def demonstrate_lexer_and_parser():
    """Demonstrate the lexer and parser with modular architecture"""
    print("=== SPL Lexer & Parser - Modular Architecture Demo ===\n")

    # Example program
    program = """
    glob {
        result
    }

    proc {
        init() {
            local { temp } temp = 0
        }
    }

    func {
        add(x y) {
            local { sum } sum = ( x plus y ); return sum
        }
    }

    main {
        var { a b }
        a = 10;
        b = 20;
        result = add(a b);
        print result;
        halt
    }
    """

    print("1. Source Code:")
    print(program)
    print("\n" + "="*60 + "\n")

    try:
        # Lexical Analysis
        print("2. Lexical Analysis (Tokenization):")
        tokens = tokenize_spl(program, debug=config.get('debug_lexer'))
        print_tokens(tokens)
        print("\n" + "="*60 + "\n")

        # Parsing
        print("3. Parsing (AST Construction):")
        ast = parse_spl(tokens)
        print_ast(ast)
        print("\n" + "="*60 + "\n")

        # Semantic Analysis
        print("4. Semantic Analysis (Name-Scope Rules):")
        symbol_table, semantic_errors = analyze_semantics(ast)
        
        if semantic_errors.has_errors():
            print("❌ Semantic Errors Found:")
            semantic_errors.print_errors()
        else:
            print("✅ No semantic errors found!")
        
        print("\nSymbol Table:")
        symbol_table.print_table()
        print("\n" + "="*60 + "\n")

        # Show modular architecture benefits
        print("5. Modular Architecture Benefits:")
        print("   ✅ Shared TokenType enum used")
        print("   ✅ Shared SPLConstants for keywords")
        print("   ✅ Shared SPLValidator for validation")
        print("   ✅ Shared error handling (LexerError, SemanticError)")
        print("   ✅ Shared debugging utilities")
        print("   ✅ Configurable debug modes")
        print("   ✅ Symbol table with node IDs")
        print("\n" + "="*60 + "\n")

        # Future phases (placeholders)
        print("6. Future Compilation Phases:")
        print("   📝 Code Generation - TODO")

        print("\n🎉 Lexer, parser, and semantic analyzer working perfectly!")

    except LexerError as e:
        print(f"❌ Lexical Error: {e}")
    except SemanticError as e:
        print(f"❌ Semantic Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()


# Simple AST pretty printer for demonstration
def print_ast(node, indent=0):
    prefix = '  ' * indent
    if node is None:
        print(prefix + 'None')
        return
    cls = node.__class__.__name__
    if hasattr(node, '__dict__'):
        print(f"{prefix}{cls}:")
        for k, v in node.__dict__.items():
            print(f"{prefix}  {k}:", end=' ')
            if isinstance(v, list):
                print()
                for item in v:
                    print_ast(item, indent+2)
            elif hasattr(v, '__dict__'):
                print()
                print_ast(v, indent+2)
            else:
                print(repr(v))
    else:
        print(f"{prefix}{repr(node)}")


def demo_lexer():
    """Demonstrate the lexer with sample SPL programs"""
    
    print("=== SPL Lexer Demo ===\n")
    
    # Example 1: Simple program structure
    print("Example 1: Basic SPL Program Structure")
    program1 = """
    glob {
        counter;
    }

    proc {
        increment() {
            local { temp };
            counter = counter plus 1;
        }
    }

    main {
        var { x };
        x = 10;
        print "Hello";
        halt;
    }
    """
    
    try:
        tokens = tokenize_spl(program1)
        print_tokens(tokens)
    except LexerError as e:
        print(f"Lexer Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Function with arithmetic
    print("Example 2: Function with Arithmetic")
    program2 = """
    func {
        calculate(a b) {
            local { result };
            result = (a plus b) mult 2;
        }; return result;
    }
    """
    
    try:
        tokens = tokenize_spl(program2)
        print_tokens(tokens)
    except LexerError as e:
        print(f"Lexer Error: {e}")


def interactive_lexer():
    """Interactive lexer for testing"""
    print("\n=== Interactive SPL Lexer ===")
    print("Enter SPL code (press Ctrl+C to exit):")
    print("Example: x = 42 plus y")
    
    while True:
        try:
            user_input = input("\nSPL> ")
            if not user_input.strip():
                continue
                
            tokens = tokenize_spl(user_input)
            print_tokens(tokens)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except LexerError as e:
            print(f"Lexer Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")



def main():
    """Main function"""
    print("SPL Compiler - Lexical & Syntax Analyzer")
    print("COS341 Semester Project 2025")
    print("-" * 40)

    # Show configuration
    print(f"Debug mode: Lexer={config.get('debug_lexer')}")
    print()

    # Run demonstration (lexer + parser)
    demonstrate_lexer_and_parser()

    # Ask if user wants more demos
    try:
        choice = input("\nRun additional lexer demo? (y/n): ").lower()
        if choice in ['y', 'yes']:
            demo_lexer()

        choice = input("\nRun interactive lexer? (y/n): ").lower()
        if choice in ['y', 'yes']:
            interactive_lexer()
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
