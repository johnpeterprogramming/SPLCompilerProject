#!/usr/bin/env python3
"""
SPL Compiler - Main Entry Point
COS341 Semester Project 2025

This is the main entry point for the SPL compiler.
Currently demonstrates the lexer functionality with modular architecture.
"""

import sys
import argparse
from lexer import tokenize_spl
from spl_types import LexerError, SemanticError, CodeGenError, TokenType
from spl_utils import format_token_list, config
from parser import parse_spl
from semantic_analyzer import analyze_semantics
from code_generator import generate_intermediate_code, generate_basic_code


def print_tokens(tokens):
    """Optional: print tokens in readable format"""
    print(f"{'Token Type':<20} {'Value':<15} {'Line':<5} {'Column':<6}")
    print("-" * 50)
    for token in tokens:
        if token.type != TokenType.EOF:
            print(f"{token.type.name:<20} {repr(token.value):<15} {token.line:<5} {token.column:<6}")
    print("-" * 50)

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_spl_file.txt> <output_basic_file.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        # Read SPL source file
        with open(input_file, 'r') as f:
            program = f.read()

        # 1️⃣ Lexical Analysis
        tokens = tokenize_spl(program)
        print("Tokens accepted.")

        # 2️⃣ Parsing
        ast = parse_spl(tokens)
        print("Syntax accepted.")

        # 3️⃣ Semantic Analysis
        symbol_table, semantic_errors = analyze_semantics(ast)
        if semantic_errors.has_errors():
            print("Semantic errors detected:")
            semantic_errors.print_errors()
            sys.exit(1)
        print("Variable naming and types accepted.")

        # 4️⃣ Code Generation
        basic_code = generate_basic_code(symbol_table, ast, output_file)
        print(f"Executable BASIC code successfully generated in: {output_file}")

    except LexerError as e:
        print(f"Lexical error: {e}")
        sys.exit(1)
    except SemanticError as e:
        print(f"Semantic error: {e}")
        sys.exit(1)
    except CodeGenError as e:
        print(f"Code generation error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()