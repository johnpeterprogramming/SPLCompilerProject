# SPL Compiler Project - COS341 Semester Project 2025

## Overview

This is a compiler implementation for the **Students' Programming Language (SPL)**, developed as a group project for COS341. The compiler is designed to translate SPL source code into executable target code using a **modular architecture** with shared components.

## Project Structure

```text
SPLCompilerProject/
├── spl_types.py          # Shared types, enums, and constants
├── spl_utils.py          # Shared utility functions and classes
├── lexer.py              # Lexical analyzer implementation
├── parser.py             # Parser implementation (stub)
├── abstract_syntax_tree.py # AST implementation (TODO)
├── main.py               # Main compiler entry point
├── example.spl           # Example SPL program for testing
├── tests/
│   ├── test_lexer.py     # Comprehensive lexer tests
│   └── test_parser.py    # Parser tests (TODO)
└── README.md             # This file
```

## Modular Architecture

The compiler uses a **modular design** with shared components across all phases:

### Core Modules

#### `spl_types.py` - Shared Types and Constants

- **TokenType enum**: All SPL token types
- **Token class**: Immutable token representation
- **Error hierarchy**: LexerError, ParseError, SemanticError, CodeGenError
- **SPLConstants**: Language specifications and mappings
- **SPLOperators**: Operator precedence and associativity
- **SPLGrammar**: Grammar production rules reference

#### `spl_utils.py` - Shared Utilities

- **TokenStream**: Token stream management for parser
- **ErrorReporter**: Error collection and reporting
- **DebugPrinter**: Debug output with indentation
- **SPLValidator**: Validation utilities for language constructs
- **ConfigManager**: Compiler configuration management

#### `lexer.py` - Lexical Analyzer

- **SPLLexer**: Main lexer class using shared types
- **tokenize_spl()**: Convenience function for tokenization
- Integrated with shared validation and error handling

#### `parser.py` - Parser (Stub)

- **SPLParser**: Parser class using TokenStream
- **parse_spl()**: Convenience function for parsing
- Ready for full implementation using shared utilities

## Current Implementation Status

### ✅ Completed

- **Modular Architecture**: Shared types and utilities across phases
- **Token System**: Complete token representation with enhanced features
- **Token Types & Keywords**: All SPL keywords and operators defined
- **Lexer Implementation**: Full lexical analyzer with error handling
- **Lexer Tests**: Comprehensive test suite (23 test cases, all passing)
- **Parser Stub**: Basic parser structure using shared components
- **Configuration System**: Debug modes and compiler settings

### 🚧 In Progress

- Full parser implementation
- Abstract Syntax Tree (AST) implementation
- Semantic analysis
- Code generation

## SPL Language Features

### Keywords

- **Program structure**: `glob`, `proc`, `func`, `main`
- **Variables**: `var`, `local`
- **Control flow**: `if`, `else`, `while`, `do`, `until`
- **Operations**: `halt`, `print`, `return`
- **Operators**: `neg`, `not`, `eq`, `or`, `and`, `plus`, `minus`, `mult`, `div`

### Data Types

- **Numbers**: Integers following pattern `(0 | [1-9][0-9]*)`
- **Strings**: Alphanumeric sequences (max 15 chars) in quotes
- **User-defined names**: Following pattern `[a-z][a-z]*[0-9]*`

### Program Structure

```spl
glob {
    // Global variables
}

proc {
    // Procedure definitions (no return value)
}

func {
    // Function definitions (return a value)
}

main {
    // Main program
}
```

## Lexer Implementation

### Features

- **Complete tokenization** of SPL source code
- **Error handling** with line and column reporting
- **Comment support** (`//` single-line comments)
- **Whitespace handling** (spaces, tabs, newlines)
- **String validation** (alphanumeric only, max 15 chars)
- **Number validation** (no leading zeros except for `0`)
- **Identifier validation** (lowercase letters + optional digits)

### Token Types

The lexer recognizes the following token types:

- Keywords (24 types)
- Operators (10 types)
- Delimiters (7 types)
- Literals (numbers, strings, identifiers)
- Special tokens (EOF, whitespace, comments)

### Usage Example

