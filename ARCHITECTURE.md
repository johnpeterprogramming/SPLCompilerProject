# SPL Compiler - Modular Architecture Guide

## **COS341 Semester Project 2025**

## Overview

This document describes the modular architecture implemented for the SPL compiler, focusing on shared components that will be used across all compilation phases.

## Architecture Principles

### 1. Separation of Concerns

- Each module has a single, well-defined responsibility
- Clear interfaces between components
- Minimal coupling between modules

### 2. Reusability

- Shared types and utilities used across all phases
- Common error handling and reporting
- Standardized debugging and configuration

### 3. Maintainability

- Centralized constants and specifications
- Consistent coding patterns
- Comprehensive documentation

## Module Breakdown

### `spl_types.py` - Core Type System

**Purpose**: Central definition of all types, enums, and constants used throughout the compiler.

**Key Components**:

```python
# Token system
class TokenType(Enum)          # All SPL token types
class Token(NamedTuple)        # Immutable token representation

# Error hierarchy
class SPLError(Exception)      # Base error class
class LexerError(SPLError)     # Lexical analysis errors
class ParseError(SPLError)     # Parsing errors
class SemanticError(SPLError)  # Semantic analysis errors
class CodeGenError(SPLError)   # Code generation errors

# Language specifications
class SPLConstants             # Language rules and mappings
class SPLOperators            # Operator precedence and associativity
class SPLGrammar              # Grammar production rules
```

**Benefits**:

- Single source of truth for all types
- Consistent error handling across phases
- Easy to modify language specifications
- Type safety and IDE support

### `spl_utils.py` - Shared Utilities

**Purpose**: Common utility functions and helper classes used across all compilation phases.

**Key Components**:

```python
class TokenStream              # Token stream management for parser
class ErrorReporter            # Error collection and reporting
class DebugPrinter            # Debug output with indentation
class SPLValidator            # Language construct validation
class ConfigManager           # Compiler settings and configuration
```

**Benefits**:

- Consistent debugging across all phases
- Centralized error collection and reporting
- Reusable validation logic
- Configurable compiler behavior

### `lexer.py` - Lexical Analyzer

**Purpose**: Tokenize SPL source code into a stream of tokens.

**Integration with Shared Components**:

- Uses `TokenType` and `Token` from `spl_types.py`
- Uses `SPLConstants` for keyword mappings and patterns
- Uses `SPLValidator` for validation logic
- Uses `LexerError` for error reporting
- Uses `DebugPrinter` for debug output

**Key Features**:

- Complete SPL tokenization
- Proper error handling with line/column info
- Debug mode support
- Shared validation logic

### `parser.py` - Parser (Stub)

**Purpose**: Parse token stream into Abstract Syntax Tree (ready for full implementation).

**Integration with Shared Components**:

- Uses `TokenStream` for token management
- Uses `ParseError` for error reporting
- Uses `DebugPrinter` for debug output
- Uses `ErrorReporter` for error collection
- Ready to use `SPLOperators` for precedence parsing

**Current Status**: Stub implementation demonstrating architecture

## Usage Examples

### Basic Tokenization

```python
from lexer import tokenize_spl
from spl_types import LexerError

try:
    tokens = tokenize_spl("x = 42 plus y")
    for token in tokens:
        print(f"{token.type.name}: {token.value}")
except LexerError as e:
    print(f"Error: {e}")
```

### Debug Mode

```python
from lexer import tokenize_spl
from spl_utils import config

# Enable debug mode
config.set('debug_lexer', True)

tokens = tokenize_spl("x = 42", debug=True)
```

### Error Handling

```python
from spl_utils import ErrorReporter
from spl_types import LexerError

reporter = ErrorReporter()
try:
    # ... compilation phases ...
    pass
except LexerError as e:
    reporter.add_error(e)

if reporter.has_errors():
    reporter.print_errors()
```

### Validation

```python
from spl_utils import SPLValidator

# Validate identifiers
is_valid = SPLValidator.validate_user_defined_name("myvar123")  # True
is_valid = SPLValidator.validate_user_defined_name("while")     # False (keyword)

# Validate numbers
is_valid = SPLValidator.validate_number("42")    # True
is_valid = SPLValidator.validate_number("042")   # False (leading zero)
```

## Benefits for Team Development

### 1. Clear Responsibilities

- **Lexer Team**: Focus on tokenization using shared types
- **Parser Team**: Use `TokenStream` and shared error handling
- **AST Team**: Use shared types for node definitions
- **Semantic Team**: Use shared validation and error reporting
- **CodeGen Team**: Use shared configuration and utilities

### 2. Consistent Interfaces

- All phases use the same `Token` type
- Standardized error reporting across phases
- Common debugging infrastructure
- Shared configuration system

### 3. Easy Integration

- Well-defined module boundaries
- Clear import structure
- Minimal dependencies between phases
- Plug-and-play architecture

### 4. Testing Benefits

- Shared components can be tested independently
- Mock objects easy to create with consistent interfaces
- Integration testing simplified

## Development Guidelines

### Adding New Features

1. **Types**: Add new types to `spl_types.py`
2. **Utilities**: Add reusable functions to `spl_utils.py`
3. **Constants**: Add language specifications to `SPLConstants`
4. **Errors**: Use appropriate error types from hierarchy

### Coding Standards

1. **Imports**: Always import from shared modules first
2. **Error Handling**: Use shared error types and reporting
3. **Debugging**: Use `DebugPrinter` for consistent output
4. **Validation**: Use `SPLValidator` for language rules

### Testing

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test cross-module interactions
3. **Shared Tests**: Common test utilities in `spl_utils.py`

## Future Extensions

The modular architecture easily supports:

1. **Multiple Target Languages**: Add target-specific code generators
2. **Optimization Phases**: Add optimization utilities to `spl_utils.py`
3. **Language Extensions**: Extend `SPLConstants` and `TokenType`
4. **IDE Integration**: Use shared types for language server
5. **Debugging Tools**: Extend `DebugPrinter` for advanced debugging

## Conclusion

This modular architecture provides a solid foundation for the SPL compiler that:

- Promotes code reuse and maintainability
- Enables efficient team collaboration
- Supports future extensions and modifications
- Maintains clean separation of concerns
- Provides consistent interfaces across all phases

The abstraction of common components into shared modules ensures that the compiler is robust, maintainable, and ready for collaborative development by multiple team members.
