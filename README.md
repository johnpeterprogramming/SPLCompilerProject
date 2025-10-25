# SPL Compiler Project - COS341 Semester Project 2025

## Overview

This is a compiler implementation for the **Students' Programming Language (SPL)**, developed as a group project for COS341. The compiler is designed to translate SPL source code into executable target code using a **modular architecture** with shared components.

The project implements Project Type A, meaning it supports:
- Lexical analysis
- Parsing and AST construction
- Semantic analysis (name scoping, type checking)
- Executable BASIC code generation


## Command-line Usage
python main.py <input_spl_file.spl> <output_basic_file.txt>

Example:
python main.py input.spl out.txt

Input: SPL source file (.spl)
Output: Generated executable BASIC code (.txt)

If any errors occur during lexing, parsing, or semantic analysis, the compiler prints a descriptive message and exits.


## Project Structure

```text
SPLCompilerProject/
├── spl_types.py          # Shared types, enums, constants, and error classes
├── spl_utils.py          # Utility functions, error reporting, and configuration
├── lexer.py              # Lexical analyzer implementation
├── parser.py             # Parser implementation (constructs AST)
├── semantic_analyzer.py  # Semantic checks (name scoping, type checking)
├── code_generator.py     # Code generation (intermediate & BASIC)
├── main.py               # Main compiler entry point (CLI)
├── input.spl             # Example SPL program for testing
├── out.txt               # Generated executable BASIC code (output)
├── tests/
│   ├── test_lexer.py     # Lexer unit tests
│   └── test_parser.py    # Parser unit tests
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

#### `parser.py` - Parser

- **SPLParser**: Parser class using TokenStream
- **parse_spl()**: Convenience function for parsing
- Detects syntax errors and provides descriptive messages with line/column info.
- Builds an Abstract Syntax Tree (AST) representing program structure, including blocks, expressions, and statements.

#### `semantic_analyzer.py` - Semantic Analysis
-
-
-
-

#### `code_generator.py` - Code Generation
-
-
-
-



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


### Token Types

The lexer recognizes the following token types:

- Keywords (24 types)
- Operators (10 types)
- Delimiters (7 types)
- Literals (numbers, strings, identifiers)
- Special tokens (EOF, whitespace, comments)


## Testing

### Running Tests

```bash
# Run all tests
python3 -m pytest -q
```


## Parser Implementation
- Builds an AST for the entire SPL program.
- Detects syntax errors, such as unmatched brackets, missing semicolons, or invalid expressions.
- Prepares the AST for semantic analysis and code generation.

## Testing

### Running Tests

```bash
# Run all tests
py -m pytest tests/test_parser.py -v
```

## Semantic Analysis





## Code Generation








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

- Indentation: Use 4 spaces per indentation level | 1 Tab
- Include comprehensive docstrings
- Write unit tests for all new features
- Functions/variables: snake_case (e.g., my_function, token_type)
- Classes: PascalCase (e.g., SPLLexer, TokenType)
- Constants: UPPER_CASE (e.g., MAX_STRING_LENGTH)
- Private methods: Start with underscore (e.g., _parse_token)

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

---