```python
from lexer import tokenize_spl, LexerError

# Tokenize SPL code
try:
    source = """
    main {
        var { x }
        x = 42;
        print "Hello"
    }
    """
    tokens = tokenize_spl(source)
    for token in tokens:
        print(f"{token.type.name}: {token.value}")
except LexerError as e:
    print(f"Error: {e}")
```

## Testing

### Running Tests

```bash
# Run lexer tests
python3 tests/test_lexer.py

# Run all tests (when parser tests are added)
python3 -m unittest discover tests/
```

### Test Coverage

The lexer test suite includes:

- ✅ Token type recognition (keywords, operators, delimiters)
- ✅ Number parsing (valid/invalid formats)
- ✅ String parsing (valid/invalid formats)
- ✅ Identifier recognition
- ✅ Whitespace and comment handling
- ✅ Complex program tokenization
- ✅ Error handling and reporting
- ✅ Edge cases and boundary conditions

**Test Results**: 23/23 tests passing

## Grammar Specification

### SPL Context-Free Grammar

```text
SPL_PROG ::= glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }

VARIABLES ::= ε | VAR VARIABLES
VAR ::= user-defined-name
NAME ::= user-defined-name

PROCDEFS ::= ε | PDEF PROCDEFS
PDEF ::= NAME ( PARAM ) { BODY }

FUNCDEFS ::= FDEF FUNCDEFS | ε
FDEF ::= NAME ( PARAM ) { BODY ; return ATOM }

BODY ::= local { MAXTHREE } ALGO
PARAM ::= MAXTHREE
MAXTHREE ::= ε | VAR | VAR VAR | VAR VAR VAR

MAINPROG ::= var { VARIABLES } ALGO

ATOM ::= VAR | number
ALGO ::= INSTR | INSTR ; ALGO

INSTR ::= halt | print OUTPUT | NAME ( INPUT ) | ASSIGN | LOOP | BRANCH
ASSIGN ::= VAR = NAME ( INPUT ) | VAR = TERM
LOOP ::= while TERM { ALGO } | do { ALGO } until TERM
BRANCH ::= if TERM { ALGO } | if TERM { ALGO } else { ALGO }

OUTPUT ::= ATOM | string
INPUT ::= ε | ATOM | ATOM ATOM | ATOM ATOM ATOM

TERM ::= ATOM | ( UNOP TERM ) | ( TERM BINOP TERM )
UNOP ::= neg | not
BINOP ::= eq | > | or | and | plus | minus | mult | div
```

### Vocabulary Rules

1. User-defined names cannot be keywords
2. User-defined names: `[a-z][a-z]*[0-9]*`
3. Numbers: `(0 | [1-9][0-9]*)`
4. Strings: alphanumeric sequences (max 15 chars) in quotes

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Include comprehensive docstrings
- Write unit tests for all new features

### Git Workflow

1. Create feature branches for new components
2. Write tests before implementation (TDD)
3. Ensure all tests pass before merging
4. Use descriptive commit messages

### Team Responsibilities

- **Lexer**: ✅ Complete (Token class, types, implementation, tests)
- **Parser**: 🚧 In progress
- **AST**: 🚧 Planned
- **Code Generation**: 🚧 Planned

## Example Programs

### Simple Program

```spl
glob {
    counter
}

main {
    var { x }
    counter = 0;
    x = 42;
    print "Done";
    halt
}
```

### Function Example

```spl
func {
    add(a b) {
        local { result }
        result = a plus b;
        return result
    }
}

main {
    var { sum }
    sum = add(10 20);
    print sum
}
```

### Control Structures

```spl
main {
    var { x }
    x = 10;
    
    while (x > 0) {
        print x;
        x = x minus 1
    };
    
    if (x eq 0) {
        print "Done"
    }
}
```

## Resources

- **Project Specification**: COS341 Semester Project 2025 Worksheet
- **Grammar Reference**: SPL Context-Free Grammar (provided above)
- **Python Documentation**: [docs.python.org](https://docs.python.org/)
- **Testing Framework**: Python unittest module

## Team Information

**Course**: COS341 - Compiler Construction  
**Project**: SPL Compiler Implementation  
**Current Phase**: Compiler Frontend

---

**Last Updated**: September 2, 2025  
**Version**: 1.0 (Lexer Complete)
